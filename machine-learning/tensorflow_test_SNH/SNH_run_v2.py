##########################################
# Train a simple CNN using Keras
# with Tensorflow back-end on SH data
##########################################

# load modules
import keras
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator, array_to_img
from keras.preprocessing.image import img_to_array, load_img
import numpy as np
import os
from sklearn.metrics import roc_curve, roc_auc_score, accuracy_score
from sklearn.model_selection import train_test_split

# Parameters
batch_size = 32
num_classes = 2
epochs = 40
data_augmentation = False
path_snh = "D:/Studium_GD/Zooniverse/Data/SNHuntersInception/"

# function to import one image
def import_one_image(path):
    # this is a PIL image
    img = load_img(path)
    # this is a Numpy array with shape (3, x, y)
    x = img_to_array(img)
    # this is a Numpy array with shape (1, 3, x, y)
    x = x.reshape((1,) + x.shape)
    return x

# function to import images from directory
def import_dir(path):
    # store file names
    file_names = []
    # loop over all images
    for f in os.listdir(path):
        # get path
        file_names.append(f)
        # get image
        img = import_one_image(path + f)
        # append image vector
        if len(file_names) == 1:
            all_images = img
        else:
            all_images = np.vstack((all_images, img))
    return all_images


# read all real_train data and generate labels
x_data_real_train = import_dir(path_snh + 'images/real/')
y_real_train = [1 for i in range(0, x_data_real_train.shape[0])]

# read all bogus_train data and generate labels
x_data_bogus_train = import_dir(path_snh + 'images/bogus/')
y_bogus_train = [0 for i in range(0, x_data_bogus_train.shape[0])]

# read all real_test data and generate labels
x_data_real_test = import_dir(path_snh + 'test/real/')
y_real_test = [1 for i in range(0, x_data_real_test.shape[0])]

# read all bogus_test data and generate labels
x_data_bogus_test = import_dir(path_snh + 'test/bogus/')
y_bogus_test = [0 for i in range(0, x_data_bogus_test.shape[0])]


# stack train and test data together
x_data_train = np.vstack((x_data_real_train, x_data_bogus_train))
y_train = y_real_train + y_bogus_train

x_data_test = np.vstack((x_data_real_test, x_data_bogus_test))
y_test = y_real_test + y_bogus_test

# generate validation split
x_data_train_tr, x_data_train_te, y_train_tr, y_train_te = train_test_split(
        x_data_train, y_train, test_size = 0.07, random_state = 42)

# print numbers
print('x_train shape:', x_data_train_tr.shape)
print(x_data_train_tr.shape[0], 'train samples')
print(x_data_train_te.shape[0], 'validation samples')
print(x_data_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
y_train_tr = keras.utils.to_categorical(y_train_tr, num_classes)
y_train_te = keras.utils.to_categorical(y_train_te, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

# Define model architecture
model = Sequential()

model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=x_data_train_tr.shape[1:]))
model.add(Activation('relu'))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes))
model.add(Activation('softmax'))

# initiate RMSprop optimizer
opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)

# Let's train the model using RMSprop
model.compile(loss='categorical_crossentropy',
              optimizer=opt,
              metrics=['accuracy'])


# some convertions
def convert_data(x):
    x = x.astype('float32')
    x /= 255
    return x

# convert images
x_data_train_tr = convert_data(x_data_train_tr)
x_data_train_te = convert_data(x_data_train_te)
x_data_test = convert_data(x_data_test)


if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(x_data_train_tr, y_train_tr,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_data_train_te, y_train_te),
              shuffle=True)

    # evaluate model on training split
    p_test = model.predict_proba(x_data_test)
    roc_curve(y_true=y_test[:,1],y_score=p_test[:,1])
    roc_auc_score(y_true=y_test[:,1],y_score=p_test[:,1])
    p_test_label = model.p
    (x_data_test)
    accuracy_score(y_true=y_test[:,1],y_pred=p_test_label)

else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # Compute quantities required for feature-wise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(x_data_train_tr)

    # Fit the model on the batches generated by datagen.flow().
    model.fit_generator(datagen.flow(x_data_train_tr, y_train_tr,
                                     batch_size=batch_size),
                        steps_per_epoch=x_data_train_tr.shape[0] // batch_size,
                        epochs=epochs,
                        validation_data=(x_data_train_te, y_train_te))

    p_test = model.predict_proba(x_data_test)
    roc_curve(y_true=y_test[:,1],y_score=p_test[:,1])
    roc_auc_score(y_true=y_test[:,1],y_score=p_test[:,1])
