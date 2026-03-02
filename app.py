import os
import asyncio
from telegram import Bot
from web3 import AsyncWeb3, WebSocketProvider

# --- CONFIG ---
WSS_URL = os.getenv("ALCHEMY_WSS_URL")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "-1003605806688"
REFERRAL_LINK = "https://t.me/BananaGunBot?start=ref_yourname" # Replace with your link

async def run_scout():
    async with AsyncWeb3(WebSocketProvider(WSS_URL)) as w3:
        tg_bot = Bot(token=TG_TOKEN)
        print("--- Sentinel Scout V1: Generating Referral Income ---")

        await w3.eth.subscribe("newHeads")
        
        async for response in w3.socket.process_subscriptions():
            try:
                # Logic: Find a new 'Long-Tail' token launch
                token_address = "0x..." 
                
                msg = (
                    "🚀 **NEW HIGH-ALPHA TOKEN DETECTED**\n\n"
                    f"**Contract:** `{token_address}`\n"
                    "⚠️ *Security: Unverified. Use caution.*\n\n"
                    f"👉 [Trade this token instantly here]({REFERRAL_LINK})"
                )
                await tg_bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
            except:
                continue

if __name__ == "__main__":
    asyncio.run(run_scout())
