import json
import os.path
import time

from amazon import Amazon
from fastapi import FastAPI
import nest_asyncio

from scraper.iherb import Iherb

nest_asyncio.apply()
app = FastAPI()
base_storage = '/tmp/search/'
isExist = os.path.exists(base_storage)

app.last_scrape_request = time.time()

if not isExist:
    os.makedirs(base_storage)
    print("The new directory is created!")


@app.get("/", tags = ['ROOT'])
async def root() -> dict:
    return {"data": "hello2", "success": True}

@app.get("/supplement/{keyword}")
async def supplement_search(keyword: str, update_cache: bool = False, country_code: str = 'jp') -> dict:
    # return cached value if exists
    file_path = base_storage + keyword + '_' + country_code
    try:
        if os.path.isfile(file_path) and update_cache is False:
            f = open(file_path)
            data = json.load(f)
            stat = os.stat(file_path)
            return {'data': data, 'success': True, 'lastUpdated': stat.st_mtime}
    except Exception:
        os.remove(file_path)
        return {'data': IOError, 'success': False}

    # rate limit request to amazon
    # only 1 request can be processed per time window, which is the same as the cooldown
    request_cooldown = 2  # seconds
    sec_since_last_req = time.time() - app.last_scrape_request
    if sec_since_last_req < request_cooldown:
        return {'data': [],
                'success': False,
                'message': '%d seconds until a new request can be processed' %
                           (request_cooldown - sec_since_last_req)}

    # search
    try:
        res_amazon = Amazon.scrape(keyword, country_code)
        app.last_scrape_request = time.time()
    except Exception:
        return {'data': Exception, 'success': False}

    # search
    try:
        res_iherb = Iherb.scrape(keyword, country_code)
        app.last_scrape_request = time.time()
    except Exception:
        return {'data': Exception, 'success': False}
    
    res_comb = res_amazon + res_iherb

    # cache the result in a file
    try:
        with open(file_path, 'w') as f:
            json.dump(res_comb, f)
    except Exception:
        return {'data': Exception, 'success': False}
    
    return {'data': res_comb, 'success': True, 'lastUpdated': time.time()}

# todo price tracker
