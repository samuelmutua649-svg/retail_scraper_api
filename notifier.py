import httpx
from config import DISCORD_WEBHOOK_URL

async def send_alert(message: str):
    """Sends a formatted alert message directly to your Discord channel."""
    if not DISCORD_WEBHOOK_URL or "YOUR_DISCORD_WEBHOOK_URL_HERE" in DISCORD_WEBHOOK_URL:
        print(f"\n[ALERT TRIGGERED - DISCORD NOT CONFIGURED]:\n{message}\n")
        return

    payload = {
        "content": message
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DISCORD_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            print("💬 Discord notification sent successfully!")
        except Exception as e:
            print(f"❌ Failed to send Discord alert: {e}")