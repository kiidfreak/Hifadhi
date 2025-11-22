# 🚀 QUICK START GUIDE - Production Setup

## Step 1: Get OpenAI API Key (2 minutes)
1. Go to: https://platform.openai.com/api-keys
2. Create account (free)
3. Click "Create new secret key"
4. Copy the key (starts with sk-proj-...)

## Step 2: Configure Environment (1 minute)
Edit the .env file:
```bash
OPENAI_API_KEY=sk-proj-paste-your-key-here
```

## Step 3: Run Production Server (1 minute)
```bash
python web_server.py
```

## Step 4: Test (1 minute)
Open browser: http://localhost:8000/ui
Ask: "What is the status of application APP00001?"

Now you'll get REAL AI responses! 🤖

---

## Optional: Enable M-Pesa Payments

### Get PayLink Account
1. Visit: https://paylink.ke
2. Sign up for business account
3. Get API credentials
4. Add to .env:
```bash
PAYLINK_API_KEY=your_key
PAYLINK_API_SECRET=your_secret
```

---

## Deploy to Cloud (Azure Example)

### Prerequisites
- Azure account (free tier available)
- Azure CLI installed

### Deploy
```bash
# Login
az login

# Deploy
az webapp up --name hifadhi-hr-prod --runtime "PYTHON:3.11" --sku B1

# Your app will be live at:
# https://hifadhi-hr-prod.azurewebsites.net
```

---

## Deploy to Heroku (Easiest)

```bash
# Install Heroku CLI
# Then:

heroku create hifadhi-hr
git push heroku main

# Live at: https://hifadhi-hr.herokuapp.com
```

---

## Security Checklist for Production

- [ ] Add HTTPS/SSL certificate
- [ ] Set strong API keys
- [ ] Enable rate limiting
- [ ] Add authentication (login system)
- [ ] Backup database daily
- [ ] Monitor logs
- [ ] Set up error alerts

---

## Scaling for Growth

### 100 employees
- Current setup works perfectly ✅

### 1,000 employees  
- Add Redis caching
- Use PostgreSQL instead of SQLite
- 2-4 Uvicorn workers

### 10,000+ employees
- Kubernetes cluster
- Load balancer
- Distributed database
- Dedicated AI infrastructure

---

## Support & Maintenance

### Monthly Tasks
- [ ] Review analytics
- [ ] Update candidate data
- [ ] Check payment logs
- [ ] Monitor API costs

### Quarterly Tasks
- [ ] Security audit
- [ ] Performance optimization
- [ ] Feature updates
- [ ] User feedback review

---

## Getting Help

1. **Documentation**: Check `/docs` folder
2. **API Docs**: http://localhost:8000/docs
3. **Logs**: Check `logs/hifadhi.log`
4. **Phoenix Dashboard**: http://localhost:6006 (debugging)

---

## ROI Calculator

### Before Hifadhi
- HR Manager time: 20 hrs/week on manual tasks
- Cost: ~$1,000/month in HR labor

### After Hifadhi  
- HR Manager time: 5 hrs/week
- System cost: ~$20/month
- **Savings**: ~$980/month + faster hiring

**Payback Period**: Immediate! 🎉

---

## Next Steps

1. ✅ You have the UI and demo working
2. ⏳ Add OpenAI API key → Get real AI
3. ⏳ Deploy to cloud → Go live
4. ⏳ Add PayLink → Process payments
5. ⏳ Market to companies → Start earning

**You're 95% there!** Just need that API key! 🚀
