#!/usr/bin/env python3

from sys import argv
from math import floor, ceil
from os import urandom, listdir
from os.path import dirname, join
from random import randrange, choice
import argparse
import json

SECTOR_SIZE = 512

MIN_GAPS = 1
MAX_GAPS = 3

class RandomByteStream():
	def read(self, amount):
		return urandom(amount)


def write_sector(out_file, in_stream):
	out_file.write(in_stream.read(SECTOR_SIZE))


def create_bitmap(init_size):
	bitmap = [0] * init_size
	offset = 0

	slots = []

	num_new_sectors = randrange(floor(init_size/3), ceil(init_size/2))
	num_gaps = randrange(MIN_GAPS, MAX_GAPS+1)

	for i in range(num_gaps):
		slots.append(randrange(1, init_size))
	slots.sort()

	for slot in slots:
		slot += offset
		gap_size = ceil(num_new_sectors / num_gaps)

		bitmap[slot:slot] = [1] * gap_size
		offset += gap_size

	print("True Sectors:", init_size)
	print("New Sectors:", num_new_sectors)

	return bitmap, num_new_sectors


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Fragement a file.')
	parser.add_argument('in_file', help='in file')
	parser.add_argument('out_file', help='out file')

	args = parser.parse_args()
	rand_stream = RandomByteStream()

	in_filename = args.in_file
	out_filename = args.out_file

	json_filename = out_filename + "_frag.json"
	out_filename += "_frag.dat"
	
	meta_data = {}
	with open(in_filename, "rb") as in_file:
		in_file.seek(0, 2) # seek to end
		num_sectors = ceil(in_file.tell() / float(SECTOR_SIZE))
		in_file.seek(0)
	
		bitmap, num_new_sectors = create_bitmap(num_sectors)

		meta_data["num_sectors"] = num_sectors
		meta_data["num_new_sectors"] = num_new_sectors
		meta_data["true_sectors"] = []

		with open(out_filename, "wb") as out_file:
			for index, bit in enumerate(bitmap):
				if bit == 0:
					meta_data["true_sectors"].append(index)
					write_sector(out_file, in_file)
				else:
					write_sector(out_file, rand_stream)

	with open(json_filename, "w") as out_file:
		out_file.write(json.dumps(meta_data))

	print(f"{in_filename} -> {out_filename}, {json_filename}")
	

