import os
import asyncio
from web3 import Web3
from telegram import Bot

# PRODUCTION CONFIGURATION
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Known Liquidity Router Address (Uniswap V2/Base Swap)
ROUTER_ADDRESS = "0x4752ba5DBc23f44D82143D093042C01768afc35E" 

async def run_sentinel():
    w3 = Web3(Web3.LegacyWebSocketProvider(WSS_URL))
    bot = Bot(token=TG_TOKEN)
    
    print("--- Sentinel Active: Monitoring Audit & Liquidity Events ---")
    
    async for tx_hash in w3.eth.subscribe("pending_transactions"):
        try:
            tx = w3.eth.get_transaction(tx_hash)
            if not tx: continue

            # 1. AUDIT LOGIC: Detect New Contract Creation
            if tx.get('to') is None:
                msg = f"🚨 **NEW CONTRACT DETECTED**\nHash: `{tx_hash.hex()}`\nStatus: *Auditing Bytecode...*"
                await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

            # 2. LIQUIDITY LOGIC: Detect 'Add Liquidity' calls to the Router
            elif tx.get('to').lower() == ROUTER_ADDRESS.lower():
                # Check if the transaction data starts with the 'addLiquidity' method ID
                if tx.get('input', '').hex().startswith('0xf305639b'): 
                    lp_msg = (
                        "💰 **LIQUIDITY ADDED!**\n"
                        f"**TX:** `{tx_hash.hex()}`\n"
                        "**Action:** Trade Window Opening Now."
                    )
                    await bot.send_message(chat_id=CHAT_ID, text=lp_msg, parse_mode="Markdown")
                
        except Exception:
            continue

if __name__ == "__main__":
    asyncio.run(run_sentinel())
