import json
import os.path
from amazon import Amazon
from fastapi import FastAPI
import nest_asyncio

nest_asyncio.apply()
app = FastAPI()
base_storage = '/tmp/search/'
isExist = os.path.exists(base_storage)
if not isExist:
    os.makedirs(base_storage)
    print("The new directory is created!")


@app.get("/", tags = ['ROOT'])
async def root() -> dict:
    return {"data": "hello2", "success": True}


@app.get("/supplement/{keyword}")
async def supplement_search(keyword: str, update_cache: bool = False, country_code: str = 'jp') -> dict:
    # return cached value if exists
    file_path = base_storage + keyword
    try:
        if os.path.isfile(file_path) and update_cache is False:
            f = open(file_path)
            data = json.load(f)
            return {'data': data, 'success': True}
    except Exception:
        os.remove(file_path)
        return {'data': IOError, 'success': False}
    
    # search
    try:
        result = Amazon.scrape(keyword, country_code)
    except Exception:
        return {'data': Exception, 'success': False}
    
    # cache the result in a file
    try:
        with open(file_path, 'w') as f:
            json.dump(result, f)
    except Exception:
        return {'data': Exception, 'success': False}
    
    return {'data': result, 'success': True}

# todo price tracker
