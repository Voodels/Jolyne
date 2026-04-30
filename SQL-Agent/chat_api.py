import json
import os
import uuid
from functools import lru_cache
from dataclasses import dataclass
from typing import Any, Callable, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from langchain_setup import (
    build_schema_snapshot,
    build_system_prompt,
    init_model,
    init_sql_tools,
    load_settings,
    setup_google_env,
    setup_groq_env,
    setup_langsmith_env,
    validate_settings,
)
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import ToolMessage


@dataclass
class Runtime:
    model: Any
    db: Any
    tools: list
    agent: Any
    engine: Any
    run_query: Callable[[str], Any]
    settings: Any
    schema_snapshot: Optional[str] = None


class StartResponse(BaseModel):
    session_id: str


class ChatMessageIn(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(min_length=1)


class PendingActionOut(BaseModel):
    id: str
    tool_name: str
    tool_args: dict
    description: Optional[str] = None


class ChatMessageOut(BaseModel):
    session_id: str
    thinking_preview: Optional[str] = None
    pending_action: Optional[PendingActionOut] = None
    assistant_message: Optional[str] = None


class ApproveIn(BaseModel):
    action_id: str
    decision: str


class HistoryMessage(BaseModel):
    role: str
    content: str
    created_at: str


class HistoryOut(BaseModel):
    session_id: str
    messages: list[HistoryMessage]


class RefreshSchemaOut(BaseModel):
    schema_cached: bool
    table_count: int


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RUNTIME: Optional[Runtime] = None


def create_schema(engine) -> None:
    print("[DEBUG] Initializing database schema...")
    statements = [
        """
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id UUID PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY,
            session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS pending_actions (
            id UUID PRIMARY KEY,
            session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            tool_name TEXT NOT NULL,
            tool_args JSONB NOT NULL,
            user_text TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """,
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_session(engine, session_id: Optional[str]) -> str:
    if session_id:
        with engine.begin() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM chat_sessions WHERE id = :id"),
                {"id": session_id},
            ).fetchone()
        if exists:
            print(f"[DEBUG] Found existing session: {session_id}")
            return session_id

    new_session = str(uuid.uuid4())
    print(f"[DEBUG] Creating new session: {new_session}")
    with engine.begin() as connection:
        connection.execute(
            text("INSERT INTO chat_sessions (id) VALUES (:id)"),
            {"id": new_session},
        )
    return new_session


def save_message(engine, session_id: str, role: str, content: str) -> None:
    print(f"[DEBUG] Saving {role} message to session {session_id}")
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO chat_messages (id, session_id, role, content)
                VALUES (:id, :session_id, :role, :content)
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "role": role,
                "content": content,
            },
        )


