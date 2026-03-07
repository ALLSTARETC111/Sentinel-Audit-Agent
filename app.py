import os
import asyncio
import threading
import json
import time
from flask import Flask
from web3 import Web3
from eth_account import Account
from websockets import connect
import requests

app = Flask(__name__)

# --- CONFIGURATION (Environment Variables) ---
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
HTTP_URL = os.getenv("ALCHEMY_HTTP_URL")
SIGNER_KEY = os.getenv("RELAY_SIGNER_KEY")
REFUND_ADDR = os.getenv("MY_ADDR")
THRESHOLD = float(os.getenv("MIN_TRADE_THRESHOLD", 1.0))
RELAY_URL = "https://relay.flashbots.net/api/v1/alerts"

w3 = Web3(Web3.HTTPProvider(HTTP_URL))
signer_account = Account.from_key(SIGNER_KEY)

async def send_to_relay_fast_path(tx_hash, value_eth):
    """The 'Spicy' Priority Signal Logic"""
    try:
        # Calculate urgency (1-100) based on whale size
        urgency = min(int((value_eth / THRESHOLD) * 10), 100)
        
        # 2026 MEV-Share Payload
        payload = {
            "method": "mev_sendBundle",
            "params": [{
                "txs": [tx_hash],
                "blockNumber": hex(w3.eth.block_number + 1),
                "minTimestamp": int(time.time()),
                "maxTimestamp": int(time.time()) + 60,
            }],
            "id": 1,
            "jsonrpc": "2.0"
        }

        # Sign the body for Reputation/Identity
        body = json.dumps(payload)
        signature = signer_account.address + ":" + signer_account.sign_message(
            Account._message_from_string(body)
        ).signature.hex()

        headers = {
            "X-Flashbots-Signature": signature,
            "X-Flashbots-Auction-Priority": str(urgency),
            "X-Region-Depth": "Global",
            "Content-Type": "application/json"
        }

        # Non-blocking fire-and-forget
        requests.post(RELAY_URL, data=body, headers=headers, timeout=0.5)
        print(f"🔥 [SPICY SIGNAL SENT]: {tx_hash} | Urgency: {urgency}")
    except Exception as e:
        print(f"❌ Relay Error: {e}")

async def run_scout():
    """Main Persistence Loop & Threshold Filter"""
    async for websocket in connect(WSS_URL):
        try:
            # Subscribe to Base Pending Transactions
            subscribe_msg = {
                "jsonrpc":"2.0", "id": 1, 
                "method": "eth_subscribe", 
                "params": ["alchemy_pendingTransactions"]
            }
            await websocket.send(json.dumps(subscribe_msg))
            print(f"✅ LIVENESS: Scout Active | Threshold: {THRESHOLD} ETH")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if "params" in data:
                    tx = data["params"]["result"]
                    # Extract value from hex
                    raw_val = tx.get('value', '0x0')
                    value_in_eth = float(w3.from_wei(int(raw_val, 16), 'ether'))
                    
                    # THE THRESHOLD FILTER
                    if value_in_eth >= THRESHOLD:
                        tx_hash = tx.get('hash')
                        print(f"💰 [WHALE]: {value_in_eth} ETH detected.")
                        # Trigger the spicy fast-path signal
                        asyncio.create_task(send_to_relay_fast_path(tx_hash, value_in_eth))
                    
        except Exception as e:
            print(f"⚠️ Connection Reset: {e}. Retrying...")
            await asyncio.sleep(5)

def start_background_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_scout())

# Multi-threaded launch to prevent Gunicorn timeout
threading.Thread(target=start_background_loop, daemon=True).start()

@app.route('/')
def health():
    return {
        "status": "Operational",
        "network": "Base",
        "reputation_tier": "Building",
        "active_threshold": THRESHOLD
    }, 200

if __name__ == "__main__":
    # Local only; Gunicorn uses 'app'
    app.run(host='0.0.0.0', port=10000)
