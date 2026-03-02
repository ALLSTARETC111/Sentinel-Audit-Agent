import os
import json
import asyncio
import requests
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from flask import Flask

# Health check server for Render
app = Flask(__name__)

@app.route('/')
def health():
    return "Bot Active", 200

# Strict Environment Configuration
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
MY_ADDR = os.getenv("MY_ADDRESS")
SIGNER_KEY = os.getenv("RELAY_SIGNER_KEY")
RELAY_URL = "https://relay.flashbots.net" # 2026 Production Endpoint

async def monitor_mempool():
    """
    Scans Base mempool for high-value transactions and 
    dispatches signed signals to the private relay.
    """
    # Connect via Alchemy WebSocket
    w3 = Web3(Web3.LegacyWebSocketProvider(WSS_URL))
    
    # Subscribe to pending transactions
    async for tx_hash in w3.eth.filter('pending').get_new_entries():
        try:
            tx = await w3.eth.get_transaction(tx_hash)
            
            # Searcher Logic: Detect trades over 1.2 ETH
            if tx and tx['value'] > w3.to_wei(1.2, 'ether'):
                signal = {
                    "method": "eth_sendPrivateSignal",
                    "params": {
                        "tx_hash": tx_hash.hex(),
                        "searcher": MY_ADDR
                    }
                }
                
                # Digital Signature using the RELAY_SIGNER_KEY
                message = json.dumps(signal)
                signature = Account.sign_message(
                    encode_defunct(text=message), 
                    private_key=SIGNER_KEY
                )
                
                # Dispatching to Flashbots Relay
                requests.post(
                    RELAY_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "eth_sendPrivateSignal",
                        "params": [signal, signature.signature.hex()]
                    },
                    timeout=1
                )
                
        except Exception:
            continue
        
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    # Start mempool scouter in the background
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_mempool())
    
    # Start web server on Render port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
