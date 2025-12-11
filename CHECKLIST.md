# ✅ Deployment Checklist

## Pre-Deployment (Do These Once)

### 1. System Setup
- [ ] Git installed on your computer
  - Test: Open PowerShell, type `git --version`
- [ ] Hugging Face account created
  - Go to: https://huggingface.co/join

### 2. API Keys Ready
- [ ] OPENAI_API_KEY (from OpenRouter or OpenAI)
- [ ] QDRANT_URL (your Qdrant instance)
- [ ] QDRANT_API_KEY (Qdrant authentication)
- [ ] COHERE_API_KEY (Cohere API)

**Keep these safe!** Don't commit them to git.

### 3. Local Testing (Optional)
- [ ] Run backend: `python openai_agent_retrieval/run_server.py`
- [ ] Run frontend: `python frontend/server.py`
- [ ] Test at: http://localhost:3000
- [ ] Can chat and get responses

---

## Deployment Process

### Phase 1: Git Setup (First Time)

```bash
cd d:\Hackhthon
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git init
git add .
git commit -m "Initial commit"
```

- [ ] Git initialized
- [ ] Files committed

### Phase 2: Create Hugging Face Space

Go to: https://huggingface.co/spaces

- [ ] Click "Create new Space"
- [ ] **Owner**: Your username
- [ ] **Name**: `physical-ai-chatbot`
- [ ] **License**: MIT
- [ ] **SDK**: Docker
- [ ] **Visibility**: Public
- [ ] Click "Create Space"

### Phase 3: Push Code

After Space is created:

```bash
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/physical-ai-chatbot.git
git push huggingface main
```

- [ ] Code pushed successfully
- [ ] No authentication errors

### Phase 4: Add Secrets

Go to: Your Space → Settings → Repository secrets

Add these 4 secrets:

- [ ] `OPENAI_API_KEY` = (your key)
- [ ] `QDRANT_URL` = (your URL)
- [ ] `QDRANT_API_KEY` = (your key)
- [ ] `COHERE_API_KEY` = (your key)

Click "Save" after each one.

### Phase 5: Wait for Build

Your Space page shows status:

- [ ] "Building" (5-15 minutes)
- [ ] "Running" (Success!)

Once "Running", your app is live!

---

## Post-Deployment

### Your Live App

- [ ] App accessible at: `https://YOUR_USERNAME-physical-ai-chatbot.hf.space`
- [ ] Can ask questions
- [ ] Getting responses from backend
- [ ] Sources showing correctly

### Updates

To update your app in the future:

```bash
# Make code changes
# Then:
git add .
git commit -m "Description of changes"
git push huggingface main
# Wait 2-5 minutes for rebuild
```

- [ ] Update process works
- [ ] Auto-rebuild successful

---

## Troubleshooting Checklist

If something doesn't work:

### App won't build
- [ ] Check Space → Settings → Logs
- [ ] Verify all API keys are correct
- [ ] Make sure dependencies are installed locally

### App loads but gives errors
- [ ] Check browser console (F12)
- [ ] Verify all 4 secrets are added
- [ ] Test locally first

### Slow or timing out
- [ ] API keys might have rate limits
- [ ] Qdrant server might be slow
- [ ] Check Space logs for errors

### Can't push code
- [ ] Git username/email configured
- [ ] Correct Space repository URL
- [ ] Have Hugging Face write token

---

## Success Criteria

✅ Deployment is successful when:

1. Your Space shows "Running" status
2. URL loads without errors
3. Can type a question
4. Get a response back
5. Sources are displayed
6. App works on mobile too

---

## File Structure (What Gets Deployed)

```
your-space/
├── Dockerfile          ← Docker config
├── hf_app.py          ← Main app
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── openai_agent_retrieval/
│   ├── main.py
│   ├── agent.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── styles.css
│   └── server.py
├── README.md
└── .gitignore
```

---

## Quick Commands Reference

```bash
# First time setup
git init
git config --global user.name "Name"
git config --global user.email "email"
git add .
git commit -m "message"

# Add Hugging Face remote
git remote add huggingface https://huggingface.co/spaces/USERNAME/SPACE_NAME.git

# Push to Hugging Face
git push huggingface main

# Update app (after first deployment)
git add .
git commit -m "message"
git push huggingface main
```

---

## Support Resources

📖 **Documentation**:
- README.md - Overview
- HUGGINGFACE_DEPLOY.md - Complete guide
- DEPLOYMENT_GUIDE.md - Step-by-step
- QUICK_START.md - Quick reference

🔗 **Useful Links**:
- Hugging Face Spaces: https://huggingface.co/spaces
- Tokens (for git auth): https://huggingface.co/settings/tokens
- Spaces Docs: https://huggingface.co/docs/hub/spaces

---

## Final Checklist

Before you start:
- [ ] Read this entire checklist
- [ ] Have all API keys ready
- [ ] Git installed and working
- [ ] Hugging Face account created

Good to go?
→ Start with "Phase 1: Git Setup" above!

---

**Good luck! 🚀 You've got this!**
