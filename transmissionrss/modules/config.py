#!/usr/bin/env python
""" Module provides an easy wrapper around the pyyaml library """

from os.path import isfile, expanduser
from yaml import dump, load

class Config(object):
    """
     Try to read from a local configuration file
     If no readable files can be found, create one with a default configuration meant to be edited.
    """
    def __init__(self):
        self.files_to_check = ['~/.config/transmission-rss.conf', '~/.transmission-rss.conf']
        self.is_default = False
        self.__file__ = None
        self.feeds = []
        self.read()
    def read(self):
        """
         Read from one of the specified configuration files, and attempt to
         parse it as a config file. If no suitable file is found, create one
         with some default information and return False. Otherwise, return True.
        """
        if len([isfile(expanduser(conf_file)) for conf_file in self.files_to_check]) == 0:
            with open(expanduser('~/.transmission-rss.conf'), 'w') as infile:
                defaultconfig = {
                    "connection": {
                        "host": "localhost",
                        "port": 9091,
                        "path": "/transmission/rpc",
                        "login": {
                            "username": "If you dont have authentication setup",
                            "password": "Just replace this with `login: null`"
                        }
                    },
                    "feeds": [
                        {
                            "url": "http://example.com/feed.rss",
                            "regex": ".*"
                        },
                        {
                            "url": "http://example.com/feed2.rss",
                            "regex": [
                                ".*",
                                ".mkv$"
                            ]
                        },
                        {
                            "url": "https://example.com/feed3.rss",
                            "folder": "/home/karen/Downloads/"
                        }
                    ]
                }
                infile.write(dump(defaultconfig, default_flow_style=False))
            self.is_default = True
            return False
        for conf in self.files_to_check:
            if isfile(expanduser(conf)):
                try:
                    self.__path__ = expanduser(conf)
                    with open(self.__path__, 'r') as outfile:
                        self.__file__ = outfile.read()
                        break
                except IOError:
                    pass
        self.__yaml__ = load(self.__file__)
        self.feeds = self.__yaml__['feeds']
        self.connection = self.__yaml__['connection']
        return True
    def write(self):
        """
         Write the current configuration stored in memory as human-readable YAML.
        """
        with open(self.__path__, 'w') as outfile:
            outfile.write(dump({
                "feeds": self.feeds,
                "connection": self.connection
            }, default_flow_style=False))
