#!/usr/bin/env python3
"""Isolated QA HTTP server: prevent synthetic mtime ordering from yielding false 304 on SW replacement."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        # The real GitHub Pages deployment produces a fresh HTTP 200 for changed SW bytes.
        # In the local symlink fixture the predecessor file is freshly written,
        # while successor source has an older checkout timestamp. Python's
        # default conditional-response logic can incorrectly report HTTP 304.
        # Suppress conditional validators ONLY for sw.js, which is the upgrade script.
        if self.path.split("?",1)[0].endswith("/sw.js"):
            if "If-Modified-Since" in self.headers: del self.headers["If-Modified-Since"]
            if "If-None-Match" in self.headers: del self.headers["If-None-Match"]
        return super().send_head()
    def end_headers(self):
        self.send_header("Cache-Control","no-store, max-age=0")
        return super().end_headers()
if __name__=="__main__":
    ThreadingHTTPServer(("127.0.0.1",8999),lambda *a,**k:Handler(*a,directory="/tmp/ldc-r23-live",**k)).serve_forever()
