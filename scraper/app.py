import json
import os.path
import time

from amazon import Amazon
from iherb import Iherb
from fastapi import FastAPI
import nest_asyncio


nest_asyncio.apply()
app = FastAPI()
base_storage = '/tmp/search/'
isExist = os.path.exists(base_storage)

app.last_scrape_request = time.time()

if not isExist:
    try:
        os.makedirs(base_storage)
        print("New cache directory is created!")
    except Exception:
        print("unable to create cache directory!")
        print(Exception)


@app.get("/", tags = ['ROOT'])
async def root() -> dict:
    return {"data": "hello2", "success": True}


@app.get("/supplement/{keyword}")
async def supplement_search(keyword: str, update_cache: bool = False, country_code: str = 'jp') -> dict:
    # return cached value if 1. exists 2. has values 3. update_cache is set to false
    file_path = base_storage + keyword + '_' + country_code
    cached_data = []
    cache_exists = os.path.isfile(file_path)
    cached_time = None
    try:
        if cache_exists and update_cache is False:
            f = open(file_path)
            cached_data = json.load(f)
            stat = os.stat(file_path)
            cached_time = stat.st_mtime
    except Exception:
        os.remove(file_path)
        return {'data': IOError, 'success': False}
    
    if cache_exists and update_cache is False and len(cached_data):
        return {'data': cached_data, 'success': True, 'lastUpdated': cached_time}
    
    # rate limit request to amazon
    # only 1 request can be processed per time window, which is the same as the cooldown
    request_cooldown = 2  # seconds
    sec_since_last_req = time.time() - app.last_scrape_request
    if sec_since_last_req < request_cooldown:
        return {'data': cached_data,
                'success': False,
                'message': '%d seconds until a new request can be processed' %
                           (request_cooldown - sec_since_last_req)}
    
    # search
    res_amazon = []
    try:
        res_amazon = Amazon.scrape(keyword, country_code)
        app.last_scrape_request = time.time()
    except Exception:
        pass
    
    # search
    res_iherb = []
    try:
        res_iherb = Iherb.scrape(keyword, country_code)
        app.last_scrape_request = time.time()
    except Exception:
        pass
    
    res_comb = res_amazon + res_iherb
    
    # if the response contains zero data, just return cached data
    if not len(res_comb):
        res_comb = cached_data

    # cache the result in a file if it contains data
    try:
        with open(file_path, 'w') as f:
            json.dump(res_comb, f)
    except Exception:
        return {'data': Exception, 'success': False}
    
    return {'data': res_comb, 'success': True, 'lastUpdated': time.time()}

# todo price tracker
