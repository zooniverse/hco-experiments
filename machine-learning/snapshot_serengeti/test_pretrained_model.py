# add path to modules from:
# https://github.com/fchollet/deep-learning-models
import sys
sys.path.insert(0, 'D:/Studium_GD/Zooniverse/GitHub/deep-learning-models')

# import modules
from resnet50 import ResNet50
from keras.preprocessing import image
from imagenet_utils import preprocess_input, decode_predictions
import os
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import gridspec
import matplotlib.pyplot as plt
from vgg16 import VGG16
from inception_v3 import InceptionV3


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
# Functions
#########################

# Plot prediction as barchart below image
def plot_pred_vs_image(img,preds_df,out_name):
    # function to plot predictions vs image
    f, axarr = plt.subplots(2, 1)
    plt.suptitle("ResNet50- PreTrained on ImageNet")
    axarr[0].imshow(img)
    sns.set_style("whitegrid")
    pl = sns.barplot(data = preds_df, x='Score', y='Species')
    axarr[1] = sns.barplot(data = preds_df, x='Score', y='Species',)
    axarr[0].autoscale(enable=False)
    axarr[0].get_xaxis().set_ticks([])
    axarr[0].get_yaxis().set_ticks([])
    axarr[1].autoscale(enable=False)
    gs = gridspec.GridSpec(2,1, width_ratios=[1],height_ratios=[1,0.1])
    plt.tight_layout()
    plt.savefig(out_name + '.png')


#########################
# Models
#########################

# load model
model = ResNet50(weights='imagenet')

model = InceptionV3(weights='imagenet')


# model = VGG16(weights='imagenet', include_top=False)

# pre-processing for inception model only
def preprocess_input(x):
    x /= 255.
    x -= 0.5
    x *= 2.
    return x

# get all available images
img_names_on_disk = os.listdir(path_images)
img_paths_on_disk = [path_images + x for x in img_names_on_disk]

# loop through all images, make a classification and plot
for img_path in img_paths_on_disk:
    img_name = img_path.split("/")[-1]
    # img = image.load_img(img_path, target_size=(224, 224))
    img = image.load_img(img_path, target_size=(299, 299))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    preds = model.predict(x)
    preds_dec = decode_predictions(preds)
    print('Predicted:', preds_dec)

    # save predictions in data frame
    pred_labels = [x[1] for x in preds_dec[0]]
    pred_scores = [x[2] for x in preds_dec[0]]
    preds_df = pd.DataFrame({'Species' : pred_labels, 'Score': pred_scores})

    plot_pred_vs_image(img,preds_df,path + 'models/IncepV3_' + img_name.strip('.JPG'))











# plot graph
#from keras.utils import plot_model
#import pydot
#pydot.find_graphviz = lambda: True
#plot_model(model, to_file= path + 'models/model.png')



#from IPython.display import SVG
#from keras.utils.vis_utils import model_to_dot
#
#SVG(model_to_dot(model).create(prog='dot', format='svg'))
