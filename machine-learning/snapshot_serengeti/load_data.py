#########################################
# Import Data
# - meta data
# - annotations
# - images
# SS data from: http://datadryad.org/resource/doi:10.5061/dryad.5pt92
#########################################

#########################
# load modules
#########################

import numpy as np
import pandas as pd
import os
import requests
import random as rand


#########################
# Parameters
#########################

path = "D:/Studium_GD/Zooniverse/Data/snapshot_serengeti/"
path_images = path + 'images/'
path_gold = path + "annotations/gold_standard_data.csv"
path_consensus = path + "annotations/consensus_data.csv"
path_image_links = path + "image_links/all_images.csv"
image_url = "https://snapshotserengeti.s3.msi.umn.edu/"


#########################
# Read Meta Data
#########################

# CaptureEventID, NumSpecies, Species, Count, CaptureEventID
#
dat_gold = pd.read_csv(path_gold)

# CaptureEventID, NumImages, DateTime, SiteID, LocationX, LocationY,
# NumSpecies, Species, Count, Standing, Resting, Moving, Eating, Interacting,
# Babies, NumClassifications, NumVotes, NumBlanks, Evenness

dat_consensus = pd.read_csv(path_consensus)

# CaptureEventID, URL_Info
dat_image_links = pd.read_csv(path_image_links)


#########################
# Print Statistics
#########################

# extract some statistics
print("-------- Gold Label Stats ---------------------------")
print("Number of identified species events: %s" % (dat_gold.shape[0]))
nunique = dat_gold.apply(lambda x: len(x.unique()))
print("Number of different species: %s" % (nunique['Species']))
tt = dat_gold.groupby(dat_gold.CaptureEventID).count()
print("Number of distinct capture events: %s" % (tt.shape[0]))


print("-------- Annotation Stats (Consensus)-----------------")
print("Number of identified species events: %s" % (dat_consensus.shape[0]))
nunique = dat_consensus.apply(lambda x: len(x.unique()))
print("Number of different species: %s" % (nunique['Species']))
print("Number of different locations: %s" % (nunique['SiteID']))
tt = dat_consensus.groupby(dat_consensus.CaptureEventID).count()
print("Number of distinct capture events: %s" % (tt.shape[0]))


print("-------- Image Link Stats-----------------")
print("Number of images: %s" % (dat_image_links.shape[0]))
tt = dat_image_links['URL_Info'].apply(lambda x: x.split("/")[0])
print("Number of images per season")
tt.groupby(tt).count()

print("-------- Gold Label and Season-----------------")
# inner join images with gold label data
dat_gold_images = pd.merge(dat_gold, dat_image_links, how='inner',
                           left_on='CaptureEventID',
                           right_on='CaptureEventID')

tt = dat_gold_images['URL_Info'].apply(lambda x: x.split("/")[0])
print("Number of images per season")
tt.groupby(tt).count()

# animal species
dat_consensus.groupby(dat_consensus.Species).CaptureEventID.count()
dat_gold_images.groupby(dat_gold_images.Species).CaptureEventID.count()


#########################
# Find specific images
#########################

# function to choose a random image from a set of urls
def choose_random(df, image_urls, n_samples=1):
    # get capture ids
    captures = df['CaptureEventID']
    n_rows = captures.shape[0]
    # choose random capture event
    ii = rand.sample(range(0, n_rows), min(n_samples, n_rows))
    # loop over all samples
    for i in ii:
        cap_id = captures.iloc[i]
        # get image link
        image_path = image_urls[image_urls['CaptureEventID'] == cap_id].iloc[0]
        image_path = image_path['URL_Info']
        image_name = image_path.split("/")[3]
        # get image
        get_image_URL(url=image_url + image_path,
                      output_image_name=image_name,
                      path_output=path_images)

# find images from babies
babies = dat_consensus[dat_consensus.Babies > 0.9]
choose_random(babies, dat_image_links, n_samples=10)

# find images with low consensus
low_consensus = dat_consensus[(dat_consensus.Evenness > 0.8) &
                              (dat_consensus.NumVotes > 20)]
choose_random(low_consensus, dat_image_links, n_samples=10)

# find eating animals
eating = dat_consensus[dat_consensus.Eating > 0.9]
choose_random(eating, dat_image_links, n_samples=10)

# find lions
lions = dat_consensus[(dat_consensus.Species == 'lionFemale') |
                      (dat_consensus.Species == 'lionMale')]
choose_random(lions, dat_image_links, n_samples=10)


#########################
# Get Image Data
#########################

# function to download an image
def get_image_URL(url, output_image_name, path_output):
    img_data = requests.get(url).content
    with open(path_output + output_image_name, 'wb') as handler:
        handler.write(img_data)

# test
image_path = "S4/R10/R10_R2/S4_R10_R2_IMAG0553.JPG"
image_name = image_path.split("/")[3]
get_image_URL(url=image_url + image_path,
              output_image_name=image_name,
              path_output=path_images)


# test over several files
for image_path in dat_gold_images['URL_Info'][0:100]:
    image_name = image_path.split("/")[3]
    get_image_URL(url=image_url + image_path,
                  output_image_name=image_name,
                  path_output=path_images)



###############################
# List images on disk
###############################

img_names = os.listdir(path_images)
img_paths = [path_images + x for x in img_names]

