#!/usr/bin/env python3
"""
web cache and tracker
"""
import requests
import redis
from functools import wraps

try:
    store = redis.Redis(host='localhost', port=6379, db=0)
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")


def count_url_access(method):
    """Decorator counting how many times a URL is accessed"""
    @wraps(method)
    def wrapper(url):
        cached_key = "cached:" + url
        count_key = "count:" + url

        # Check if the URL data is already cached
        cached_data = store.get(cached_key)
        if cached_data:
            print(f"Cache hit for {url}")
            return cached_data.decode("utf-8")

        # Cache miss, fetch the URL data
        print(f"Cache miss for {url}, fetching data...")
        try:
            html = method(url)
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None

        # Store the data in cache and increment the access count
        store.setex(cached_key, 10, html)  # setex sets the value and expiration time in one call
        store.incr(count_key)
        return html

    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Returns HTML content of a url"""
    res = requests.get(url)
    res.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    return res.text


# Example usage:
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    print(get_page(url))
    print(get_page(url))
