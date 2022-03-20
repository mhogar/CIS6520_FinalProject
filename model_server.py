#!/usr/bin/env python3

import json
import model
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
	def __init__(self, *args):
		self.model = model.Model()
		BaseHTTPRequestHandler.__init__(self, *args)


	def _set_response(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/json')
		self.end_headers()


	def do_POST(self):
		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length)

		response = self.model.predict(post_data)

		self._set_response()
		self.wfile.write(f"{json.dumps(response)}\n".encode('utf-8'))
	

def run(host='', port=8080):
	server_address = (host, port)
	httpd = HTTPServer(server_address, Handler)

	print(f"Running server {server_address}")
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()


if __name__ == '__main__':
	from sys import argv

	if len(argv) >= 3:
		run(host=argv[2], port=int(argv[1]))
	elif len(argv) >= 2:
		run(port=int(argv[1]))
	else:
		run()

