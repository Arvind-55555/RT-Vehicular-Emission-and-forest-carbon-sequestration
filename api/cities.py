from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/cities':
            self.get_cities()
        else:
            self.send_error(404)

    def get_cities(self):
        cities_data = {
            'cities': [
                {'id': 'delhi', 'name': 'Delhi', 'status': 'active'},
                {'id': 'mumbai', 'name': 'Mumbai', 'status': 'active'},
                {'id': 'bengaluru', 'name': 'Bengaluru', 'status': 'active'},
                {'id': 'chennai', 'name': 'Chennai', 'status': 'active'},
                {'id': 'kolkata', 'name': 'Kolkata', 'status': 'active'}
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(cities_data).encode())