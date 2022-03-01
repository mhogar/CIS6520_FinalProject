#!/usr/bin/env python3

import numpy as np
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from joblib import load

class Handler(BaseHTTPRequestHandler):
	def __init__(self, *args):
		self.clf = load("model/model.dat")
		with open("model/labels.csv") as file:
			self.labels = file.readline().split(",")

		BaseHTTPRequestHandler.__init__(self, *args)


	def _set_response(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/json')
		self.end_headers()


	def do_POST(self):
		length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(length)

		response = {
			'type': self.determine_block_type(post_data)
		}

		self._set_response()
		self.wfile.write(f"{json.dumps(response)}\n".encode('utf-8'))


	def determine_block_type(self, data):
		vec = np.zeros(256, dtype=np.int16)
		for byte in data:
			vec[byte] += 1

		prediction = self.clf.predict([vec])[0]
		return self.labels[prediction]


def run(port=8080):
	server_address = ('192.168.1.12', port)
	httpd = HTTPServer(server_address, Handler)

	print(f"Running server {server_address}")
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		httpd.server_close()


if __name__ == '__main__':
	from sys import argv

	if len(argv) == 2:
		run(port=int(argv[1]))
	else:
		run()

