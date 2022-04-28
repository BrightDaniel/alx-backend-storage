#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Any, Callable
from datetime import timedelta


def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data.
    '''
    @wraps(method)
    def invoker(*args, **kwargs) -> Any:
        '''The wrapper function for caching the output.
        '''
        redis_store = redis.Redis()
        res_key = 'result:{}'.format(','.join(args))
        req_key = 'count:{}'.format(','.join(args))
        result = redis_store.get(res_key)
        redis_store.incr(req_key)
        if result is not None:
            return result.decode('utf-8')
        result = method(*args, **kwargs)
        redis_store.setex(res_key, timedelta(seconds=10), result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    if url is None or len(url.strip()) == 0:
        return ''
    return requests.get(url).text
