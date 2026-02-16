from src.bot import bot, DISCORD_TOKEN
import os
from aiohttp import web
import asyncio
import threading

async def handle(request):
    return web.Response(text="Maria-Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found.")
        return

    await start_web_server()
    
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
