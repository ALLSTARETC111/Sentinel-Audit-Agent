import os
import asyncio
from web3 import AsyncWeb3, WebSocketProvider
from telegram import Bot

# PRODUCTION CONFIGURATION
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "-1003605806688" 

# Base Mainnet Uniswap V2 Router
ROUTER_ADDRESS = "0x4752ba5DBc23f44D82143D093042C01768afc35E" 

async def run_sentinel():
    # Use AsyncWeb3 for modern subscription support
    async with AsyncWeb3(WebSocketProvider(WSS_URL)) as w3:
        bot = Bot(token=TG_TOKEN)
        
        print(f"--- Sentinel Active ---")
        print(f"Broadcasting to Channel: {CHAT_ID}")

        # Subscribe to new pending transactions
        subscription_id = await w3.eth.subscribe("pending_transactions")
        
        async for response in w3.socket.process_subscriptions():
            try:
                tx_hash = response['result']
                tx = await w3.eth.get_transaction(tx_hash)
                
                if not tx: continue

                # LOGIC 1: Detect New Contract Creations
                if tx.get('to') is None:
                    audit_msg = (
                        "🚨 **SENTINEL: NEW CONTRACT DETECTED**\n\n"
                        f"**Hash:** `{tx_hash}`\n"
                        "**Status:** Auditing Bytecode...\n\n"
                        "🛡️ [Check Safety on GoPlus](https://gopluslabs.io/token-security/8453/)"
                    )
                    await bot.send_message(chat_id=CHAT_ID, text=audit_msg, parse_mode="Markdown")

                # LOGIC 2: Detect 'Add Liquidity' calls
                elif tx.get('to').lower() == ROUTER_ADDRESS.lower():
                    if tx.get('input').hex().startswith('0xf305639b'): 
                        lp_msg = (
                            "💰 **LIQUIDITY ADDED!**\n"
                            f"**TX:** `{tx_hash}`\n\n"
                            "🚀 Trade window opening. Verify lock status."
                        )
                        await bot.send_message(chat_id=CHAT_ID, text=lp_msg, parse_mode="Markdown")
                
            except Exception:
                continue

if __name__ == "__main__":
    asyncio.run(run_sentinel())
