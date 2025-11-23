# Hifadhi AI - Global AI Hiring Operating System v6.0

**The world's first Agent-Native HR platform powered by Multi-Agent AI**

Built for emerging markets AND global enterprises.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```
OPENAI_API_KEY=your_key_here
```

### 3. Start the Servers
```bash
# Terminal 1: Main HR System (port 8000)
python agent_server.py

# Terminal 2: Agent Orchestrator (port 8001)
python agent_os_server.py
```

### 4. Access Dashboard
```
http://localhost:8000/dashboard
```

---

## ✨ Key Features

### 🤖 Multi-Agent AI System
- **SourcingAgent**: Finds top talent from databases and job boards
- **ScreeningAgent**: AI-powered resume analysis & compliance checks
- **InterviewAgent**: Automated interview scheduling & coordination

### 🎯 Mission Control
Launch high-level hiring missions like "Hire a Senior Python Developer" and watch AI agents collaborate autonomously.

### 📊 Real-Time Intelligence
- Live agent status monitoring
- AI-powered insights on every candidate
- Actionable recommendations

### 🎨 Premium Soft UI Design
Beautiful glassmorphism and neumorphic interface built with Tailwind CSS.

---

## 📁 Project Structure

```
HifadhiOS/
├── agent_engine.py          # Multi-agent orchestration system
├── agent_os_server.py        # Agent API (port 8001)
├── agent_server.py           # Main HR API (port 8000)
├── dashboard_v6.html         # Mission Control UI
├── docs/
│   ├── ARCHITECTURE_V2.md    # System design
│   └── QUICK_START.md        # Getting started guide
├── tools/                    # Agent tools (DB, email, etc.)
├── utils/                    # LLM client & utilities
└── data/                     # SQLite database
```

---

## 🔧 Architecture

### Agent Orchestration
The system uses an **Event-Driven Architecture** where agents communicate via an event bus:

1. **User** launches a mission
2. **Orchestrator** delegates to SourcingAgent
3. **SourcingAgent** finds candidates → emits `CANDIDATE_FOUND`
4. **ScreeningAgent** screens candidate → triggers next step
5. **InterviewAgent** schedules interview → emits `MISSION_COMPLETED`

### APIs
- **Port 8000**: HR CRUD operations, analytics, dashboard
- **Port 8001**: Agent orchestration, mission control, events

---

## 🌍 Global Readiness Roadmap

### Phase 1 ✅ (Current)
- Multi-agent architecture
- Real-time agent monitoring
- Mission-based workflows

### Phase 2 🚧 (Next)
- PayLink integration for agent economy
- Multi-tenant support (org isolation)
- ATS connectors (Greenhouse, Lever, BambooHR)

### Phase 3 🔮 (Future)
- Global compliance layer (GDPR, EEOC, SOC2)
- AI video interviews with NLP scoring
- Salary intelligence (Payscale, Levels.fyi)

---

## 💡 Usage Examples

### Launch a Mission
```javascript
// Via UI: Mission Control tab
// Or via API:
POST http://localhost:8001/api/v2/mission
{
  "mission": "Find senior Python developers with 5+ years experience"
}
```

### Monitor Agents
```javascript
GET http://localhost:8001/api/v2/agents
// Returns real-time status of all agents
```

### Get Mission Results
```javascript
GET http://localhost:8001/api/v2/events
// Returns recent events including MISSION_COMPLETED
```

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLite, Uvicorn
- **AI**: OpenAI GPT-4o-mini with function calling
- **Frontend**: Tailwind CSS, Vanilla JavaScript
- **Architecture**: Multi-Agent System (MAS), Event-Driven

---

## 📝 License

MIT License - Built for the future of AI-powered hiring.

---

## 🤝 Contributing

This is the foundation of a global AI Hiring OS. Contributions welcome!

**Need help?** Check `docs/QUICK_START.md` for detailed setup instructions.

**Want to integrate?** See `docs/ARCHITECTURE_V2.md` for system design.

---

**Built with ❤️ for Africa and the World**
