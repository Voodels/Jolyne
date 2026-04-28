"""
pdfparser.py
------------
Resume parser for the AI Recruitment Hackathon.
Handles messy PDFs and plain text/CSV dumps.
Extracts structured data via Groq LLM and optionally
embeds results into ChromaDB for semantic search.

Requirements:
    pip install pdfplumber langchain-groq chromadb sentence-transformers

Usage:
    from pdfparser import parse_resume, batch_parse, search_candidates

    # Single file
    result = parse_resume("resume.pdf")

    # Batch process a folder
    batch_parse("./resumes", save_to_json=True)

    # Semantic search (after batch_parse has run)
    results = search_candidates("Java developer with banking experience", top_k=5)
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import pdfplumber
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# ── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pdfparser.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")          # set in environment
GROQ_MODEL   = "llama-3.3-70b-versatile"
MAX_TEXT_CHARS = 6000                                  # cap sent to LLM (~1500 tokens)
RATE_LIMIT_EVERY = 25                                  # pause every N requests
RATE_LIMIT_SLEEP = 62                                  # seconds (Groq free = ~30 req/min)
CHROMA_PERSIST_DIR = "./chroma_db"                     # local ChromaDB storage
CHROMA_COLLECTION  = "candidates"

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv"}

# ── LLM setup ────────────────────────────────────────────────────────────────

def _build_llm() -> ChatGroq:
    """Build the Groq LLM client. Raises clearly if API key is missing."""
    if not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Export it with: export GROQ_API_KEY=your_key_here"
        )
    return ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0)


PARSE_PROMPT = ChatPromptTemplate.from_template(
    """You are a resume data extractor. The text below may be a messy PDF,
plain text, or CSV dump. It may lack a name, have data in unusual positions,
or contain garbage characters. Extract whatever is available. 
NEVER invent or assume data — use null for anything not found.

Return ONLY a raw JSON object with no markdown, no code fences, no explanation.

{{
  "name": "full name or null",
  "email": "email address or null",
  "phone": "phone number as string or null",
  "skills": ["list of technical skills, tools, languages, frameworks"],
  "years_experience": <integer or null>,
  "education": "highest qualification found or null",
  "previous_roles": ["job titles found, most recent first"],
  "current_or_last_company": "company name or null",
  "domain": "industry domain e.g. Banking, IT, Healthcare, Retail or null",
  "summary": "2 sentence candidate summary based ONLY on what is present in the text"
}}

Resume text:
{text}"""
)

# ── Text extraction ───────────────────────────────────────────────────────────

def _extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract raw text from a PDF using pdfplumber.
    Returns empty string if file is unreadable — never raises.
    """
    try:
        with pdfplumber.open(str(file_path)) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n".join(pages_text).strip()
    except Exception as e:
        log.warning(f"pdfplumber failed on {file_path.name}: {e}")
        return ""


