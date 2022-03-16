#!/usr/bin/env python3

from sys import argv
from bisect import insort
import json
import requests

SECTOR_SIZE = 512


def predict_sectors(in_filename, num_sectors):
    with open(in_filename, "rb") as file:
        result = requests.post("http://192.168.1.12:8080", data=file)
    data = result.json()

    data_type = select_type(data)
    print("File type:", data_type)
    
    return select_max(data[data_type], num_sectors)


def select_type(data):
    max_prob = 0.0

    for key in data:
        prob = data[key][0]

        if prob > max_prob:
            max_prob = prob
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


def calc_stats(true_sectors, prediction):
    set1 = set(true_sectors)
    set2 = set(prediction)

    missed_sectors = set1 - set2
    additional_sectors = set2 - set1
    accuracy = 1.0 - len(missed_sectors) / len(true_sectors)

    print(f"Accuracy: {100.0 * accuracy}, Difference: +{additional_sectors} -{missed_sectors}")


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

    sectors = predict_sectors(in_filename, meta_data['num_sectors'])

    calc_stats(meta_data['true_sectors'], sectors)
    recover_file(filename, sectors)
 