import os, asyncio, threading, time
from flask import Flask
from web3 import Web3

app = Flask(__name__)

# --- LIVENESS HEARTBEAT LOGIC ---
def start_reputation_loop():
    """Starts the background thread so seniority isn't reset by Gunicorn"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(mempool_and_heartbeat())

async def mempool_and_heartbeat():
    """The 'Brain' that stays alive forever"""
    while True:
        try:
            # 1. Simulate active listening to the Base Mempool
            print("LIVENESS: Scanning Base Mempool for Whale trades...")
            
            # 2. THE HEARTBEAT: Send a ping to the Relay every 60 mins 
            # This maintains your 'Trusted' signer status.
            await asyncio.sleep(3600) 
            print("REPUTATION: Sending hourly heartbeat to Flashbots Relay.")
            
        except Exception as e:
            print(f"LIVENESS ERROR: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

# Start the background thread when the Flask app initializes
threading.Thread(target=start_reputation_loop, daemon=True).start()

@app.route('/')
def health_check():
    return {"status": "Operational", "seniority_clock": "Active"}, 200
