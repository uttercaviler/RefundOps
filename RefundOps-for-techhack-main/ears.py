import imaplib
import email
import time
import main

import config

# --- CONFIGURATION ---
EMAIL_USER = config.EMAIL_USER
EMAIL_PASS = config.EMAIL_PASS
IMAP_SERVER = config.IMAP_SERVER


def listen():
    print("EARS: Connected to Gmail. Waiting for emails...", flush=True)
    while True:
        try:
            # 1. Connect
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_USER, EMAIL_PASS)
            mail.select("inbox")
            
            # 2. Search for UNSEEN (unread) emails (Gmail IMAP expects 'UNSEEN')
            status, messages = mail.search(None, 'UNSEEN')
            
            # Simple log to show we are alive
            print(f"[{time.strftime('%H:%M:%S')}] Checked {EMAIL_USER} - Search Status: {status}", flush=True)

            email_ids = messages[0].split()
            if email_ids:
                print(f"EARS: Found {len(email_ids)} new UNREAD email(s)!", flush=True)
            else:
                print(f"No new unread emails found.", flush=True)


            if email_ids:
                # Loop through emails
                for e_id in email_ids:
                    # Fetch content
                    _, msg_data = mail.fetch(e_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject = msg["Subject"]
                            
                            # Extract Body
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode()
                                        print(f"Subject: {subject}", flush=True)
                                        
                                        # 3. TRIGGER THE AGENT
                                        main.process_refund_email(body)
            
            # Sleep to prevent spamming Gmail
            time.sleep(5)

        except Exception as e:
            error_msg = str(e)
            print(f"Connection Error: {error_msg}", flush=True)
            if "[AUTHENTICATIONFAILED]" in error_msg:
                print("\n!!! AUTHENTICATION ACTION REQUIRED !!!", flush=True)
                print("Google rejected your password.", flush=True)
                print("1. Ensure you are using an App Password (16 characters), NOT your normal Gmail password.", flush=True)
                print("2. Generate a NEW App Password here: https://myaccount.google.com/apppasswords", flush=True)
                print("3. Update the 'EMAIL_PASS' variable in 'config.py' with the new password.", flush=True)
                print("4. Restart the application.\n", flush=True)
                # Stop the loop to avoid spamming logs
                break
            time.sleep(5)

if __name__ == "__main__":
    listen()