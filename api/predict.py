from http.server import BaseHTTPRequestHandler
import json
import numpy as np
from datetime import datetime
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/predict':
            self.handle_prediction()
        else:
            self.send_error(404)

    def handle_prediction(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            city = data.get('city', 'delhi')
            traffic_reduction = data.get('traffic_reduction', 0)
            afforestation = data.get('afforestation', 0)
            bs_upgrade = data.get('bs_upgrade', 0)
            
            results = self.predict_impact(city, traffic_reduction, afforestation, bs_upgrade)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            self.send_error(500, str(e))

    def predict_impact(self, city, traffic_reduction, afforestation, bs_upgrade):
        base_values = {
            'delhi': {'co2': 35000, 'pm25': 150, 'nox': 280},
            'mumbai': {'co2': 28000, 'pm25': 120, 'nox': 220},
            'bengaluru': {'co2': 32000, 'pm25': 130, 'nox': 240},
            'chennai': {'co2': 25000, 'pm25': 110, 'nox': 200},
            'kolkata': {'co2': 22000, 'pm25': 100, 'nox': 180}
        }
        
        base = base_values.get(city, base_values['delhi'])
        
        traffic_impact = max(0.5, 1 - (traffic_reduction / 100) * 0.7)
        forest_impact = max(0.3, 1 - (afforestation / 100) * 0.4)
        upgrade_impact = max(0.4, 1 - (bs_upgrade / 100) * 0.6)
        
        net_co2 = base['co2'] * traffic_impact * forest_impact
        net_pm25 = base['pm25'] * traffic_impact * upgrade_impact
        net_nox = base['nox'] * traffic_impact * upgrade_impact
        
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'city': city,
            'parameters': {
                'traffic_reduction': traffic_reduction,
                'afforestation': afforestation,
                'bs_upgrade': bs_upgrade
            },
            'results': {
                'net_co2': round(net_co2),
                'net_pm25': round(net_pm25, 2),
                'net_nox': round(net_nox, 2),
                'co2_reduction': round(base['co2'] - net_co2),
                'pm25_reduction': round(base['pm25'] - net_pm25, 2),
                'nox_reduction': round(base['nox'] - net_nox, 2)
            }
        }