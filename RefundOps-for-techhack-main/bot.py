from playwright.sync_api import sync_playwright
import time
import os
import database

# --- 1. INDIGO PROCESS ---
def start_indigo_process(pnr_number, customer_name):
    print(f"INDIGO BOT: Opening local portal for PNR {pnr_number}...", flush=True)
    run_local_bot("indigo.html", pnr_number, "Indigo", customer_name)

# --- 2. AIR INDIA PROCESS ---
def start_airindia_process(pnr_number, customer_name):
    print(f"AIR INDIA BOT: Opening local portal for PNR {pnr_number}...", flush=True)
    run_local_bot("airindia.html", pnr_number, "Air India", customer_name)

# --- SHARED LOGIC (The "Smart" Function) ---
def run_local_bot(filename, pnr, airline_name, customer_name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Headless=False so you see it
        page = browser.new_page()
        
        # 1. Load the Local File
        file_path = os.path.abspath(filename)
        if not os.path.exists(file_path):
            print(f"ERROR: Could not find '{filename}' in the folder.")
            print(f"Please rename your downloaded HTML file to '{filename}'")
            browser.close()
            return

        try:
            page.goto(f"file://{file_path}", wait_until="domcontentloaded", timeout=10000)
            print(f"Loaded {airline_name} portal.", flush=True)
        except Exception as e:
            print(f"Warning: Page load timed out or had issues: {e}", flush=True)
            print("Proceeding anyway...", flush=True)

        try:
            # 2. Fill form fields
            print("Filling Form Details...", flush=True)
            
            # Wait for page to be ready
            time.sleep(2)

            # Air India Specifics: Scroll and Accept Cookies
            if airline_name == "Air India":
                try:
                    # Scroll down a bit
                    page.mouse.wheel(0, 300)
                    time.sleep(1)
                    
                    # Click "Accept All" for cookies
                    try:
                        # Try finding by ID first (most reliable)
                        page.locator("#accept-cookies-btn").wait_for(state="visible", timeout=3000)
                        page.locator("#accept-cookies-btn").click()
                        print("Clicked 'Accept All' cookies (ID method).", flush=True)
                    except Exception:
                        # Fallback to text
                        print("ID method failed for cookies, trying text...", flush=True)
                        accept_btn = page.get_by_text("Accept All", exact=False).first
                        if accept_btn.is_visible():
                            accept_btn.click()
                            print("Clicked 'Accept All' cookies (Text method).", flush=True)
                    
                    time.sleep(1)
                except Exception as e:
                    print(f"Air India specific setup failed: {e}", flush=True)

            # Fill PNR
            # Fill PNR
            try:
                page.locator('[name="pnr-booking-ref"]').wait_for(state="visible", timeout=2000)
                page.locator('[name="pnr-booking-ref"]').press_sequentially(pnr, delay=100)
                print(f"Filled PNR: {pnr}", flush=True)
            except Exception:
                try:
                    page.locator("#pnr").wait_for(state="visible", timeout=2000)
                    page.locator("#pnr").press_sequentially(pnr, delay=100)
                    print(f"Filled PNR: {pnr}", flush=True)
                except Exception:
                    try:
                        # Air India new selector
                        page.locator("#pnr-input").wait_for(state="visible", timeout=2000)
                        page.locator("#pnr-input").press_sequentially(pnr, delay=100)
                        print(f"Filled PNR (Air India): {pnr}", flush=True)
                    except Exception as e3:
                        print(f"Could not find PNR field: {e3}", flush=True)

            # Fill Email/Last Name
            try:
                page.locator('[name="email-last-name"]').wait_for(state="visible", timeout=2000)
                page.locator('[name="email-last-name"]').press_sequentially(customer_name, delay=100)
                print(f"Filled Email/Last Name: {customer_name}", flush=True)
            except Exception:
                try:
                    page.locator("#email").wait_for(state="visible", timeout=2000)
                    page.locator("#email").press_sequentially(customer_name, delay=100) # Assuming email fallback is handled or name is email
                    print(f"Filled Email: {customer_name}", flush=True)
                except Exception:
                    try:
                        # Air India new selector
                        page.locator("#lastname-input").wait_for(state="visible", timeout=2000)
                        # Extract last name for Air India if full name is provided
                        last_name = customer_name.split()[-1] if customer_name else "Unknown"
                        page.locator("#lastname-input").press_sequentially(last_name, delay=100)
                        print(f"Filled Last Name (Air India): {last_name}", flush=True)
                    except Exception:
                        try:
                            # Indigo new selector
                            page.locator("#lastname").wait_for(state="visible", timeout=2000)
                            # Extract last name for Indigo if full name is provided
                            last_name = customer_name.split()[-1] if customer_name else "Unknown"
                            page.locator("#lastname").press_sequentially(last_name, delay=100)
                            print(f"Filled Last Name (Indigo): {last_name}", flush=True)
                        except Exception as e3:
                            print(f"Could not find Email/Last Name field: {e3}", flush=True)

            # 3. Handle Form Submission (Different for Step 1 vs Step 2)
            print("Submitting Form...", flush=True)
            time.sleep(1)

            if airline_name == "Indigo":
                try:
                    # Step 1: Click "Get Booking Details" (Next)
                    print("Indigo Step 1: Getting Booking...", flush=True)
                    page.locator("#nextBtn").click()
                    
                    # Wait for Step 2 to appear (simulation delay + transition)
                    try:
                        page.locator("#step-2").wait_for(state="visible", timeout=5000)
                        print("Indigo Step 2: Options loaded.", flush=True)
                    except:
                        print("Warning: Step 2 did not appear.", flush=True)

                    # Step 2a: Select Reason (Slower interaction)
                    page.locator("#refund-reason").focus() # Highlight it first
                    time.sleep(1) # Let user see it
                    page.locator("#refund-reason").select_option("cancelled")
                    print("Selected Reason: Flight Cancelled", flush=True)
                    time.sleep(1.5) # Let user read the selection

                    # Step 2b: Type Remarks
                    remarks_text = f"Automated refund request for PNR {pnr}. Flight cancelled by airline."
                    page.locator("#refund-remarks").press_sequentially(remarks_text, delay=50)
                    print(f"Typed Remarks: {remarks_text}", flush=True)
                    time.sleep(1)

                    # Step 2c: Select "Back to Source" (Slower)
                    page.locator("#refund-mode").focus()
                    time.sleep(0.5)
                    page.locator("#refund-mode").select_option("original")
                    print("Selected: Refund to Bank Source", flush=True)
                    time.sleep(1)

                    # Step 3: Check Terms
                    page.locator("#terms-check").check()
                    print("Checked: Terms & Conditions", flush=True)
                    time.sleep(1)

                    # Step 4: Final Submit
                    page.locator("#submitBtn").click()
                    print("Clicked: Confirm Refund", flush=True)

                except Exception as e:
                    print(f"Indigo specific flow failed: {e}", flush=True)
            
            elif airline_name == "Air India":
                try:
                    # Step 1: Click "Retrieve Booking" (Next)
                    print("Air India Step 1: Retrieving Booking...", flush=True)
                    page.locator("#nextBtn").click()

                    # Wait for Step 2
                    try:
                        page.locator("#step-2").wait_for(state="visible", timeout=5000)
                        print("Air India Step 2: Options loaded.", flush=True)
                    except:
                        print("Warning: Step 2 did not appear.", flush=True)

                    # Step 2a: Select Reason (Slower interaction)
                    page.locator("#refund-reason").focus()
                    time.sleep(1)
                    page.locator("#refund-reason").select_option("cancelled")
                    print("Selected Reason: Flight Cancelled", flush=True)
                    time.sleep(1.5)

                    # Step 2b: Type Remarks (The visual "wow" factor)
                    remarks_text = f"Automated refund request for PNR {pnr}. Flight cancelled by airline."
                    page.locator("#refund-remarks").press_sequentially(remarks_text, delay=50)
                    print(f"Typed Remarks: {remarks_text}", flush=True)
                    time.sleep(1)

                    # Step 2c: Select "Original Payment Source"
                    page.locator("#refund-mode").focus()
                    time.sleep(0.5)
                    page.locator("#refund-mode").select_option("original")
                    print("Selected: Original Payment Source", flush=True)
                    time.sleep(1)

                    # Step 3: Check Terms
                    page.locator("#terms-check").check()
                    print("Checked: Refund Policy", flush=True)
                    time.sleep(1)

                    # Step 4: Final Submit
                    page.locator("#submitBtn").click()
                    print("Clicked: Confirm Refund", flush=True)

                except Exception as e:
                    print(f"Air India specific flow failed: {e}", flush=True)
            
            else:
                # Generic fallback (Just in case)
                try:
                    clicked = False
                    # Try ID first
                    btn = page.locator("#submitBtn")
                    if btn.is_visible():
                        btn.click()
                        clicked = True
                    else:
                        # Try finding by text
                        for text in ["Submit", "Next", "Retrieve Booking", "Search", "Check Status", "Get Refund"]:
                            try:
                                btn = page.get_by_text(text, exact=False).first
                                if btn.is_visible():
                                    print(f"Found button with text: {text}", flush=True)
                                    btn.click()
                                    clicked = True
                                    break
                            except:
                                continue
                        
                        if not clicked:
                            # Fallback to JS by ID
                            page.evaluate("document.getElementById('submitBtn').click()")
                            clicked = True

                except Exception as e:
                    print(f"Generic submit failed: {e}", flush=True) 

            # Wait for navigation/action
            time.sleep(2)
            
            # Check if we need to manually navigate to success page
            # If URL didn't change (still on local file), load success page
            current_url = page.url
            if "success" not in current_url:
                print("Navigating to success page manually...", flush=True)
                success_filename = f"{airline_name.lower()}_success.html".replace(" ", "")
                success_path = os.path.abspath(success_filename)
                if os.path.exists(success_path):
                    page.goto(f"file://{success_path}")
                    print(f"Manually navigated to {success_filename}", flush=True)
                else:
                    print(f"Success file not found: {success_filename}")
                
                time.sleep(3)

            # 4. SUCCESS SCREENSHOT
            time.sleep(2)
            screenshot_name = f"{airline_name.lower()}_success.png"
            page.screenshot(path=screenshot_name)
            print(f"Success! Screenshot saved: {screenshot_name}")
            
            # Update Statistics
            database.increment_refund_count()

        except Exception as e:
            print(f"Error on {airline_name} page: {e}")
        
        browser.close()
        