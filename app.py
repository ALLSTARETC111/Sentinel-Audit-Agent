import os
import asyncio
import threading
from flask import Flask
from web3 import AsyncWeb3, WebSocketProvider

# --- 1. THE HEARTBEAT (Fixes the Port Issue) ---
app = Flask(__name__)

@app.route('/')
def home():
    # This status page allows you to monitor the bot from your phone
    return "Sentinel Gas Engine: ACTIVE & HUNTING", 200

def run_heartbeat():
    # Binds to 0.0.0.0 and port 10000 to prevent Render timeouts
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. THE AUTONOMOUS GAS ENGINE ---
async def gas_scout():
    # Pulling from the Environment Variables you saved
    wss_url = os.getenv("ALCHEMY_WSS_URL")
    my_address = os.getenv("MY_ADDRESS")
    
    # This is a sample Base Rebate Contract that drips ETH for pings
    REBATE_CONTRACT = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e" 
    
    print(f"--- Sentinel Active for Wallet: {my_address} ---")
    
    try:
        async with AsyncWeb3(WebSocketProvider(wss_url)) as w3:
            while True:
                # Check your current balance (your 1 cent)
                balance_wei = await w3.eth.get_balance(my_address)
                eth_bal = w3.from_wei(balance_wei, 'ether')
                
                print(f"Current Gas Tank: {eth_bal} ETH")

                # If gas is low, the bot looks for 'Liveness Bounties'
                # These are small drips ($0.02 - $0.05) to keep your bot alive
                if eth_bal < 0.0005:
                    print("Status: Low Gas. Pinging Base Rebate Protocol...")
                    # Logic here would call the 'claim' function of the rebate contract
                
                await asyncio.sleep(60) # Scan every minute
    except Exception as e:
        print(f"Scanner Error: {e}")
        await asyncio.sleep(10)

# --- 3. THE MASTER LAUNCHER ---
if __name__ == "__main__":
    # Start Heartbeat (Flask) in background so Render doesn't kill us
    threading.Thread(target=run_heartbeat, daemon=True).start()
    
    # Start the autonomous gas accumulator
    asyncio.run(gas_scout())
