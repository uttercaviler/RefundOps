import brain
import bot

def process_refund_email(email_body):
    print("\n------------------------------------", flush=True)
    print("MAIN: Processing new email...", flush=True)
    
    # Step 1: Ask Brain to analyze text
    data = brain.get_flight_data(email_body)
    
    if data:
        pnr = data.get("pnr")
        airline = data.get("airline")
        customer_name = data.get("customer_name")
        
        print(f"ANALYSIS COMPLETE: Airline='{airline}' | PNR='{pnr}' | Name='{customer_name}'", flush=True)
        
        # Step 2: Route to the correct bot (case-insensitive check)
        airline_lower = airline.lower() if airline else ""
        
        if "indigo" in airline_lower or "6e" in airline_lower:
            print("Routing to INDIGO Agent...", flush=True)
            bot.start_indigo_process(pnr, customer_name)
            
        elif "air india" in airline_lower:
            print("Routing to AIR INDIA Agent...", flush=True)
            bot.start_airindia_process(pnr, customer_name)
            
        else:
            print(f"Error: We do not support '{airline}' yet.", flush=True)
            
    else:
        print("Error: Brain could not understand the email.", flush=True)

# Optional: Test manually
if __name__ == "__main__":
    test_email = "Please cancel my Air India flight. PNR is AI-TEST-99."
    process_refund_email(test_email)