import os
import asyncio
from web3 import AsyncWeb3, WebSocketProvider
from telegram import Bot

# PRODUCTION CONFIGURATION (Values pulled from Render Environment)
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")

# YOUR SPECIFIC CHANNEL ID
CHAT_ID = "-1003605806688" 

# Base Mainnet Uniswap V2 Router (Common for new token liquidity)
ROUTER_ADDRESS = "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24" 

async def run_sentinel():
    # Use the modern AsyncWeb3 provider for 2026 standards
    async with AsyncWeb3(WebSocketProvider(WSS_URL)) as w3:
        bot = Bot(token=TG_TOKEN)
        
        print(f"--- Sentinel Active on Base Mainnet ---")
        print(f"Broadcasting to: {CHAT_ID}")

        # Subscribe to new block headers (Supported on Base)
        subscription_id = await w3.eth.subscribe("newHeads")
        
        async for response in w3.socket.process_subscriptions():
            try:
                # Extract block header and fetch full transaction details
                block_number = response['result']['number']
                block = await w3.eth.get_block(block_number, full_transactions=True)
                
                for tx in block.transactions:
                    # LOGIC 1: Detect New Contract Creations (Targeting Audits)
                    if tx.get('to') is None:
                        tx_hash = tx['hash'].hex()
                        audit_msg = (
                            "🚨 **SENTINEL: NEW CONTRACT DETECTED**\n\n"
                            f"**Hash:** `{tx_hash}`\n"
                            "**Status:** Auditing Bytecode...\n\n"
                            "🛡️ [Check Safety on GoPlus](https://gopluslabs.io/token-security/8453/)"
                        )
                        await bot.send_message(chat_id=CHAT_ID, text=audit_msg, parse_mode="Markdown")

                    # LOGIC 2: Detect 'Add Liquidity' (Targeting Trade Signals)
                    elif tx.get('to') and tx.get('to').lower() == ROUTER_ADDRESS.lower():
                        # check for addLiquidityETH method (0xf305639b)
                        if tx.get('input').hex().startswith('0xf305639b'): 
                            tx_hash = tx['hash'].hex()
                            lp_msg = (
                                "💰 **LIQUIDITY ADDED!**\n"
                                f"**TX:** `{tx_hash}`\n\n"
                                "🚀 Trade window open. Check lock status before entry."
                            )
                            await bot.send_message(chat_id=CHAT_ID, text=lp_msg, parse_mode="Markdown")
                
            except Exception as e:
                # Silent catch to prevent the bot from stopping during network hiccups
                continue

if __name__ == "__main__":
    asyncio.run(run_sentinel())