def _extract_text_from_plaintext(file_path: Path) -> str:
    """Read .txt or .csv files safely, trying utf-8 then latin-1 fallback."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return file_path.read_text(encoding=encoding).strip()
        except (UnicodeDecodeError, LookupError):
            continue
    log.warning(f"Could not decode {file_path.name} with any known encoding.")
    return ""


def extract_raw_text(file_path: str) -> str:
    """
    Entry point for text extraction.
    Dispatches to the right extractor based on file extension.

    Returns:
        Raw text string (may be empty if file is unreadable).
    """
    path = Path(file_path)

    if not path.exists():
        log.error(f"File not found: {file_path}")
        return ""

    if not path.is_file():
        log.error(f"Path is not a file: {file_path}")
        return ""

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_text_from_pdf(path)

    if suffix in (".txt", ".csv"):
        return _extract_text_from_plaintext(path)

    log.warning(f"Unsupported file type '{suffix}' for {path.name}. Skipping.")
    return ""


# ── LLM parsing ──────────────────────────────────────────────────────────────

def _safe_json_parse(raw: str) -> Optional[dict]:
    """
    Parse LLM output as JSON.
    Handles cases where the model adds markdown code fences despite instructions.
    Returns None if parsing fails completely.
    """
    text = raw.strip()

    # Strip ```json ... ``` or ``` ... ``` fences if present
    if text.startswith("```"):
        lines = text.splitlines()
        # Remove first line (```json or ```) and last line (```)
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        log.warning(f"JSON parse failed: {e}. Raw output snippet: {text[:200]}")
        return None


def parse_resume(file_path: str, llm: Optional[ChatGroq] = None) -> dict:
    """
    Parse a single resume file into structured JSON.

    Args:
        file_path: Path to .pdf, .txt, or .csv file.
        llm:       Optional pre-built ChatGroq instance (reuse across batch calls).

    Returns:
        dict with parsed fields, or a dict with an "error" key on failure.
        Always includes "source_file" for traceability.
    """
    path = Path(file_path)
    base_result = {"source_file": path.name}

    # ── Step 1: extract raw text ──────────────────────────────────────────
    raw_text = extract_raw_text(file_path)

    if not raw_text:
        log.warning(f"No text extracted from {path.name}")
        return {**base_result, "error": "empty_or_unreadable"}

    # ── Step 2: cap text length before sending to LLM ────────────────────
    truncated = raw_text[:MAX_TEXT_CHARS]
    if len(raw_text) > MAX_TEXT_CHARS:
        log.debug(f"{path.name}: text truncated from {len(raw_text)} to {MAX_TEXT_CHARS} chars")

    # ── Step 3: call LLM ──────────────────────────────────────────────────
    try:
        _llm = llm or _build_llm()
        chain = PARSE_PROMPT | _llm
        response = chain.invoke({"text": truncated})
    except Exception as e:
        log.error(f"LLM call failed for {path.name}: {e}")
        return {**base_result, "error": f"llm_error: {str(e)}"}

    # ── Step 4: parse JSON response ───────────────────────────────────────
    parsed = _safe_json_parse(response.content)

    if parsed is None:
        log.error(f"Could not parse LLM output for {path.name}")
        return {**base_result, "error": "json_parse_failed", "raw_output": response.content[:500]}

    parsed["source_file"] = path.name
    log.info(f"Parsed: {path.name} → name={parsed.get('name')}, skills={len(parsed.get('skills', []))}")
    return parsed


# ── ChromaDB embedding ────────────────────────────────────────────────────────

def _get_chroma_collection():
    """
    Lazily initialise ChromaDB with a persistent local store.
    Returns the collection object.
    """
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # ~80MB, CPU-friendly
        )
        collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            embedding_function=embedding_fn,
        )
        return collection
    except ImportError:
        raise ImportError(
            "ChromaDB or sentence-transformers not installed.\n"
            "Run: pip install chromadb sentence-transformers"
        )


def embed_candidate(parsed: dict, candidate_id: Optional[str] = None) -> bool:
    """
    Embed a parsed candidate into ChromaDB for semantic search.

    Args:
        parsed:       Output dict from parse_resume().
        candidate_id: Optional stable ID (e.g. DB primary key). 
                      Falls back to source_file name.

    Returns:
        True on success, False on failure.
    """
    if "error" in parsed:
        log.debug(f"Skipping embed for errored record: {parsed.get('source_file')}")
        return False

    try:
        collection = _get_chroma_collection()

        # Build a rich text document for embedding
        skills_str  = ", ".join(parsed.get("skills", [])) or "unknown"
        roles_str   = ", ".join(parsed.get("previous_roles", [])) or "unknown"
        doc_text = (
            f"{parsed.get('summary', '')} "
            f"Skills: {skills_str}. "
            f"Roles: {roles_str}. "
            f"Domain: {parsed.get('domain', '')}. "
            f"Experience: {parsed.get('years_experience', '')} years."
        ).strip()

        uid = candidate_id or parsed.get("source_file", str(time.time_ns()))

        # Metadata stored alongside vector (filterable in Chroma)
        metadata = {
            "name":             str(parsed.get("name") or ""),
            "email":            str(parsed.get("email") or ""),
            "domain":           str(parsed.get("domain") or ""),
            "years_experience": str(parsed.get("years_experience") or ""),
            "source_file":      str(parsed.get("source_file") or ""),
        }

        collection.upsert(
            ids=[uid],
            documents=[doc_text],
            metadatas=[metadata],
        )
        log.debug(f"Embedded candidate: {uid}")
        return True

    except Exception as e:
        log.error(f"ChromaDB embed failed for {parsed.get('source_file')}: {e}")
        return False


def search_candidates(query: str, top_k: int = 5) -> list[dict]:
    """
    Semantic search over embedded candidates.

    Args:
        query: Natural language query e.g. "Java developer with banking experience"
        top_k: Number of results to return.

    Returns:
        List of dicts with candidate metadata and similarity distance.
    """
    try:
        collection = _get_chroma_collection()
        results = collection.query(query_texts=[query], n_results=top_k)

        candidates = []
        for i, meta in enumerate(results["metadatas"][0]):
            candidates.append({
                **meta,
                "match_score": round(1 - results["distances"][0][i], 3),  # 0–1, higher = better
                "summary_snippet": results["documents"][0][i][:200],
            })

        log.info(f"Search '{query}' → {len(candidates)} results")
        return candidates

    except Exception as e:
        log.error(f"ChromaDB search failed: {e}")
        return []


# ── Batch processing ──────────────────────────────────────────────────────────

def batch_parse(
    folder: str,
    save_to_json: bool = True,
    embed_to_chroma: bool = True,
    output_file: str = "parsed_candidates.jsonl",
) -> list[dict]:
    """
    Batch parse all supported resume files in a folder (recursive).

    Args:
        folder:          Path to folder containing resume files.
        save_to_json:    Write each parsed result to a .jsonl file (append mode).
        embed_to_chroma: Also embed each parsed candidate into ChromaDB.
        output_file:     Path for the .jsonl output file.

    Returns:
        List of all parsed candidate dicts.
    """
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        log.error(f"Folder not found: {folder}")
        return []

    # Gather all supported files
    files = [
        f for ext in SUPPORTED_EXTENSIONS
        for f in root.rglob(f"*{ext}")
        if f.is_file()
    ]

    if not files:
        log.warning(f"No supported files found in {folder}")
        return []

    log.info(f"Found {len(files)} files to process in '{folder}'")

    # Build LLM once — reuse across all calls to avoid repeated init
    try:
        llm = _build_llm()
    except EnvironmentError as e:
        log.error(str(e))
        return []

    results = []
    failed  = 0

    for i, file_path in enumerate(files, start=1):
        log.info(f"[{i}/{len(files)}] Processing: {file_path.name}")

        parsed = parse_resume(str(file_path), llm=llm)
        results.append(parsed)

        if "error" in parsed:
            failed += 1
        else:
            if embed_to_chroma:
                embed_candidate(parsed)

        # Save incrementally so progress isn't lost on crash
        if save_to_json:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(parsed, ensure_ascii=False) + "\n")

        # Rate limiting: Groq free tier ~30 req/min
        if i % RATE_LIMIT_EVERY == 0:
            log.info(f"Rate limit pause — {RATE_LIMIT_SLEEP}s ({i}/{len(files)} done, {failed} failed so far)")
            time.sleep(RATE_LIMIT_SLEEP)

    log.info(
        f"Batch complete. Total: {len(files)}, "
        f"Success: {len(files) - failed}, Failed: {failed}"
    )
    return results


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    if not args:
        print(
            "Usage:\n"
            "  python pdfparser.py <file.pdf>           — parse a single file\n"
            "  python pdfparser.py --batch <folder>     — batch parse a folder\n"
            "  python pdfparser.py --search <query>     — semantic search\n"
        )
        sys.exit(0)

    if args[0] == "--batch" and len(args) >= 2:
        batch_parse(args[1])

    elif args[0] == "--search" and len(args) >= 2:
        query = " ".join(args[1:])
        hits  = search_candidates(query, top_k=5)
        for hit in hits:
            print(json.dumps(hit, indent=2))

    else:
        # Single file parse
        result = parse_resume(args[0])
        print(json.dumps(result, indent=2, ensure_ascii=False))