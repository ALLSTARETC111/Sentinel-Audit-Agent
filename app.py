import os
import json
import asyncio
import requests
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def health():
    return "Bot Operational", 200

WSS_URL = os.getenv("ALCHEMY_WSS_URL")
MY_ADDR = os.getenv("MY_ADDRESS")
SIGNER_KEY = os.getenv("RELAY_SIGNER_KEY")
RELAY_URL = "https://rpc.flashbots.net"

async def scout_mempool():
    try:
        w3 = Web3(Web3.LegacyWebSocketProvider(WSS_URL))
        async for tx_hash in w3.eth.filter('pending').get_new_entries():
            try:
                tx = await w3.eth.get_transaction(tx_hash)
                if tx and tx['value'] > w3.to_wei(1, 'ether'):
                    signal = {
                        "method": "eth_sendPrivateSignal",
                        "params": {"tx": tx_hash.hex(), "finder": MY_ADDR}
                    }
                    message = json.dumps(signal)
                    signed = Account.sign_message(encode_defunct(text=message), private_key=SIGNER_KEY)
                    requests.post(RELAY_URL, json={
                        "jsonrpc": "2.0", "id": 1, 
                        "method": "eth_sendPrivateSignal",
                        "params": [signal, signed.signature.hex()]
                    }, timeout=1)
            except:
                continue
    except Exception as e:
        print(f"Error: {e}")

def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scout_mempool())

if __name__ == "__main__":
    daemon = Thread(target=run_async_loop, daemon=True)
    daemon.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
