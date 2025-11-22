# 🤖 Hifadhi Multi-Agent System

> Enterprise-grade AI-powered HR Management System for Kenya, built with LangGraph, OpenAI, and M-Pesa integration.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.28-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Observability](#observability)
- [PayLink Integration](#paylink-integration)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [License](#license)

---

## 🌟 Overview

**Hifadhi** is a production-ready multi-agent AI system designed specifically for HR management in Kenya. It automates candidate screening, onboarding, compliance verification (KRA/NSSF/NHIF), payroll processing via M-Pesa, and provides real-time analytics.

### **Key Capabilities:**

- 🎯 **Intelligent Routing** - Supervisor agent analyzes intent and routes to specialists
- 💰 **M-Pesa Payments** - Automated salary processing via PayLink STK Push
- 📊 **Analytics** - Real-time hiring metrics and pipeline insights
- ✅ **Compliance** - KRA PIN, NSSF, NHIF verification
- 📝 **Onboarding** - Automated task tracking and document collection
- 🔍 **Candidate Screening** - AI-powered application review
- 💬 **RAG-Powered FAQ** - ChromaDB vector search for HR questions
- 🔭 **Observability** - Phoenix (Arize) distributed tracing

---

## 🚀 Features

### **Multi-Agent Architecture**

| Agent | Responsibility | Tools |
|-------|---------------|-------|
| **Supervisor** | Central orchestrator, intent analysis | `ask_user` |
| **Candidate Screening** | Application tracking, interviews | `get_candidate_details`, `get_application_status` |
| **Onboarding** | Task management, document collection | `get_onboarding_tasks` |
| **Compliance** | KRA/NSSF/NHIF verification | `get_compliance_status` |
| **Payroll** | M-Pesa payments, salary processing | `initiate_mpesa_stk_push`, `get_payroll_history` |
| **Analytics** | Hiring metrics, pipeline analytics | `get_hiring_metrics`, `get_pipeline_analytics` |
| **General Help** | FAQ responses (RAG) | ChromaDB vector search |
| **Human Escalation** | Complex case handoff | N/A |
| **Final Answer** | Response polishing | N/A |

### **Technology Stack**

- **Framework**: LangGraph (state-based orchestration)
- **LLM**: OpenAI GPT-4o-mini
- **Database**: SQLite (500 candidates, 20 jobs, 1000 applications)
- **Vector Store**: ChromaDB (HR FAQs)
- **Payments**: PayLink M-Pesa API
- **Observability**: Phoenix (Arize)
- **API**: FastAPI
- **Deployment**: Docker + Docker Compose

---

## 🏗️ Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌────────────────────────────┐
│   Supervisor Agent         │  ← Central Orchestrator
│  (Intent Analysis)         │
└──────┬────────────────────┬┘
       │                    │
       ▼                    ▼
┌──────────────┐    ┌───────────────┐
│ Specialist 1 │    │ Specialist 2  │
│ (Payroll)    │    │ (Screening)   │
└──────┬───────┘    └───────┬───────┘
       │                    │
       └────────┬───────────┘
                ▼
       ┌────────────────┐
       │ Final Answer   │
       │ Agent          │
       └────────────────┘
```

**Workflow Flow:**
1. User query → Supervisor
2. Supervisor routes to specialist(s)
3. Specialist executes tasks (tool calls)
4. Returns to Supervisor
5. Supervisor routes to Final Answer
6. Polished response → User

---

## ⚡ Quick Start

### **Prerequisites**

- Python 3.11+
- Docker & Docker Compose (optional)
- OpenAI API key
- PayLink API credentials (for payments)

### **Installation**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/hifadhi-os.git
cd hifadhi-os

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 5. Initialize database
python data/setup_database.py
python data/load_hr_faqs.py

# 6. Run the system
python main.py
```

### **Interactive Mode**

```bash
$ python main.py

🤖 Hifadhi Interactive Mode
Type 'exit' to quit

HR Manager: What is the status of application APP00001?

======================================================================
HIFADHI MULTI-AGENT SYSTEM
======================================================================
Query: What is the status of application APP00001?
======================================================================

---SUPERVISOR AGENT---
📝 User Query: What is the status of application APP00001?
Supervisor iteration: 1
🎯 Intent: check_application_status
➡️ Routing to: candidate_screening_agent

---CANDIDATE SCREENING AGENT---
📋 Task: Check application status for APP00001
🔍 Fetching details...
✅ Done

======================================================================
FINAL RESPONSE
======================================================================
Application APP00001 (Jane Mwangi for Customer Service Representative):
• Status: Interview Scheduled
• AI Screening Score: 78/100  
• Interview Date: 2024-12-15 at  10:00 AM
• Location: Nairobi Office
======================================================================
```

---

## 🐳 Deployment

### **Docker Compose (Recommended)**

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add API keys

# 2. Deploy
chmod +x deploy.sh
./deploy.sh

# Services will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Phoenix: http://localhost:6006
```

### **Manual Docker Build**

```bash
docker build -t hifadhi-agent-system .

docker run -d \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name hifadhi-app \
  hifadhi-agent-system
```

### **Docker Compose Commands**

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f hifadhi

# Stop services
docker-compose down

# Rebuild
docker-compose build --no-cache
```

---

## 📡 API Documentation

### **Base URL**
```
http://localhost:8000
```

### **Endpoints**

#### **1. Health Check**
```http
GET /
```

**Response:**
```json
{
  "status": "online",
  "system": "Hifadhi Multi-Agent OS"
}
```

#### **2. Chat (Process Query)**
```http
POST /chat
Content-Type: application/json

{
  "query": "Process salary for candidate CAND00001",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "I've initiated a payment of KES 50,000...",
  "session_id": "session_20241122_103045",
  "agent_history": [
    "Supervisor Agent: Analyzed intent",
    "Payroll Agent: Processed payment"
  ],
  "requires_action": false
}
```

#### **3. PayLink Webhook**
```http
POST /webhooks/paylink
Content-Type: application/json

{
  "transaction_id": "TRX123456",
  "status": "completed",
  "amount": 50000,
  "mpesa_receipt_number": "PK12ABC345"
}
```

**Response:**
```json
{
  "status": "received"
}
```

### **Interactive API Docs**

Visit `http://localhost:8000/docs` for Swagger UI with live API testing.

---

## 🔭 Observability

### **Phoenix Dashboard**

**Start Phoenix:**
```bash
docker-compose up phoenix
```

**Access Dashboard:**
```
http://localhost:6006
```

**Features:**
- Distributed tracing across all agents
- LLM call monitoring
- Tool execution tracking
- Error debugging
- Performance metrics

**Example Trace:**
```
supervisor_agent (250ms)
├─ analyze_intent (50ms)
├─ extract_entities (30ms)
└─ route_decision (20ms)

payroll_agent (1200ms)
├─ tool.get_candidate_details (80ms)
├─ tool.initiate_mpesa_stk_push (1000ms)
└─ format_response (50ms)

final_answer_agent (100ms)
```

---

## 💳 PayLink Integration

### **M-Pesa STK Push**

```python
from tools.paylink_integration import initiate_mpesa_stk_push

result = initiate_mpesa_stk_push(
    candidate_id="CAND00001",
    amount=50000.0,
    phone_number="0712345678",
    payment_type="salary",
    description="November 2024 Salary"
)

# Result:
# {
#     "success": True,
#     "transaction_id": "TRX123456789",
#     "message": "STK Push sent to 254712345678",
#     "status": "pending"
# }
```

### **Bulk Payroll Processing**

```python
from tools.paylink_integration import process_bulk_payments

payments = [
    {"candidate_id": "CAND00001", "amount": 50000, "phone_number": "0712345678"},
    {"candidate_id": "CAND00002", "amount": 45000, "phone_number": "0723456789"}
]

results = process_bulk_payments(payments)
# {
#     "total": 2,
#     "pending": 2,
#     "failed": 0
# }
```

### **Payment Status Check**

```python
from tools.paylink_integration import check_payment_status

status = check_payment_status("TRX123456789")
# {
#     "status": "completed",
#     "mpesa_receipt": "PK12ABC345"
# }
```

---

## ⚙️ Configuration

### **Environment Variables**

Edit `.env`:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# PayLink
PAYLINK_API_KEY=your_api_key
PAYLINK_API_SECRET=your_api_secret
PAYLINK_WEBHOOK_SECRET=your_webhook_secret
PAYLINK_CALLBACK_URL=https://yourdomain.com/webhooks/paylink

# Phoenix
PHOENIX_COLLECTOR_ENDPOINT=http://127.0.0.1:6006/v1/traces

# Database
DATABASE_PATH=data/hifadhi.db
VECTOR_STORE_PATH=data/chroma_db

# Logging
LOG_LEVEL=INFO
```

---

## 💻 Development

### **Project Structure**

```
HifadhiOS/
├── agents/              # 9 specialized agents
│   ├── supervisor_agent.py
│   ├── candidate_screening_agent.py
│   ├── payroll_agent.py
│   └── ...
├── workflows/           # LangGraph orchestration
│   ├── langgraph_workflow.py
│   ├── routing_logic.py
│   └── workflow_monitor.py
├── tools/               # Database, PayLink, Analytics
│   ├── database_tools.py
│   ├── paylink_integration.py
│   └── analytics_tools.py
├── utils/               # LLM client, tracing
│   ├── llm_client.py
│   ├── tracing.py
│   └── state_management.py
├── data/                # SQLite DB + ChromaDB
├── tests/               # Unit & integration tests
├── docs/                # Documentation
├── web_server.py        # FastAPI server
├── main.py              # CLI entry point
├── Dockerfile
└── docker-compose.yml
```

### **Adding a New Agent**

1. Create `agents/new_agent.py`
2. Implement agent function with state parameter
3. Add to `workflows/langgraph_workflow.py`
4. Update routing logic in `workflows/routing_logic.py`
5. Add tests in `tests/`

---

## 🧪 Testing

### **Run All Tests**

```bash
python -m unittest discover tests
```

### **Specific Test Suites**

```bash
# API tests
python -m unittest tests/test_api.py

# PayLink tests
python -m unittest tests/test_paylink.py

# Workflow tests
python -m unittest tests/test_workflow.py
```

### **Test Coverage**

- ✅ Unit tests for all agents
- ✅ Integration tests for API endpoints
- ✅ PayLink payment flow tests
- ✅ Workflow routing tests
- ✅ Database tools tests

---

## 📊 Performance

- **Average Query Processing:** 2-3 seconds
- **Database Queries:** <100ms
- **LLM Calls:** 500-1500ms
- **PayLink API:** 1-2 seconds (STK Push)
- **Concurrent Requests:** 50+ (with Uvicorn workers)

---

## 🔒 Security

- ✅ Environment variable-based configuration
- ✅ HMAC-SHA256 webhook signature verification
- ✅ API key authentication for PayLink
- ✅ Input validation (Pydantic models)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Rate limiting (TODO for production)

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👥 Contributors

- **Imain** - Lead Developer

---

## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini
- LangChain team for LangGraph
- Arize for Phoenix observability
- PayLink for M-Pesa integration

---

## 📞 Support

For issues and questions:
- GitHub Issues: [Issues](https://github.com/yourusername/hifadhi-os/issues)
- Email: support@hifadhi.ai
- Documentation: [docs/](docs/)

---

**Built with ❤️ in Kenya 🇰🇪**
