import asyncio
import aiohttp

API_EXCEPTIONS = [
    aiohttp.ClientConnectionError, 
    aiohttp.ClientResponseError, 
    aiohttp.InvalidURL, 
    asyncio.TimeoutError
]