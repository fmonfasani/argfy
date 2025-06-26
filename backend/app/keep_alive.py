# backend/app/keep_alive.py
import asyncio
import aiohttp
import os
from datetime import datetime

async def ping_self():
    """Ping al propio servicio cada 10 minutos para evitar sleep"""
    if os.getenv("ENVIRONMENT") != "production":
        return
    
    url = "https://argfy-backend.onrender.com/health"
    
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"Keep-alive ping: {datetime.now()}")
        except Exception as e:
            print(f"Keep-alive error: {e}")
        
        # Esperar 10 minutos
        await asyncio.sleep(600)
