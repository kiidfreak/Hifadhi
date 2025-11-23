# Hifadhi AI - Quick Start Guide

## Prerequisites
- Python 3.8+
- OpenAI API key

## Setup (5 minutes)

### 1. Clone & Install
```bash
cd HifadhiOS
pip install -r requirements.txt
```

### 2. Configure
Create `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Initialize Database
```bash
python -c "from tools.database_tools import init_database; init_database()"
```

### 4. Start Servers

**Terminal 1** - Main HR System:
```bash
python agent_server.py
```

**Terminal 2** - Agent Orchestrator:
```bash
python agent_os_server.py
```

### 5. Access Dashboard
Open browser: `http://localhost:8000/dashboard`

---

## First Mission

1. Click **Mission Control** in sidebar
2. Type: `Find Python developers with 5+ years experience`
3. Click **Launch Mission**
4. Watch agents work in real-time!

You'll see:
- 🟡 **SourcingAgent** → Finding candidates
- 🟡 **ScreeningAgent** → Screening resumes
- 🟡 **InterviewAgent** → Scheduling interviews
- ✅ **Mission Complete** with next steps

---

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Agents Not Working
- Check `.env` has valid OpenAI API key
- Restart both servers
- Check browser console for errors

### No Data Showing
```bash
# Reset database
python -c "from tools.database_tools import init_database; init_database()"
```

---

## What's Next?

- ✅ Try different missions
- ✅ Explore AI insights on candidates
- ✅ Review agent activity logs
- 📚 Read `ARCHITECTURE_V2.md` to understand the system

**Need help?** Check logs in terminal or browser console.
