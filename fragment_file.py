#!/usr/bin/env python3

from sys import argv
from math import ceil
from os import urandom, listdir
from os.path import dirname, join
from random import randrange, choice
import json

SECTOR_SIZE = 512

MIN_GAPS = 1
MAX_GAPS = 4

MIN_GAP_SIZE = 3
MAX_GAP_SIZE = 10


class RandomByteStream():
	def read(self, amount):
		return urandom(amount)


def write_sector(out_file, in_stream):
	out_file.write(in_stream.read(SECTOR_SIZE))


def create_bitmap(init_size):
	bitmap = [0] * init_size
	offset = 0

	slots = []

	num_gaps = randrange(MIN_GAPS, MAX_GAPS+1)
	print("Fragments:", num_gaps + 1)

	for i in range(num_gaps):
		slots.append(randrange(1, init_size))
	slots.sort()

	for slot in slots:
		slot += offset
		gap_size = randrange(MIN_GAP_SIZE, MAX_GAP_SIZE+1)

		bitmap[slot:slot] = [1] * gap_size
		offset += gap_size

	return bitmap


if __name__ == "__main__":
	if len(argv) < 3:
		print("Too few arguments.")
		exit(0)

	rand_stream = RandomByteStream()

	in_filename = argv[1]
	out_filename = argv[2]

	json_filename = out_filename + "_frag.json"
	out_filename += "_frag.dat"
	
	meta_data = {}
	with open(in_filename, "rb") as in_file:
		in_file.seek(0, 2) # seek to end
		num_sectors = ceil(in_file.tell() / float(SECTOR_SIZE))
		in_file.seek(0)
	
		bitmap = create_bitmap(num_sectors)

		meta_data["num_sectors"] = num_sectors
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
	

