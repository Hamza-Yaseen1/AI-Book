# Step-by-Step Guide: Deploy to Hugging Face Spaces

## Prerequisites
- GitHub account (optional but recommended)
- Hugging Face account
- API keys ready:
  - OpenRouter or OpenAI API key
  - Qdrant URL and API key
  - Cohere API key

---

## Baby Steps to Deploy

### Step 1: Prepare Your Local Environment
✅ You already have your code ready in `d:\Hackhthon`

### Step 2: Create a Git Repository (Recommended)

If you don't have Git installed:
1. Download from https://git-scm.com/
2. Install with default settings

Initialize Git in your project:
```bash
cd d:\Hackhthon
git init
git add .
git commit -m "Initial commit: RAG chatbot with FastAPI and Qdrant"
```

### Step 3: Create Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up with email
3. Verify email

### Step 4: Create a New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space" button
3. Fill in:
   - **Owner**: Your username (select from dropdown)
   - **Space name**: `physical-ai-chatbot` (or any name)
   - **License**: Select MIT or Apache 2.0
   - **Space SDK**: Select "Docker"
   - **Visibility**: Public (or Private if you prefer)
4. Click "Create Space"

### Step 5: Get Your Space Repository URL
After creating the Space:
- You'll see a page with repository information
- Copy the repository URL (looks like: `https://huggingface.co/spaces/your-username/physical-ai-chatbot`)
- The git URL will be: `https://huggingface.co/spaces/your-username/physical-ai-chatbot.git`

### Step 6: Connect Your Code to the Space

In your command line:

```bash
# Navigate to your project
cd d:\Hackhthon

# Add Hugging Face as a remote
git remote add huggingface https://huggingface.co/spaces/your-username/physical-ai-chatbot.git

# Push your code
git push huggingface main
```

**Note**: Replace `your-username` with your actual Hugging Face username

### Step 7: Add API Secrets to the Space

1. Go to your Space page
2. Click "Settings" (gear icon)
3. Scroll to "Repository secrets"
4. Add each secret:
   - **Name**: `OPENAI_API_KEY`
     **Value**: Your OpenRouter or OpenAI key
   - **Name**: `QDRANT_URL`
     **Value**: Your Qdrant URL
   - **Name**: `QDRANT_API_KEY`
     **Value**: Your Qdrant API key
   - **Name**: `COHERE_API_KEY`
     **Value**: Your Cohere API key

5. Click "Save" for each secret

### Step 8: Update .env to Use Secrets

The app will automatically read environment variables on Hugging Face.

### Step 9: Wait for Deployment

1. Go back to your Space main page
2. You'll see a status indicating "Building" or "Running"
3. Wait 5-10 minutes for the Docker image to build
4. Once complete, you'll see "Running" status

### Step 10: Access Your App

1. Your app will be live at:
   `https://your-username-physical-ai-chatbot.hf.space`
2. Share this link with anyone!

---

## Troubleshooting

### App shows "Building" forever
- Check the logs: Go to Space Settings → Logs
- Look for error messages
- Common issues: Wrong API keys, missing dependencies

### "Port already in use" error
- Edit `frontend/server.py` to use a different port
- Or check Hugging Face documentation for port requirements

### App crashes on startup
- Check logs in Space Settings
- Verify all API keys are correct
- Make sure `.env` variables match the secret names

### Changes not updating
```bash
git push huggingface main
```
This will trigger a rebuild with your latest code.

---

## Quick Reference

**After first setup, to update your app:**

```bash
cd d:\Hackhthon

# Make your changes to the code

git add .
git commit -m "Your change description"
git push huggingface main

# Wait 2-5 minutes for auto-rebuild and redeploy
```

---

## What Gets Deployed

Your Hugging Face Space will have:
- ✅ Backend API (FastAPI) on internal port 8000
- ✅ Frontend (HTML/CSS/JS) accessible at the Space URL
- ✅ All Python dependencies installed
- ✅ Docker container running both servers

---

## Next Steps

1. ✅ Prepare files (Dockerfile, README, .env)
2. ✅ Initialize Git repository
3. ✅ Create Hugging Face Space (Docker)
4. ✅ Push code to Space
5. ✅ Add API secrets
6. ✅ Wait for deployment
7. ✅ Share your Space link!

---

## Tips for Success

- **Keep API keys secret** - Use Space Secrets, never commit them
- **Monitor logs** - Check Space Settings → Logs if something fails
- **Test locally first** - Make sure it works on your computer before pushing
- **Use meaningful commits** - "git commit -m" messages help track changes
- **Auto-reload** - Any git push to main will auto-build and deploy

Good luck! 🚀
