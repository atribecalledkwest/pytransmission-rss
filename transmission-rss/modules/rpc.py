#!/usr/bin/env python
"""
A minimal-ish RPC client for transmission that really does
only what we want it to do, i.e. adding torrents.
"""

import json
from urlparse import urljoin
import requests

class RPCClient(object):
    """
    Provides a very minimal rpc client for transmission daemon
    """
    def __init__(self, host, port, path, credentials=None):
        self.host = host
        self.port = int(port)
        self.path = path
        self.credentials = credentials
        self.host_string = "http://{}:{:d}".format(self.host, self.port)
        self.endpoint = urljoin(self.host_string, self.path)
        self.login()
    def send_command(self, method, arguments=None, tag=None):
        """
        A very basic (if not awful) function to send commands to a daemon
        Returns the response as JSON as compliant with the RPC spec.
        """
        if arguments is None:
            arguments = {}
        data = {
            "method": method,
            "arguments": arguments
        }
        if tag is not None and isinstance(tag, (int, float)):
            data.update({
                'tag': int(tag)
            })
        resp = self.session.post(self.endpoint, data=json.dumps(data))
        if resp.status_code == 401:
            raise Exception("Authentication failed")
        if resp.status_code == 409:
            self.get_session_id()
            return self.send_command(method, arguments, tag)
        return resp.json()
    def login(self):
        """
        Sets up the session for our requests and saves basic auth information,
        then gets the session id.
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "pyTransmissionRSS v0.0.1a"})
        if self.credentials is not None and self.credentials != {}:
            if self.credentials.keys() == ['username', 'password']:
                auth = [self.credentials[i] for i in ['username', 'password']]
                self.session.auth = tuple(auth)
        self.get_session_id()
    def get_session_id(self):
        """
        Makes an empty post to the RPC endpoint, store the valid session-id.
        """
        head = self.session.post(self.endpoint)
        self.session.headers.update({
            "X-Transmission-Session-Id": head.headers['x-transmission-session-id']
        })
    def add_torrent(self, url, folder=None):
        """
        Takes a URL and an optional remote folder and adds it to the
        remote transmission daemon.
        If successful, returns a tuple of (True, Torrent name)
        Otherwise, returns a tuple of (False, Error string)
        """
        arguments = {
            "filename": url
        }
        if folder is not None:
            arguments.update({
                "download-dir": folder
            })
        add_resp = self.send_command("torrent-add", arguments=arguments)
        if add_resp['result'] == 'success':
            # Return name
            return True, add_resp['arguments']['torrent-added']['name']
        else:
            # Return the error given
            return False, add_resp['result']
