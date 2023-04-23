from scraper.amazon import Amazon
from fastapi import FastAPI

import nest_asyncio

nest_asyncio.apply()
app = FastAPI()


@app.get("/", tags = ['ROOT'])
async def root() -> list:
    return Amazon.scrape('tmg', 'us')
