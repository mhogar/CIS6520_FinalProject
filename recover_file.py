#!/usr/bin/env python3

from sys import argv
import json

SECTOR_SIZE = 512


def predict_sectors(in_filename, num_sectors):
    pass


def calc_accuracy(true_sectors, prediction):
    num_diff = len(true_sectors - prediction)
    return 1.0 - float(num_diff) / len(true_sectors)


def recover_file(filename, sectors):
    in_filename = filename + "_frag.dat"
    out_filename =  filename + "_recovered.dat"

    with open(in_filename, "rb") as in_file:
        with open(out_filename, "wb") as out_file:
            for sector in sectors:
                in_file.seek(sector * SECTOR_SIZE)
                out_file.write(in_file.read(SECTOR_SIZE))

    print(f"{in_filename} -> {out_filename}")


if __name__ == "__main__":
    if len(argv) < 2:
        print("Missing filename.")
        exit(0)
    
    filename = argv[1]
    in_filename = filename + "_frag.dat"
    json_filename = filename + "_frag.json"

    with open(json_filename) as file:
        meta_data = json.load(file)

    true_sectors = set(meta_data['true_sectors'])
    sectors = true_sectors
    #sectors = predict_sectors(in_filename, meta_data['num_sectors'])

    print(f"Accuracy: {calc_accuracy(true_sectors, sectors)}")
    recover_file(filename, sectors)
 