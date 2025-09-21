# Complete Commands Guide for Beginners 🚀

This guide provides step-by-step terminal/command line instructions for users with no prior development experience. Follow these instructions carefully to set up and run the Math AI Agent.

## Table of Contents
1. [Prerequisites Check](#prerequisites-check)
2. [Setting Up Python Environment](#setting-up-python-environment)
3. [Setting Up Node.js Environment](#setting-up-nodejs-environment)
4. [Project Setup](#project-setup)
5. [Backend Setup and Installation](#backend-setup-and-installation)
6. [Frontend Setup and Installation](#frontend-setup-and-installation)
7. [Running the Application](#running-the-application)
8. [Testing the System](#testing-the-system)
9. [Troubleshooting Commands](#troubleshooting-commands)

---

## Prerequisites Check

Before starting, let's check if you have the required software installed.

### Check Python Installation

Open your terminal/command prompt and type:

```bash
python --version
```

**Expected Output:** `Python 3.8.x` or higher (e.g., `Python 3.10.12`)

**If Python is not installed or version is too old:**
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: Use `brew install python` or download from python.org
- **Linux**: Use `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### Check Node.js Installation

```bash
node --version
```

**Expected Output:** `v16.x.x` or higher (e.g., `v18.17.0`)

```bash
npm --version
```

**Expected Output:** `8.x.x` or higher (e.g., `9.6.7`)

**If Node.js is not installed:**
- Download from [nodejs.org](https://nodejs.org/) (choose LTS version)
- This will install both Node.js and npm

### Check Git Installation (Optional but Recommended)

```bash
git --version
```

**Expected Output:** `git version 2.x.x`

---

## Setting Up Python Environment

### Step 1: Navigate to Your Desired Directory

Choose where you want to store the project. For example, your Desktop:

```bash
# On Windows
cd Desktop

# On macOS/Linux
cd ~/Desktop
```

### Step 2: Clone or Download the Project

**If you have the project files already:**
```bash
cd math-ai-agent
```

**If you need to clone from Git:**
```bash
git clone <repository-url>
cd math-ai-agent
```

### Step 3: Create a Python Virtual Environment

**What this does:** Creates an isolated Python environment for this project.

```bash
# Navigate to the backend directory
cd backend

# Create virtual environment (this creates a folder called 'venv')
python -m venv venv
```

**On Windows, if `python` doesn't work, try:**
```bash
python3 -m venv venv
```

### Step 4: Activate the Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**Success indicator:** Your terminal prompt should now show `(venv)` at the beginning.

**Example:**
```
(venv) C:\Users\YourName\Desktop\math-ai-agent\backend>
```

---

## Setting Up Node.js Environment

### Step 1: Navigate to Frontend Directory

**From the project root directory:**
```bash
# If you're in the backend directory, go back to project root
cd ..

# Now go to frontend directory
cd frontend
```

### Step 2: Verify You're in the Right Directory

```bash
# This should show package.json among other files
ls
```

**On Windows:**
```bash
dir
```

**Expected files:** You should see `package.json`, `src/`, `public/`, etc.

---

## Project Setup

### Step 1: Configure Backend Environment

**Navigate to backend directory:**
```bash
cd ../backend
```

**Copy the example environment file:**
```bash
# On macOS/Linux
cp .env.example .env

# On Windows
copy .env.example .env
```

**Edit the .env file:**
You can use any text editor. For example:

```bash
# On Windows
notepad .env

# On macOS
open -e .env

# On Linux
nano .env
```

**Important:** Replace the placeholder values with your actual API keys.

**Example .env content:**
```
# Required for AI responses
GEMINI_API_KEY=your_api_key

# Optional for enhanced Google search fallback
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here

# Database and app configuration
DATABASE_URL=sqlite:///./math_ai_agent.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./math_ai_agent.db
LOG_LEVEL=INFO
DEBUG=False
CORS_ORIGINS=["http://localhost:3000"]
```

**Getting Google Search API Keys (Optional but Recommended):**

1. **Google Custom Search API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable "Custom Search API"
   - Create an API key
   
2. **Google Search Engine ID:**
   - Go to [Google Custom Search Engine](https://cse.google.com/cse/)
   - Create a new search engine
   - Set it to search the entire web
   - Copy the Search Engine ID

---

## Backend Setup and Installation

### Step 1: Ensure Virtual Environment is Active

**Check if `(venv)` appears in your prompt. If not, activate it:**

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 2: Install Python Dependencies

**What this does:** Downloads and installs all required Python packages.

```bash
pip install -r requirements.txt
```

**This command will install packages like:**
- FastAPI (web framework)
- uvicorn (web server)
- SQLAlchemy (database)
- google-generativeai (Gemini API)
- And many more...

**Expected output:** You'll see lots of "Successfully installed..." messages.

**If you get permission errors on macOS/Linux:**
```bash
pip install --user -r requirements.txt
```

### Step 3: Verify Installation

```bash
# Check if FastAPI is installed
python -c "import fastapi; print('FastAPI installed successfully')"
```

**Expected output:** `FastAPI installed successfully`

---

## Frontend Setup and Installation

### Step 1: Navigate to Frontend Directory

```bash
# From backend directory, go to frontend
cd ../frontend
```

### Step 2: Install Node.js Dependencies

**What this does:** Downloads and installs all required JavaScript packages.

```bash
npm install
```

**This process will:**
- Create a `node_modules/` folder
- Download React, styled-components, axios, and other packages
- May take 2-5 minutes depending on your internet speed

**Expected output:** You'll see a progress bar and "added X packages" at the end.

**If you get permission errors:**
```bash
sudo npm install
```

### Step 3: Verify Installation

```bash
# Check if React is installed
npm list react
```

**Expected output:** Should show React version (e.g., `react@18.2.0`)

---

## Running the Application

### Step 1: Start the Backend Server

**Open a new terminal window/tab and navigate to backend:**
```bash
cd /path/to/your/math-ai-agent/backend

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**What each part means:**
- `uvicorn`: The web server that runs FastAPI
- `app.main:app`: Points to the FastAPI app in app/main.py
- `--reload`: Automatically restarts when code changes
- `--host 0.0.0.0`: Makes server accessible from any IP
- `--port 8001`: Runs on port 8001

**Success indicators:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal window open!** The backend server is now running.

### Step 2: Start the Frontend Server

**Open another new terminal window/tab and navigate to frontend:**
```bash
cd /path/to/your/math-ai-agent/frontend

# Start the React development server
npm start
```

**What this does:**
- Compiles the React application
- Starts a development server
- Usually opens your browser automatically

**Success indicators:**
```
Compiled successfully!

You can now view math-ai-agent-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.100:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

**Keep this terminal window open too!** The frontend server is now running.

### Step 3: Access the Application

**Open your web browser and go to:**
```
http://localhost:3000
```

**You should see:**
- A beautiful Math AI Agent interface
- An input box for math questions
- Example questions you can click
- A clean, professional design

---

## Testing the System

### Basic Browser Testing

**Try these math questions in the web interface:**

1. **Simple arithmetic:** `2 + 2`
2. **Algebra:** `Solve 3x + 7 = 10`
3. **Calculus:** `What is the derivative of x^2?`
4. **Geometry:** `Find the area of a circle with radius 5`

**Expected results:**
- Detailed step-by-step solutions
- "Generated using Gemini AI" text
- 3 reference links at the bottom
- High confidence scores (0.8-0.9)

**Try these non-math questions (should show error popup):**

1. `What's the weather today?`
2. `How do I cook pasta?`
3. `Tell me a joke`

**Expected results:**
- Beautiful error popup appears
- Message: "Please enter a valid math question"
- Helpful suggestions for math questions

### API Testing with Command Line

**Test the backend API directly using curl:**

**Test a math query:**
```bash
curl -X POST "http://localhost:8001/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Solve 2x + 4 = 2",
    "context": null,
    "user_id": "test_user"
  }'
```

**Expected response:** JSON with detailed solution showing x = -1

**Test a non-math query:**
```bash
curl -X POST "http://localhost:8001/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the weather?",
    "context": null,
    "user_id": "test_user"
  }'
```

**Expected response:** Error message about non-mathematical question

### Check API Documentation

**Visit in your browser:**
```
http://localhost:8001/docs
```

**You should see:**
- Interactive API documentation
- List of available endpoints
- Ability to test API calls directly

---

## Troubleshooting Commands

### Backend Issues

#### Issue: "ModuleNotFoundError" when starting backend

**Problem:** Python can't find required packages.

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend

# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Try starting again
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### Issue: "Address already in use" error

**Problem:** Port 8001 is being used by another process.

**Solution:**
```bash
# Find and kill the process using port 8001
# On macOS/Linux:
lsof -ti:8001 | xargs kill -9

# On Windows:
netstat -ano | findstr :8001
# Note the PID and then:
taskkill /PID <PID_NUMBER> /F

# Or use a different port:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

#### Issue: "Gemini API not working" (getting fallback responses)

**Problem:** API key not configured or invalid.

**Solution:**
```bash
# Check if .env file exists
ls -la .env  # macOS/Linux
dir .env     # Windows

# Edit the .env file and ensure GEMINI_API_KEY is set correctly
nano .env    # Linux
open -e .env # macOS
notepad .env # Windows

# Test the API key
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('API Key:', os.getenv('GEMINI_API_KEY'))
"
```

### Frontend Issues

#### Issue: "npm start" fails

**Problem:** Node modules corrupted or missing.

**Solution:**
```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json  # macOS/Linux
rmdir /s node_modules & del package-lock.json  # Windows

# Reinstall everything
npm install

# Try starting again
npm start
```

#### Issue: "Cannot connect to backend"

**Problem:** Backend server not running or wrong URL.

**Solution:**
```bash
# Check if backend is running (should show JSON response)
curl http://localhost:8001/docs

# If not running, start backend:
cd ../backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Check frontend environment (if exists)
cat .env.local  # Should have REACT_APP_API_URL if configured
```

### Database Issues

#### Issue: Database connection errors

**Problem:** Database file corrupted or missing.

**Solution:**
```bash
# Navigate to backend directory
cd backend

# Remove existing database (it will be recreated)
rm math_ai_agent.db  # macOS/Linux
del math_ai_agent.db # Windows

# Restart backend server (it will recreate the database)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### General Issues

#### Issue: Command not found errors

**Problem:** Required software not installed or not in PATH.

**Solutions:**

**For Python:**
```bash
# Try python3 instead of python
python3 --version

# Add to PATH (varies by system)
# On Windows: Add Python installation directory to PATH in System Properties
# On macOS: Add to ~/.bash_profile or ~/.zshrc
# On Linux: Usually installed correctly by package manager
```

**For Node.js:**
```bash
# Reinstall Node.js from nodejs.org
# Make sure to restart terminal after installation

# Check installation
which node  # macOS/Linux
where node  # Windows
```

#### Issue: Permission denied errors

**Solutions:**

**On macOS/Linux:**
```bash
# For pip installations
pip install --user -r requirements.txt

# For npm installations
sudo npm install

# For file operations
sudo chmod +x filename
```

**On Windows:**
```bash
# Run Command Prompt as Administrator
# Right-click Command Prompt -> "Run as administrator"
```

### Getting Help

#### Check Server Logs

**Backend logs:** Look at the terminal where you started uvicorn
**Frontend logs:** Look at the terminal where you started npm start

#### Verify Services are Running

```bash
# Check if backend is responding
curl http://localhost:8001/docs

# Check if frontend is responding
curl http://localhost:3000
```

#### Test Individual Components

```bash
# Test Python environment
cd backend
source venv/bin/activate
python -c "import fastapi; print('Backend OK')"

# Test Node.js environment
cd ../frontend
node -e "console.log('Frontend OK')"
```

---

## Quick Reference Commands

### Daily Development Workflow

**Starting the application:**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend
cd frontend
npm start

# Browser
# Open http://localhost:3000
```

**Stopping the application:**
```bash
# In each terminal, press:
Ctrl+C
```

### Useful Shortcuts

**Restart backend after code changes:**
- The `--reload` flag automatically restarts the server
- Just save your Python files and the server restarts

**Restart frontend after code changes:**
- React automatically reloads in the browser
- Just save your JavaScript/CSS files

**View logs:**
- Backend logs appear in the uvicorn terminal
- Frontend logs appear in the npm start terminal
- Browser console (F12) shows frontend JavaScript errors

---

**Need more help?** Check the main [README.md](README.md) for additional information or create an issue in the project repository.
