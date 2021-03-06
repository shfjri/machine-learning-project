# -*- coding: utf-8 -*-
"""Submission Akhir BPML_Muhammad Sholih Fajri.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B0WGMWJAeFNienGyLOT_pAJChmvcx-ju
"""

# Import Library yang dibutuhkan

import numpy as np
import tensorflow as tf
import keras
import os
import zipfile

from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D, BatchNormalization
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import RMSprop, Adamax, Nadam, SGD, Adam 
from keras.callbacks import ModelCheckpoint
from keras.applications import VGG16

from matplotlib import pyplot as plt
from matplotlib import image as img

from google.colab import files

# Menginstall kaggle agar bisa langsung mendownload dataset di colab

!pip install -q kaggle

# Mengupload json file API Token user kaggle

files.upload() #upload kaggle.json

!pip install -q kaggle
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!ls ~/.kaggle
!chmod 600 /root/.kaggle/kaggle.json

# Mendownload dataset yang digunakan dengan API Command kaggle

!kaggle datasets download -d alessiocorrado99/animals10

# Mengekstrak file zip dataset

local_zip = 'animals10.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()

# Mengetahui folder kelas dataset

os.listdir('/content/raw-img')

# Path dataset yang digunakan

source_path = '/content/raw-img'

# Menginisialisasi generator untuk augmentasi dan mengaplikasikannya untuk dataset training dan validasi

augmentation_gen = ImageDataGenerator(
    rescale=1./255,
    rotation_range = 20,
    horizontal_flip = True,
    shear_range = 0.2,
    fill_mode = 'nearest',
    validation_split = 0.2
)
 
train_gen = augmentation_gen.flow_from_directory(
    source_path,
    target_size = (224,224),
    color_mode = 'rgb',
    batch_size = 32,
    class_mode = 'categorical',
    shuffle = True,
    subset = 'training'
) 
val_gen = augmentation_gen.flow_from_directory(
    source_path,
    target_size=(224,224),
    color_mode = 'rgb',
    batch_size = 32,
    class_mode='categorical',
    shuffle=True,
    subset = 'validation'
)

# Membuat model dengan pre-trained model yaitu VGG dan menambahkan layer berikutnya sesuai kebutuhan

vgg16 = VGG16(include_top=False, weights='imagenet', input_shape=(224,224,3))

model = Sequential()
model.add(vgg16)
model.add(Flatten())
model.add(Dropout(0.2))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(10, activation='softmax'))

# Menentukan optimizer dan callback beserta parameter-parameternya

sgd = SGD(learning_rate=0.001, momentum=0.9)
model.compile(loss = 'categorical_crossentropy', 
              optimizer = 'sgd', 
              metrics = ['accuracy'])

filepath = 'animals.h5'

checkpoint = ModelCheckpoint(filepath, 
                             monitor = 'val_accuracy', 
                             verbose = 1, 
                             save_best_only = True, 
                             mode = 'max')

callback_list = [checkpoint]

model.summary()

# Melatih model dengan data training dan validasi

hist = model.fit(train_gen,
                 epochs=15,
                 steps_per_epoch=100,
                 validation_data=val_gen,
                 callbacks=callback_list,
                 verbose=1)

# Membuat plot grafik akurasi dan loss pada model selama training

n = len(hist.history['loss']) + 1
ep = np.arange(1, n, 1)

fig, ax = plt.subplots(1, 2, figsize=(12,6))

ax[0].set_xlabel('Epoch', style='italic', size=12, color='b')
ax[0].set_ylabel('Accuracy', style='italic', size = 12, color = 'c')
ax[0].plot(ep, hist.history['accuracy'], color = 'g')
ax[0].plot(ep, hist.history['val_accuracy'], color = 'c')
ax[0].tick_params(axis='x', labelcolor='b')
ax[0].tick_params(axis='y', labelcolor='c')
ax[0].legend(['Training Accuracy', 'Validation Accuracy'], loc='lower right')

ax[1].set_xlabel('Epoch', style='italic', size=12, color='b')
ax[1].set_ylabel('Loss', style = 'italic', size = 12, color = 'r')
ax[1].plot(ep, hist.history['loss'], color = 'r')
ax[1].plot(ep, hist.history['val_loss'], color = 'm')
ax[1].tick_params(axis='x', labelcolor='b')
ax[1].tick_params(axis='y', labelcolor='r')
ax[1].legend(['Training Loss', 'Validation Loss'], loc='upper right')

# from tensorflow.lite import TFLiteConverter

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)

"""Referensi

https://www.tensorflow.org/lite/convert/python_api

https://keras.io/api/optimizers/sgd/

https://www.freecodecamp.org/news/how-to-pick-the-best-learning-rate-for-your-machine-learning-project-9c28865039a8/

https://ruder.io/optimizing-gradient-descent/

https://machinelearningmastery.com/understand-the-dynamics-of-learning-rate-on-deep-learning-neural-networks/

https://keras.io/api/applications/vgg/#vgg16-function

https://www.kaggle.com/general/74235

https://medium.com/analytics-vidhya/how-to-fetch-kaggle-datasets-into-google-colab-ea682569851a

https://www.kaggle.com/aman193070021/cnn-vgg-animals10
"""