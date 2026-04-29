from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
 
# ─── Supabase config ───────────────────────────────────────
SUPABASE_URL = "https://YOUR-PROJECT-ID.supabase.co"
SUPABASE_ANON_KEY = "YOUR-ANON-KEY"
BUCKET_NAME = "lab-files"
 
 
def get_file_list():
    """Fetch list of files from Supabase storage bucket."""
    url = f"{SUPABASE_URL}/storage/v1/object/list/{BUCKET_NAME}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({"prefix": "", "limit": 100}).encode(),
        method="POST"
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
    return [item["name"] for item in data if item.get("name")]
 
 
def get_file_content(filename):
    """Download a file from Supabase and return its bytes."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{filename}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {SUPABASE_ANON_KEY}"}
    )
    with urllib.request.urlopen(req) as res:
        return res.read()
 
 
class handler(BaseHTTPRequestHandler):
 
    def do_GET(self):
        path = self.path
 
        # ── GET /api/files → return file list ──────────────
        if path == "/api/files":
            try:
                files = get_file_list()
                body = json.dumps({"files": files}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
 
        # ── GET /api/download/<filename> → proxy file ──────
        elif path.startswith("/api/download/"):
            filename = path.replace("/api/download/", "")
            try:
                content = get_file_content(filename)
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Disposition",
                                 f'attachment; filename="{filename}"')
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(str(e).encode())
 
        # ── Default ─────────────────────────────────────────
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Cloud Lab API is running!",
                "endpoints": ["/api/files", "/api/download/<filename>"]
            }).encode())