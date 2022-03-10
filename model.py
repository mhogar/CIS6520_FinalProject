#!/usr/bin/env python3

import numpy as np
from joblib import load

class Model():
	def __init__(self):
		self.clf = load("model/model.dat")
		self.scaler = load("model/scaler.dat")
		with open("model/labels.csv") as file:
			self.labels = file.readline().split(",")


	def predict(self, data):
		SECTOR_SIZE = 512
		num_sectors = len(data) / SECTOR_SIZE
		vectors = np.zeros((int(num_sectors), 256), dtype=np.int16)

		for row, vec in enumerate(vectors):
			start = row*SECTOR_SIZE

			for i in range(start, start+SECTOR_SIZE):
				vec[data[i]] += 1

		vectors = self.scaler.transform(vectors)
		predictions = self.clf.predict_proba(vectors)

		result = {}

		for index, label in enumerate(self.labels):
			result[label] = [0] * len(predictions)

			for i, prediction in enumerate(predictions):
				result[label][i] = prediction[index]

			result[label]

		return result


if __name__ == '__main__':
	from sys import argv

	if len(argv) < 2:
		print("Missing filename.")
		exit(0)

	model = Model()
	with open(argv[1], "rb") as f:
		print(model.predict(f.read(512)))
