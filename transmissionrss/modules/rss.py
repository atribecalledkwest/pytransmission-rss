#!/usr/bin/env python
"""
This module provides a class for a feed with cache
"""

from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup as bs
import requests

# Minimum allowed time before another RSS update
UPDATE_MIN = timedelta(minutes=5)
# The normal time after which we will update
UPDATE_MAX = timedelta(minutes=30)

RE_TYPE = type(re.compile('retype'))

class Feed(object):
    """
     An RSS feed. Includes built-in cache and timer to stop too many requests.
    """
    def __init__(self, url, regex=None, folder=None):
        self.url = url

        # Compile regex if needed
        if isinstance(regex, (str, unicode)):
            self.regex = re.compile(regex)
        elif isinstance(regex, (list, tuple)):
            self.regex = [re.compile(i) for i in regex]
        else:
            self.regex = None

        self.folder = folder

        # Cache array
        self.cache = []

        # Last updated
        self.last_updated = None

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "pyTransmission-RSS"
        })
        self.update()
    def update(self, force=False):
        """
         Grabs the RSS feed stored, updates the cache, and sets the timer.
         Updates will be allowed if after five minutes of the last update
         if the force argument is True, and after thirty minutes otherwise.
        """
        now = datetime.now()
        if self.last_updated is not None:
            if self.last_updated + UPDATE_MIN < now and force is False:
                return False
            elif self.last_updated + UPDATE_MAX < now:
                return False
        else: # Set last updated time
            self.last_updated = datetime.now()
        resp = self.session.get(self.url)
        if resp.status_code != 200: # Not 200 OK
            return False
        self.cache = bs(resp.text, 'lxml-xml')
        return True
    def get_entries(self):
        """
         Parses the cache and returns items in a dict. If self.regex exists,
         make sure entry titles match.
        """
        # Build return array
        ret = []
        for item in self.cache.find_all('item'):
            ret.append({
                "title": item.title.text,
                "link": item.link.text
            })
        # Check if regex isn't enabled
        if self.regex is None:
            return ret
        else:
            filtered = []
            for item in ret:
                if isinstance(self.regex, RE_TYPE):
                    if re.match(self.regex, item['title']) is not None:
                        filtered.append(item)
            return filtered
