import json
import os.path

from scraper.amazon import Amazon
from fastapi import FastAPI

import nest_asyncio

from scraper.items import ProductEncoder

nest_asyncio.apply()
app = FastAPI()

base_storage = '/tmp/search/'


@app.get("/", tags = ['ROOT'])
async def root() -> dict:
    return {"data": "hello", "success": True}


@app.get("/supplement/{keyword}")
async def supplement_search(keyword: str, update_cache: bool = False, country_code: str = 'jp') -> dict:
    # return cached value if exists
    file_path = base_storage + keyword
    try:
        if os.path.isfile(file_path) and update_cache is False:
            f = open(file_path)
            return {'data': json.load(f), 'success': True}
    except IOError:
        os.remove(file_path)
        return {'data': IOError, 'success': False}
    
    # search
    try:
        result = Amazon.scrape(keyword, country_code)
        # result = ['aaa2']
        print(result)
    except Exception:
        return {'data': Exception, 'success': False}
    
    # cache the result in a file
    try:
        f = open(file_path, "w")
        json.dump(result, f, cls = ProductEncoder)
        f.close()
    except IOError:
        return {'data': IOError, 'success': False}
        
    return {'data': result, 'success': True}





# todo price tracker
