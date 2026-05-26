# AI Solver Bot

Advanced Telegram AI bot with multi-agent architecture for solving complex educational and analytical problems.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Telegram   │────▶│   FastAPI    │────▶│    Redis    │
│   Clients   │     │   Webhook    │     │    Queue    │
└─────────────┘     └──────┬───────┘     └──────┬──────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────┐     ┌──────────────┐
                    │    Agent     │     │   Workers    │
                    │ Orchestrator │     │  (OCR, AI,   │
                    │              │     │  Analytics)  │
                    └──────┬───────┘     └──────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   Math   │ │  Physics │ │Chemistry │
        │  Agent   │ │  Agent   │ │  Agent   │
        └──────────┘ └──────────┘ └──────────┘
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   Code   │ │Validator│ │Explainer │
        │  Agent   │ │  Agent   │ │  Agent   │
        └──────────┘ └──────────┘ └──────────┘

┌─────────────┐     ┌──────────────┐
│  PostgreSQL │     │  AI Provider │
│             │     │  Abstraction │
│  - Users    │     │  - OpenAI    │
│  - Convos   │     │  - Anthropic │
│  - Subs     │     │  - OpenRouter│
│  - Payments │     │  - Gemini    │
└─────────────┘     └──────────────┘
```

## Features

- **Multi-Agent AI**: Math, Physics, Chemistry, Code, and Validation agents
- **OCR Pipeline**: Handwriting, printed text, formula extraction
- **Multi-Provider**: OpenAI, Anthropic, OpenRouter with automatic fallback
- **Step-by-Step**: Detailed solutions with LaTeX formatting
- **Streaming**: Real-time response streaming
- **Rate Limiting**: Per-user request throttling
- **Admin Panel**: User management, analytics, broadcast
- **Security**: Rate limiting, spam protection, webhook validation
- **Scalable**: Async-first, Redis queue, horizontal scaling

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12+, FastAPI |
| Bot Framework | aiogram 3.x |
| Database | PostgreSQL 16 + asyncpg |
| Cache/Queue | Redis 7 |
| AI Providers | OpenAI, Anthropic, OpenRouter |
| OCR | Tesseract, OpenCV, Mathpix |
| Deployment | Docker, Railway |

## Quick Start

### 1. Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Tesseract OCR
- Telegram Bot Token (from @BotFather)

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
alembic upgrade head
```

### 5. Run

```bash
# API + Bot webhook
uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload

# Worker (separate terminal)
python -m app.workers.worker
```

## Docker Deployment

```bash
docker-compose up -d --build
```

## Railway Deployment

### Prerequisites
- Railway account
- Telegram bot token
- AI provider API keys

### Steps

1. **Install Railway CLI**
   ```bash
   curl -fsSL https://railway.app/install.sh | sh
   ```

2. **Login and Init**
   ```bash
   railway login
   railway init
   ```

3. **Set Environment Variables**
   ```bash
   railway variables --set TELEGRAM_BOT_TOKEN=your_token
   railway variables --set OPENAI_API_KEY=sk-your-key
   railway variables --set SECRET_KEY=your-secret
   railway variables --set ENVIRONMENT=production
   ```

4. **Add Add-ons**
   ```bash
   railway add postgres
   railway add redis
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Set Webhook**
   - Set `TELEGRAM_WEBHOOK_URL` to your Railway domain
   - Bot will auto-configure webhook on startup

## Project Structure

```
├── app/
│   ├── api/              # FastAPI routes, webhook
│   ├── agents/           # AI agents (Math, Physics, Chemistry, etc.)
│   ├── bot/              # Telegram bot handlers, keyboards, middlewares
│   ├── config/           # Pydantic settings
│   ├── core/             # AI providers, DI container
│   ├── db/               # Database session, migrations
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic
│   ├── schemas/          # Pydantic schemas
│   ├── security/         # Rate limiting, validation
│   ├── payments/         # Payment processing
│   ├── ocr/              # OCR pipeline
│   ├── workers/          # Background task workers
│   └── utils/            # Helpers, logging
├── Dockerfile
├── docker-compose.yml
├── railway.json
├── Procfile
├── pyproject.toml
└── requirements.txt
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/webhook` | Telegram webhook |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/metrics` | Prometheus metrics |

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Launch the bot |
| `/solve <problem>` | Solve a problem |
| `/image` | Upload image for solving |
| `/profile` | View your stats |
| `/help` | Show help |
| `/admin` | Admin panel (admins only) |

## AI Provider Configuration

The system supports multiple AI providers with automatic fallback:

**OpenAI**: Set `OPENAI_API_KEY`
**Anthropic**: Set `ANTHROPIC_API_KEY`  
**OpenRouter**: Set `OPENROUTER_API_KEY`
**Gemini**: Set `GEMINI_API_KEY` (optional)

Set `DEFAULT_AI_PROVIDER` to choose primary provider.
Set `AI_FALLBACK_ENABLED=true` to enable automatic fallback.

## OCR Configuration

- Install Tesseract with language packs
- Supported languages: English, Russian, German, French, Spanish
- Optional Mathpix API for formula recognition
- Image preprocessing: deskew, denoise, contrast enhancement, binarization

## Performance Optimization

- Redis caching for frequent requests
- Connection pooling for PostgreSQL
- Async database access with asyncpg
- Streaming AI responses for reduced latency
- Token optimization with configurable limits
- Request queueing for load management
- Horizontal scaling via Railway workers

## Security

- Rate limiting per user (configurable)
- Webhook secret validation
- Input sanitization
- API key encryption via env variables
- SQL injection protection via SQLAlchemy
- Audit logging
- Admin-only command filtering

## License

MIT