def save_pending_action(
    engine,
    session_id: str,
    tool_name: str,
    tool_args: dict,
    user_text: str,
) -> str:
    action_id = str(uuid.uuid4())
    print(f"[DEBUG] Saving pending action {action_id} for tool {tool_name}")
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO pending_actions (id, session_id, tool_name, tool_args, user_text)
                VALUES (:id, :session_id, :tool_name, CAST(:tool_args AS jsonb), :user_text)
                """
            ),
            {
                "id": action_id,
                "session_id": session_id,
                "tool_name": tool_name,
                "tool_args": json.dumps(tool_args),
                "user_text": user_text,
            },
        )
    return action_id


def get_pending_action(engine, action_id: str) -> dict:
    with engine.begin() as connection:
        row = connection.execute(
            text(
                """
                SELECT id, session_id, tool_name, tool_args, user_text, status
                FROM pending_actions
                WHERE id = :id
                """
            ),
            {"id": action_id},
        ).fetchone()

    if not row:
        print(f"[DEBUG] Pending action {action_id} not found in DB!")
        raise HTTPException(status_code=404, detail="Pending action not found")

    tool_args = row.tool_args
    if isinstance(tool_args, str):
        tool_args = json.loads(tool_args)

    return {
        "id": row.id,
        "session_id": row.session_id,
        "tool_name": row.tool_name,
        "tool_args": tool_args,
        "user_text": row.user_text,
        "status": row.status,
    }


def update_pending_status(engine, action_id: str, status: str) -> None:
    print(f"[DEBUG] Updating pending action {action_id} status to: {status}")
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE pending_actions SET status = :status WHERE id = :id"),
            {"status": status, "id": action_id},
        )


def build_reflection_prompt(user_text: str) -> str:
    return (
        "Provide a short processing note (max 140 characters). "
        "Keep it high-level and neutral, do not include hidden reasoning steps. "
        f"User question: {user_text}"
    )


def is_read_only_sql(query: str) -> bool:
    if not query: return False
    stripped = query.strip().lstrip("(").strip()
    prefix = stripped[:10].lower()
    is_safe = prefix.startswith("select") or prefix.startswith("with")
    print(f"[DEBUG] SQL Read-Only Check: {is_safe} for query: {query[:50]}...")
    return is_safe


def init_agent_runtime() -> Runtime:
    print("[DEBUG] Initializing Agent Runtime...")
    if load_dotenv:
        load_dotenv()

    settings = load_settings()
    validate_settings(settings)
    setup_langsmith_env(settings)
    setup_google_env(settings)
    setup_groq_env(settings)

    model = init_model(settings)
    db, tools = init_sql_tools(settings.database_url, model)
    schema_snapshot = None
    if settings.schema_cache:
        schema_snapshot = build_schema_snapshot(db, settings.schema_cache_table_limit)
        print("[DEBUG] Schema snapshot generated and cached.")

    system_prompt = build_system_prompt(db.dialect, top_k=5, schema_snapshot=schema_snapshot)
    
    print("[DEBUG] Compiling LangGraph ReAct agent...")
    agent = create_react_agent(
        model,
        tools,
        prompt=system_prompt,
        checkpointer=InMemorySaver(),
        interrupt_before=["tools"], # Instruct LangGraph to pause before executing ANY tool
    )

    engine = create_engine(settings.database_url)
    create_schema(engine)

    if settings.sql_query_cache_size > 0:
        print(f"[DEBUG] Query caching enabled (size: {settings.sql_query_cache_size})")
        @lru_cache(maxsize=settings.sql_query_cache_size)
        def cached_run(query: str) -> Any:
            return db.run(query)

        run_query = cached_run
    else:
        run_query = db.run

    return Runtime(
        model=model,
        db=db,
        tools=tools,
        agent=agent,
        engine=engine,
        run_query=run_query,
        settings=settings,
        schema_snapshot=schema_snapshot,
    )


def refresh_schema(runtime: Runtime) -> None:
    print("[DEBUG] Refreshing schema manually...")
    schema_snapshot = None
    if runtime.settings.schema_cache:
        schema_snapshot = build_schema_snapshot(
            runtime.db,
            runtime.settings.schema_cache_table_limit,
        )

    system_prompt = build_system_prompt(
        runtime.db.dialect,
        top_k=5,
        schema_snapshot=schema_snapshot,
    )
    
    runtime.agent = create_react_agent(
        runtime.model,
        runtime.tools,
        prompt=system_prompt,
        checkpointer=InMemorySaver(),
        interrupt_before=["tools"],
    )
    runtime.schema_snapshot = schema_snapshot


@app.on_event("startup")
def startup() -> None:
    global RUNTIME
    print("[DEBUG] [chat-api] Starting up server...")
    RUNTIME = init_agent_runtime()
    print("[DEBUG] [chat-api] Server runtime ready.")


@app.post("/chat/start", response_model=StartResponse)
def start_chat() -> StartResponse:
    if not RUNTIME:
        raise HTTPException(status_code=500, detail="Runtime not initialized")
    session_id = ensure_session(RUNTIME.engine, None)
    return StartResponse(session_id=session_id)


@app.post("/chat/refresh-schema", response_model=RefreshSchemaOut)
def refresh_schema_endpoint() -> RefreshSchemaOut:
    if not RUNTIME:
        raise HTTPException(status_code=500, detail="Runtime not initialized")

    refresh_schema(RUNTIME)
    table_count = len(RUNTIME.db.get_usable_table_names())
    return RefreshSchemaOut(
        schema_cached=bool(RUNTIME.schema_snapshot),
        table_count=table_count,
    )


@app.post("/chat/message", response_model=ChatMessageOut)
def send_message(payload: ChatMessageIn) -> ChatMessageOut:
    if not RUNTIME:
        raise HTTPException(status_code=500, detail="Runtime not initialized")

    session_id = ensure_session(RUNTIME.engine, payload.session_id)
    print(f"[DEBUG] Incoming user message for session: {session_id}")
    save_message(RUNTIME.engine, session_id, "user", payload.message)

    thinking_preview = None
    if RUNTIME.settings.enable_thinking_preview:
        print("[DEBUG] Generating thinking preview...")
        reflection_prompt = build_reflection_prompt(payload.message)
        reflection = RUNTIME.model.invoke([{"role": "user", "content": reflection_prompt}])
        thinking_preview = getattr(reflection, "content", "")

    config = {"configurable": {"thread_id": session_id}}
    pending_action = None
    assistant_message = None

    # We use input_data for the first iteration, and None for resuming if we auto-approve a safe tool
    input_data = {"messages": [{"role": "user", "content": payload.message}]}

    while True:
        print("[DEBUG] Entering LangGraph stream loop...")
        for step in RUNTIME.agent.stream(input_data, config, stream_mode="values"):
            if "messages" in step:
                msg = step["messages"][-1]
                print(f"[DEBUG] Graph emitted message: {msg.type} - {str(msg.content)[:100]}")

        # Clear input_data so subsequent loops resume the graph properly
        input_data = None
        
        # Check the state of the graph to see if it is paused
        state = RUNTIME.agent.get_state(config)
        
        if not state.next:
            print("[DEBUG] Graph execution finished naturally.")
            if state.values.get("messages"):
                assistant_message = state.values["messages"][-1].content
            break

        if state.next[0] == "tools":
            last_message = state.values["messages"][-1]
            if not last_message.tool_calls:
                break
            
            tool_call = last_message.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            print(f"[DEBUG] Graph interrupted before tool: {tool_name}")
            print(f"[DEBUG] Tool args: {tool_args}")

            # Safe tools or Read-only SQL queries are auto-approved to keep conversation fluid
            if tool_name != "sql_db_query" or is_read_only_sql(tool_args.get("query", "")):
                print(f"[DEBUG] Auto-approving safe tool: {tool_name}")
                continue # Loops back and resumes the graph automatically

            # Destructive SQL requires manual approval
            print(f"[DEBUG] HALTING: Destructive or complex SQL detected. User approval required.")
            pending_action = {
                "tool_name": tool_name,
                "tool_args": tool_args,
                "description": f"Pending approval for {tool_name}",
            }
            break

    if pending_action:
        action_id = save_pending_action(
            RUNTIME.engine,
            session_id,
            pending_action["tool_name"],
            pending_action["tool_args"],
            payload.message,
        )
        return ChatMessageOut(
            session_id=session_id,
            thinking_preview=thinking_preview,
            pending_action=PendingActionOut(
                id=action_id,
                tool_name=pending_action["tool_name"],
                tool_args=pending_action["tool_args"],
                description=pending_action.get("description"),
            ),
        )

    if assistant_message:
        save_message(RUNTIME.engine, session_id, "assistant", assistant_message)

    return ChatMessageOut(
        session_id=session_id,
        thinking_preview=thinking_preview,
        assistant_message=assistant_message,
    )


@app.post("/chat/approve", response_model=ChatMessageOut)
def approve_action(payload: ApproveIn) -> ChatMessageOut:
    if not RUNTIME:
        raise HTTPException(status_code=500, detail="Runtime not initialized")

    action = get_pending_action(RUNTIME.engine, payload.action_id)
    print(f"[DEBUG] Processing approval for action {payload.action_id}. Decision: {payload.decision}")
    
    if action["status"] != "pending":
        print("[DEBUG] Error: Action was already processed.")
        raise HTTPException(status_code=400, detail="Action already processed")

    decision = payload.decision.lower().strip()
    if decision not in {"approve", "deny"}:
        raise HTTPException(status_code=400, detail="Decision must be approve or deny")

    config = {"configurable": {"thread_id": str(action["session_id"])}}

    if decision == "deny":
        print("[DEBUG] User denied the tool execution.")
        update_pending_status(RUNTIME.engine, action["id"], "denied")
        
        # Inject a denial message directly into the graph state so the LLM knows it was rejected
        state = RUNTIME.agent.get_state(config)
        last_message = state.values["messages"][-1]
        tool_call_id = last_message.tool_calls[0]["id"]
        
        print(f"[DEBUG] Updating LangGraph state with ToolMessage rejection for {tool_call_id}")
        RUNTIME.agent.update_state(
            config,
            {"messages": [ToolMessage(tool_call_id=tool_call_id, content="User denied the request.", name=action["tool_name"])]},
            as_node="tools" # Apply this update exactly where it is paused
        )
        
        # Resume the graph to let the LLM react to the denial
        final_message = "Request denied."
        for step in RUNTIME.agent.stream(None, config, stream_mode="values"):
            if "messages" in step:
                final_message = step["messages"][-1].content
                
        save_message(RUNTIME.engine, action["session_id"], "assistant", final_message)
        return ChatMessageOut(
            session_id=action["session_id"],
            assistant_message=final_message,
        )

    # If Approved
    print("[DEBUG] User approved the tool execution. Resuming LangGraph...")
    try:
        final_message = ""
        # Passing None as input to stream() resumes execution from the breakpoint
        for step in RUNTIME.agent.stream(None, config, stream_mode="values"):
            if "messages" in step:
                final_message = step["messages"][-1].content
                print(f"[DEBUG] Graph post-execution message: {str(final_message)[:100]}")
                
        update_pending_status(RUNTIME.engine, action["id"], "approved")
        save_message(RUNTIME.engine, action["session_id"], "assistant", final_message)
        
        return ChatMessageOut(
            session_id=str(action["session_id"]),
            assistant_message=final_message,
        )
        
    except Exception as exc:
        print(f"[DEBUG] Fatal error during tool execution: {exc}")
        update_pending_status(RUNTIME.engine, action["id"], "error")
        raise HTTPException(status_code=500, detail=f"SQL execution failed: {exc}") from exc


@app.get("/chat/history/{session_id}", response_model=HistoryOut)
def get_history(session_id: str) -> HistoryOut:
    print(f"[DEBUG] Fetching history for session {session_id}")
    if not RUNTIME:
        raise HTTPException(status_code=500, detail="Runtime not initialized")

    with RUNTIME.engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT role, content, created_at
                FROM chat_messages
                WHERE session_id = :session_id
                ORDER BY created_at
                """
            ),
            {"session_id": session_id},
        ).all()

    messages = [
        HistoryMessage(
            role=row.role,
            content=row.content,
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]

    return HistoryOut(session_id=session_id, messages=messages)