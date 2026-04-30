# Environment Setup Guide

## ⚠️ SECURITY WARNING

**NEVER commit `.env` files to git!** They contain sensitive API keys and credentials.

The `.gitignore` file is configured to automatically exclude all `.env` files.

## Quick Setup

### 1. Frontend (React)

```bash
cd Frontend
cp .env.example .env
# Edit .env and fill in your values
```

Required variables:
- `REACT_APP_API_BASE_URL` - Your Java backend URL
- `REACT_APP_CHAT_API_BASE_URL` - Your SQL Agent URL

### 2. Backend (Java/Spring)

```bash
cd Backend
cp .env.example .env
# Edit .env and fill in your values
```

Required variables:
- `NEON_DATABASE_URL` - PostgreSQL connection string
- `CLOUDINARY_*` - For resume uploads
- `AFFINDA_API_KEY` - For resume parsing

### 3. SQL-Agent (Python)

```bash
cd SQL-Agent
cp .env.example .env
# Edit .env and fill in your values
```

Required variables:
- `NEON_DATABASE_URL` - Same database as Backend
- Choose ONE LLM provider:
  - **Ollama** (local): `MODEL_PROVIDER=ollama`
  - **Groq** (fast cloud): `MODEL_PROVIDER=groq` + `GROQ_API_KEY`
  - **Gemini** (Google): `MODEL_PROVIDER=gemini` + `GOOGLE_API_KEY`

## Getting API Keys

### Affinda (Resume Parsing)
1. Sign up at [affinda.com](https://www.affinda.com)
2. Get API key from dashboard
3. Add to `Backend/.env`

### Groq (Fast LLM)
1. Sign up at [groq.com](https://groq.com)
2. Create API key
3. Add to `SQL-Agent/.env`

### Google Gemini
1. Go to [Google AI Studio](https://aistudio.google.com)
2. Create API key
3. Add to `SQL-Agent/.env`

### Cloudinary (File Uploads)
1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Get credentials from dashboard
3. Add to `Backend/.env`

## Verification

Check that your `.env` files are NOT tracked by git:

```bash
git status
```

You should NOT see `.env` files in the output.

## Troubleshooting

**Issue:** "Missing environment variable" errors
- **Fix:** Copy `.env.example` to `.env` and fill in all values

**Issue:** Changes not reflecting
- **Fix:** Restart the server after editing `.env`

**Issue:** Accidentally committed `.env`
- **Fix:** 
  ```bash
  git rm --cached .env
  git commit -m "Remove .env file"
  ```
  Then rotate your API keys immediately!
