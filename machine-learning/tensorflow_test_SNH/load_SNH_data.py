# import modules
from keras.preprocessing.image import ImageDataGenerator, array_to_img
from keras.preprocessing.image import img_to_array, load_img
from PIL import Image


# path to SNH data
path_snh = "D:/Studium_GD/Zooniverse/Data/SNHuntersInception/images/"


image_shape = (3, 20, 20)
# import images
def import_one_image(path):
    # this is a PIL image
    img = load_img(path)
    # this is a Numpy array with shape (3, x, y)
    x = img_to_array(img)
    # this is a Numpy array with shape (1, 3, x, y)
    x = x.reshape((1,) + x.shape)
    return x


test_image = "real/1000142620265807300_56614.278_29315398_157_diff.jpeg"
x = import_one_image(path_snh + test_image)


# data augmentation
datagen = ImageDataGenerator(
        rotation_range=360,
        width_shift_range=0.01,
        height_shift_range=0.01,
        shear_range=0.01,
        zoom_range=0.01,
        horizontal_flip=True,
        fill_mode='nearest')


# the .flow() command below generates batches of randomly transformed images
# and saves the results to the `preview/` directory
i = 0
for batch in datagen.flow(x, batch_size=1,
                          save_to_dir=path_snh + 'test', save_prefix='aug', save_format='jpeg'):
    i += 1
    if i > 20:
        break  # otherwise the generator would loop indefinitely



from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense

model = Sequential()
model.add(Conv2D(8, (2, 2), input_shape=image_shape))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())  # this converts our 3D feature maps to 1D feature vectors
model.add(Dense(8))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])


batch_size = 16

# this is the augmentation configuration we will use for training
train_datagen = datagen

# this is the augmentation configuration we will use for testing:
# only rescaling
test_datagen = ImageDataGenerator(rescale=1)

# this is a generator that will read pictures found in
# subfolers of 'data/train', and indefinitely generate
# batches of augmented image data
train_generator = train_datagen.flow_from_directory(
        path_snh + 'real/',  # this is the target directory
        target_size=(20, 20),  # all images will be resized to 150x150
        batch_size=batch_size,
        class_mode='binary')  # since we use binary_crossentropy loss, we need binary labels

# this is a similar generator, for validation data
validation_generator = test_datagen.flow_from_directory(
        path_snh + 'bogus',
        target_size=(20, 20),
        batch_size=batch_size,
        class_mode='binary')


model.fit_generator(
        train_generator,
        steps_per_epoch=2000 // batch_size,
        epochs=50,
        validation_data=validation_generator,
        validation_steps=800 // batch_size)
model.save_weights(path_snh + 'first_try.h5')  # always save your weights after training or during training





from __future__ import print_function
import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D

batch_size = 32
num_classes = 10
epochs = 200
data_augmentation = True

# The data, shuffled and split between train and test sets:
(x_train, y_train), (x_test, y_test) = cifar10.load_data()



