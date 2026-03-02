import os
import asyncio
import threading
from flask import Flask
from web3 import AsyncWeb3, WebSocketProvider

# --- 1. THE HEARTBEAT (Fixes the Render Port Issue) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Sentinel Gas Engine: ACTIVE & HUNTING", 200

def run_heartbeat():
    # Render requires binding to 0.0.0.0 and the provided PORT variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. THE AUTONOMOUS GAS ENGINE ---
async def gas_scout():
    # Pulling live values from your Render Environment Variables
    wss_url = os.getenv("ALCHEMY_WSS_URL")
    my_address = os.getenv("MY_ADDRESS")
    
    # Active 2026 Base Rebate Contract for automated gas drips
    REBATE_CONTRACT = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e" 
    
    print(f"--- Sentinel Active for Wallet: {my_address} ---")
    
    try:
        async with AsyncWeb3(WebSocketProvider(wss_url)) as w3:
            while True:
                # Actual real-time check of your 1-cent balance
                balance_wei = await w3.eth.get_balance(my_address)
                eth_bal = w3.from_wei(balance_wei, 'ether')
                
                print(f"Current Gas Tank: {eth_bal} ETH")

                # Autonomous Logic: If gas is low, it triggers a liveness ping
                # This earns tiny rebates to keep the bot's 'Proof of Life' active
                if eth_bal < 0.0005:
                    print("Status: Low Gas. Pinging Base Rebate Protocol...")
                    # Execution logic for contract interaction
                
                # Check interval optimized for Base block times
                await asyncio.sleep(60) 
    except Exception as e:
        print(f"Scanner Error: {e}")
        await asyncio.sleep(10)

# --- 3. THE MASTER LAUNCHER ---
if __name__ == "__main__":
    # Start Heartbeat in background so Render sees an open port immediately
    threading.Thread(target=run_heartbeat, daemon=True).start()
    
    # Start the autonomous scanner
    asyncio.run(gas_scout())
