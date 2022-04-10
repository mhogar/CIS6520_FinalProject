#!/usr/bin/env python3

from sys import argv
from bisect import insort
import json
import requests
import argparse

SECTOR_SIZE = 512


def predict_sectors(in_filename, data_type, host, num_sectors):
    with open(in_filename, "rb") as file:
        result = requests.post(f"http://{host}", data=file)
    data = result.json()

    if data_type == "auto":
        data_type = select_type(data)
        print("Determined file type:", data_type)
    
    return select_max(data[data_type], num_sectors)


def select_type(data):
    max_avg = 0.0

    for key in data:
        avg = data[key][0]

        if avg > max_avg:
            max_avg = avg
            data_type = key
    
    return data_type


def select_max(probs, num_sectors):
    probs_dict = {}
    for index, prob in enumerate(probs[1:-1]):
        probs_dict[index+1] = prob

    indices = [0, len(probs)-1]
    sorted_probs_dict = sorted(probs_dict.items(), key=lambda item: -item[1])

    for item in sorted_probs_dict:
        indices.append(item[0])
        if len(indices) >= num_sectors:
            break
    
    indices.sort()
    return indices


def calc_stats(true_sectors, prediction, num_new_sectors, csv):
    set1 = set(true_sectors)
    set2 = set(prediction)

    missed_sectors = set1 - set2
    num_missed = len(missed_sectors)

    accuracy = 1.0 - num_missed / num_new_sectors

    if csv:
        print(f"{num_missed}/{num_new_sectors},{accuracy}")
    else:
        print(f"Wrong Sectors: {num_missed}/{num_new_sectors}\nAccuracy: {accuracy}")


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
    parser = argparse.ArgumentParser(description='Fragement a file.')
    parser.add_argument('in_file', help='in file')
    parser.add_argument('data_type', help='data type')
    parser.add_argument('host', help='model server host')
    parser.add_argument('--csv', dest='csv', action='store_const', const=True, default=False, help="output in csv form")

    args = parser.parse_args()
    
    filename = args.in_file
    in_filename = filename + "_frag.dat"
    json_filename = filename + "_frag.json"

    data_type = args.data_type
    host = args.host

    with open(json_filename) as file:
        meta_data = json.load(file)

    sectors = predict_sectors(in_filename, data_type, host, meta_data['num_sectors'])

    calc_stats(meta_data['true_sectors'], sectors, meta_data['num_new_sectors'], args.csv)
    if not args.csv: recover_file(filename, sectors)
 
