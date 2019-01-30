from time import time
import csv
import random
import argparse


def write_kick_out(filepath, output_filepath, miss_prob):
    chunk_size = 10000
    t0 = time()
    chunk = []
    with open(filepath, 'r') as infile, open(output_filepath, 'w') as outfile:
        for line in infile:
            if line.startswith("##"):
                chunk.append(line)
            elif line.startswith("#"):
                fields = line[1:].split()
                chunk.append(line)
                outfile.write(''.join(chunk))
                chunk = []
                break
        idx_FILTER = fields.index("FILTER")
        idx_REF = fields.index("REF")
        idx_ALT = fields.index("ALT")
        idx_INFO = fields.index("INFO")
        vcf_reader = csv.reader(infile, delimiter='\t')
        for num_row, row in enumerate(vcf_reader):
            fields = row[idx_INFO].split(';')
            new_fields = list(filter(lambda x: random.random() >= miss_prob, fields))
            if len(new_fields) == 0:
                new_fields = fields[random.randint(0, len(fields)-1)]
            row[idx_INFO] = ';'.join(new_fields)
            chunk.append(row)
            if num_row % chunk_size == 0 and num_row > 0:
                outfile.write('\n'.join(['\t'.join(var) for var in chunk]) + '\n')
                chunk = []
        outfile.write('\n'.join(['\t'.join(var) for var in chunk]))
    t1 = time()
    print("Time elapsed {}s".format(t1 - t0))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to input VCF file")
    parser.add_argument("output", help="path to output VCF file")
    parser.add_argument("miss_prob", help="Missing probability, e.g. 0.1", type=float)
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    miss_prob = args.miss_prob
    write_kick_out(input_file, output_file, float(miss_prob))


if __name__ == '__main__':
    main()
