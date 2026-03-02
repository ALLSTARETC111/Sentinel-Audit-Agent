import os
import requests
import json
from web3 import Web3

# 1. SETUP: Connection to the Base-Flashbots Relay (2026 Endpoint)
# You will need to add 'RELAY_SIGNER_KEY' to your Render Env Vars
RELAY_URL = "https://base-relay.flashbots.net"
RELAY_SIGNER_KEY = os.getenv("RELAY_SIGNER_KEY") # A separate private key for signing signals

def send_to_private_relay(opportunity_data):
    """
    Sends the detected arbitrage or MEV signal to the private relay
    to claim the Finder's Fee.
    """
    w3 = Web3()
    
    # Create a 'Signature' to prove you are the Searcher who found this
    # This ensures the Finder's Fee is sent to YOUR wallet
    message = json.dumps(opportunity_data)
    signature = w3.eth.account.sign_message(
        encode_defunct(text=message), 
        private_key=RELAY_SIGNER_KEY
    )

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_sendPrivateSignal",
        "params": [
            opportunity_data,
            signature.signature.hex()
        ]
    }

    try:
        response = requests.post(RELAY_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ [RELAY]: Signal accepted. Potential Bounty: {opportunity_data['estimated_bounty']} ETH")
        else:
            print(f"❌ [RELAY]: Signal rejected. Reason: {response.text}")
    except Exception as e:
        print(f"⚠️ [RELAY]: Connection Error: {e}")

# Example of the 'Opportunity Data' your Searcher Logic will generate
example_opportunity = {
    "target_contract": "0xAerodrome_Pool_Address",
    "profit_gap": "0.012 ETH",
    "estimated_bounty": "0.003 ETH", # Your 25% Finder's Fee
    "searcher_address": os.getenv("MY_ADDRESS")
}

# To activate, you would call:
# send_to_private_relay(example_opportunity)
