#!/usr/bin/env python3

from sys import argv
from math import ceil
from os import urandom
from os.path import dirname, join
from random import randrange
import json

SECTOR_SIZE = 512

MIN_GAPS = 4
MAX_GAPS = 9

MIN_GAP_SIZE = 5
MAX_GAP_SIZE = 15


class RandomByteStream():
	def read(self, amount):
		return urandom(amount)


def write_sector(out_file, in_stream):
	out_file.write(in_stream.read(SECTOR_SIZE))


def create_bitmap(init_size, num_gaps):
	bitmap = [0] * init_size
	offset = 0

	slots = []

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
	if len(argv) < 2:
		print("Missing filename.")
		exit(0)

	rand_stream = RandomByteStream()
	filename = argv[1]
	out_filename = filename + "_frag.dat"
	json_filename = filename + "_frag.json"

	meta_data = {}
	with open(filename, "rb") as in_file:
		in_file.seek(0, 2) # seek to end
		num_sectors = ceil(in_file.tell() / float(SECTOR_SIZE))
		in_file.seek(0)
	
		num_gaps = randrange(MIN_GAPS, MAX_GAPS+1)
		bitmap = create_bitmap(num_sectors, num_gaps)

		meta_data["num_sectors"] = num_sectors
		meta_data["num_frags"] = num_gaps + 1
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

	print(f"{filename} -> {out_filename}")
	print(json_filename)
	

