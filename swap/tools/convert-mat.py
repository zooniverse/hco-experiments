#!/usr/bin/env python
################################################################
# Script to convert .mat file to a csv

import scipy.io as sio

def main():
    path = os.path.dirname(os.path.realpath(__file__))
    fname = 'SNHunters_classification_dump_20170109_metadata.mat'
    out = 'SNHunters_classification_dump_20170109_metadata.csv'

    data = sio.loadmat('/'.join((path,fname)))
    out = '/'.join((path,out))

    keys = ['classification_id', 'user_name','user_id','annotation','gold_label','machine_score','diff','object_id','subject_id','mag','mag_err']

    for i in range(len(data['classification_id'][0])):
