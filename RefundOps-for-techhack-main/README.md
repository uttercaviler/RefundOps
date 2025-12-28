# ✈️ RefundOps

**RefundOps** is an intelligent, AI-powered automation system designed to streamline the airline ticket refund process. It acts as a "Command Center" that listens for refund request emails, parses them using Google's Gemini AI, and autonomously executes the refund procedure on airline portals using Playwright.

![RefundOps Dashboard](https://via.placeholder.com/800x400?text=RefundOps+Dashboard+Mockup)
*(Replace with actual screenshot if available)*

## 🌟 Features

- **📧 Smart Email Listening**: Continuously monitors a dedicated Gmail inbox for refund-related emails using IMAP.
- **🧠 AI-Powered Analysis**: Utilizes **Google Gemini AI** (`brain.py`) to intelligently extract booking details (PNR, Flight No, Passenger Name) from unstructured email text.
- **🤖 Autonomous Execution**: automatically navigates airline websites (e.g., Indigo, Air India) using **Playwright** to initiate and process cancelations/refunds.
- **💻 Modern Command Center**: A sleek **Streamlit** dashboard for real-time monitoring.
  - **Live Terminal Logs**: Watch the bot "think" and act in real-time.
  - **Visual Evidence**: View live screenshots of the bot's interactions with airline sites.
  - **Metrics**: Track money saved, time saved, and total refunds processed.
- **🔐 Secure Authentication**: Includes a secure signup/login system to manage bot credentials.

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **Automation**: [Playwright](https://playwright.dev/)
- **AI/LLM**: [Google Gemini (Generative AI)](https://ai.google.dev/)
- **Database**: SQLite
- **Protocol**: IMAP (for email)

## 📂 Project Structure

```bash
RefundOps/
├── backend.py          # FastAPI server handling API requests & process management
├── frontend.py         # Streamlit dashboard interface
├── bot.py              # Playwright automation logic for airline sites
├── ears.py             # Email listener service
├── brain.py            # AI logic utilizing Google Gemini
├── database.py         # SQLite database interactions
├── config.py           # Configuration file (auto-generated on login)
├── requirements.txt    # Project dependencies
└── run_app.bat         # One-click startup script (Windows)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher installed.
- A Google Cloud API Key for Gemini.
- A Gmail account with **App Password** enabled (for the bot to read emails).

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/refundops.git
   cd refundops
   ```

2. **Create a virtual environment (Optional but Recommended)**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers**
   ```bash
   playwright install
   ```

### Running the Application

**Option 1: Windows Retrieval (Easy)**
Simply double-click `run_app.bat` or run it from the terminal:
```bash
run_app.bat
```

**Option 2: Manual Start**
1. **Start the Backend:**
   ```bash
   uvicorn backend:app --reload --port 8000
   ```
2. **Start the Frontend (New Terminal):**
   ```bash
   streamlit run frontend.py
   ```

## 🎮 Usage Guide

1. Open your browser to the URL shown by Streamlit (usually `http://localhost:8501`).
2. **Sign Up / Login**: Create a user account. You will need to provide your Gmail address and an **App Password** (not your regular password).
3. **Start the Agent**: Click the "▶ START AGENT" button in the dashboard.
4. **Monitor**: Watch the logs and screenshots as the bot detects emails and processes refunds!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
