#!/usr/bin/env python
"""
This module provides a class for a feed with cache
"""
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import requests

class Feed(object):
    """
    An RSS feed. Includes built-in cache and timer to stop too many requests.
    """
    def __init__(self):
        pass
