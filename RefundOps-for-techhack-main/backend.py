from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import subprocess
import os
import signal
import sys
import glob
from collections import deque
import threading
import time
import database

# Initialize DB
database.init_db()

app = FastAPI()

# Global variable to keep track of the process and logs
ears_process = None
log_buffer = deque(maxlen=200)  # Store last 200 log lines

class LoginCredentials(BaseModel):
    # This now effectively acts as "username" and "password" for the dashboard
    # But for backward compatibility with the frontend field names, we might keep email/password
    # OR better, we use username/password
    username: str
    password: str

class SignUpCredentials(BaseModel):
    username: str
    password: str
    gmail_email: str
    gmail_app_pass: str

def read_process_output(process):
    """
    Reads stdout/stderr from the subprocess and appends to log_buffer.
    """
    try:
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                if line:
                    log_buffer.append(line.strip())
                else:
                    break
    except Exception as e:
        log_buffer.append(f"LOGGING ERROR: {e}")

@app.post("/signup")
def signup(credentials: SignUpCredentials):
    # Sanitize app password (remove spaces)
    credentials.gmail_app_pass = credentials.gmail_app_pass.replace(" ", "")
    
    success, msg = database.create_user(
        credentials.username, 
        credentials.password, 
        credentials.gmail_email, 
        credentials.gmail_app_pass
    )
    if success:
        return {"status": "success", "message": "User created successfully"}
    else:
        raise HTTPException(status_code=400, detail=msg)

@app.post("/login")
def login(credentials: LoginCredentials):
    """
    Verifies user against DB. If valid, updates config.py with their stored Gmail creds.
    """
    print(f"LOGIN ATTEMPT: Username='{credentials.username}'", flush=True)
    valid, gmail, app_pass = database.verify_user(credentials.username, credentials.password)
    
    if not valid:
        print(f"LOGIN FAILED: Invalid credentials for '{credentials.username}'", flush=True)
        # Fallback for "legacy" mode where user might just be typing raw gmail/pass?
        # Only if it looks like an email and 16 char pass. But let's enforce DB for new flow.
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Sanitize app password (remove spaces) just in case DB has spaces
    if app_pass:
        app_pass = app_pass.replace(" ", "")
    
    print(f"LOGIN SUCCESS: '{credentials.username}'", flush=True)

    try:
        config_content = f'''# --- CONFIGURATION (Auto-generated for {credentials.username}) ---
EMAIL_USER = "{gmail}"
EMAIL_PASS = "{app_pass}"
IMAP_SERVER = "imap.gmail.com"
'''
        with open("config.py", "w") as f:
            f.write(config_content)
        return {"status": "success", "message": "Login successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    global ears_process
    if ears_process and ears_process.poll() is None:
        return {"running": True}
    return {"running": False}

@app.get("/logs")
def get_logs():
    return {"logs": list(log_buffer)}

@app.get("/stats")
def get_stats_endpoint():
    return database.get_stats()

@app.post("/start")
def start_ears():
    global ears_process
    if ears_process and ears_process.poll() is None:
        return {"status": "already_running", "message": "Ears are already listening"}
    
    try:
        # Start ears.py as a subprocess using the current venv python
        # Redirect stdout and stderr to PIPE so we can capture it
        python_executable = sys.executable
        
        # Use unbuffered output (-u) to get logs instantly
        ears_process = subprocess.Popen(
            [python_executable, "-u", "ears.py"], 
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr into stdout
            text=True,
            bufsize=1, # Line buffered
            encoding='utf-8' # Ensure UTF-8
        )
        
        # Start a thread to read logs
        t = threading.Thread(target=read_process_output, args=(ears_process,))
        t.daemon = True
        t.start()
        
        return {"status": "success", "message": "Ears started listening"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stop")
def stop_ears():
    global ears_process
    if ears_process and ears_process.poll() is None:
        ears_process.terminate()
        try:
             ears_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
             ears_process.kill()
        ears_process = None
        return {"status": "success", "message": "Ears stopped listening"}
    return {"status": "not_running", "message": "Ears are not running"}

@app.get("/screenshots")
def get_screenshots():
    # List all png files in current directory
    files = glob.glob("*.png")
    # Sort by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return {"screenshots": files}
