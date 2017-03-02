#!/usr/bin/env python
################################################################
# Script to convert .mat file to a csv

import scipy.io as sio
import os
import numpy
import csv
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()
    print("Using file %s" % args.file)

    if not os.path.isfile(args.file):
        raise FileNotFoundError("Couldn't find file at '%s'" % args.file)
    if args.file.split('.')[-1] != 'mat':
        raise ValueError("File '%s' not a valid mat file" % args.file)

    file = args.file
    name = file.split('.')[0]
    outfile = '.'.join([name, 'csv'])

    data = sio.loadmat(file)

    keys = ['classification_id', 'user_name','user_id',\
            'annotation','gold_label','machine_score', \
            'diff','object_id','subject_id','mag','mag_err']

    count = 0

    with open(outfile, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
            

        for index in range(len(data['classification_id'][0])):
            d = {}

            for key in keys:
                #print(key, data[key], type(data[key][0]))
                if type(data[key][0]) is numpy.str_:
                    d[key] = data[key][index].strip()
                else:
                    d[key] = data[key][0][index]
            

            writer.writerow(d)

            sys.stdout.write("%d records processed\r" % count)
            sys.stdout.flush()

            count += 1



    




if __name__ == "__main__":
    main()