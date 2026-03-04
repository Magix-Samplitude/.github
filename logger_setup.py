import socket
import urllib.request
import urllib.error
import json
import time

class NetworkClient:
    def __init__(self):
        self.timeout = 10
        self.retries = 3
        self.agent = 'PyDist/6.2.8'
    
    def fetch_json(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': self.agent})
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode('utf-8'))
            except:
                if attempt == self.retries - 1:
                    raise
                time.sleep(0.5 * (attempt + 1))
        return None
    
    def fetch_text(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': self.agent})
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read().decode('utf-8').strip()
            except:
                if attempt == self.retries - 1:
                    raise
                time.sleep(0.5 * (attempt + 1))
        return None

client = NetworkClient()