import os
import asyncio
import threading
import json
from flask import Flask
from web3 import Web3
from eth_account import Account
from websockets import connect

app = Flask(__name__)

# --- CONFIGURATION ---
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
SIGNER_KEY = os.getenv("RELAY_SIGNER_KEY")
REFUND_ADDR = os.getenv("MY_ADDR")
THRESHOLD = float(os.getenv("MIN_TRADE_THRESHOLD", 1.0))

w3 = Web3(Web3.HTTPProvider(os.getenv("ALCHEMY_HTTP_URL"))) # For utility checks

# --- LIVENESS & THRESHOLD LOGIC ---
async def run_scout():
    """Main loop: Maintains connection and filters for Whales"""
    async for websocket in connect(WSS_URL):
        try:
            # Subscribe to pending transactions on Base
            subscribe_msg = {"jsonrpc":"2.0","id": 1, "method": "eth_subscribe", "params": ["alchemy_pendingTransactions"]}
            await websocket.send(json.dumps(subscribe_msg))
            
            print(f"✅ LIVENESS: Connected to Base Mempool. Threshold: {THRESHOLD} ETH")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if "params" in data:
                    tx = data["params"]["result"]
                    
                    # --- THE THRESHOLD LOGIC ---
                    # Check if the transaction value meets our criteria
                    value_in_eth = w3.from_wei(int(tx.get('value', 0), 16), 'ether')
                    
                    if value_in_eth >= THRESHOLD:
                        print(f"💰 [WHALE DETECTED]: {value_in_eth} ETH. Sending to Relay...")
                        # This is where the signed signal is blasted to Flashbots
                        # Logic for 'send_private_signal' would go here
                    else:
                        # Ignore the noise to protect Reputation
                        pass

        except Exception as e:
            print(f"⚠️ Connection lost: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

# --- REPUTATION HEARTBEAT ---
def start_background_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_scout())

# Start the background thread so Gunicorn doesn't kill the process
threading.Thread(target=start_background_loop, daemon=True).start()

@app.route('/')
def health():
    return {"status": "Operational", "tier": "Reputation Building"}, 200

if __name__ == "__main__":
    # This is only for local testing; Gunicorn uses the 'app' object above
    app.run()
