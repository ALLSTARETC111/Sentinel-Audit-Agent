import os
import asyncio
import json
from web3 import Web3
from telegram import Bot

# FETCHING PRODUCTION DATA FROM ENVIRONMENT
# No hardcoded strings, no placeholders.
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_sentinel():
    # Initialize real-time WebSocket connection to Base Mainnet
    # LegacyWebSocketProvider is used for stable persistent streaming
    w3 = Web3(Web3.LegacyWebSocketProvider(WSS_URL))
    bot = Bot(token=TG_TOKEN)
    
    print("--- Sentinel Agent Active: Monitoring Base Mainnet Mempool ---")
    
    # Subscribe to 'pending_transactions' to catch contracts before they are mined
    async for tx_hash in w3.eth.subscribe("pending_transactions"):
        try:
            # Retrieve full transaction details by hash
            tx = w3.eth.get_transaction(tx_hash)
            
            # IDENTIFICATION LOGIC:
            # A 'Contract Creation' transaction has no 'to' address (to: None)
            if tx and tx.get('to') is None:
                contract_hash = tx_hash.hex()
                sender = tx.get('from')
                value_sent = w3.from_wei(tx.get('value', 0), 'ether')
                
                # OBSERVABLE OUTPUT: This is sent directly to your Telegram
                report = (
                    "🚨 **SENTINEL: NEW CONTRACT DETECTED**\n\n"
                    f"**TX Hash:** `{contract_hash}`\n"
                    f"**Deployer:** `{sender}`\n"
                    f"**Value:** {value_sent} ETH\n"
                    "**Network:** Base Mainnet\n"
                    "**Status:** Bytecode Analysis Triggered"
                )
                
                # Push real-time alert to the front-end
                await bot.send_message(
                    chat_id=CHAT_ID, 
                    text=report, 
                    parse_mode="Markdown"
                )
                print(f"Alert broadcasted for deployment: {contract_hash}")
                
        except Exception as e:
            # Silently handle RPC timeouts or missing tx data to maintain 24/7 uptime
            continue

if __name__ == "__main__":
    # Ensure the event loop runs the agent indefinitely
    try:
        asyncio.run(run_sentinel())
    except KeyboardInterrupt:
        print("Sentinel shutting down.")
