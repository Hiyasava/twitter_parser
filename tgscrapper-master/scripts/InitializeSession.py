import asyncio

from pyrogram import Client
from configparser import ConfigParser


class InitializeSession():

    config = ConfigParser()
    config.read('config.ini')

    API_ID = config.get('pyrogram', 'api_id')
    API_HASH = config.get('pyrogram', 'api_hash')
    
    async def SendTestMessage(): 
        
        config = ConfigParser()
        config.read('config.ini')

        api_id = config.get('pyrogram', 'api_id')
        api_hash = config.get('pyrogram', 'api_hash')

        async with Client('my_account', api_id, api_hash) as app:
            await app.send_message('me', 'Initialize Complete')

    asyncio.run(SendTestMessage())