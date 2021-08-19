from __future__ import print_function

import keras
from keras.callbacks import LearningRateScheduler as LRS

from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Activation, Reshape
from keras.layers.normalization import BatchNormalization as BN
from keras.layers import GaussianNoise as GN
from keras.optimizers import SGD

from keras.preprocessing.image import ImageDataGenerator


batch_size = 100
num_classes = 10
epochs = 75

# the data, shuffled and split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()


print(x_train.shape)

# Mandatory to use ImageDataGenerator, it expects 4D Tensors
x_train = x_train.reshape(60000,28,28,1)
x_test = x_test.reshape(10000,28,28,1)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')

# Normalize [0..255]-->[0..1]
x_train /= 255
x_test /= 255

print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)


## Data Augmentation with an ImageGenerator
datagen = ImageDataGenerator(
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=False,
    zoom_range=0.2,
    rotation_range = 10)


## Model, note the reshape
model = Sequential()
model.add(Reshape(target_shape=(784,), input_shape=(28,28,1)))
model.add(GN(0.1))

model.add(Dense(1024))
model.add(BN())
model.add(GN(0.1))
model.add(Activation('relu'))

model.add(Dense(1024))
model.add(BN())
model.add(GN(0.1))
model.add(Activation('relu'))


model.add(Dense(num_classes, activation='softmax'))

model.summary()
##

sgd=SGD(lr=0.1, decay=0.0, momentum=0.0)

def scheduler(epoch):
    if epoch < 25:
        return .1
    elif epoch < 50:
        return 0.01
    else:
        return 0.001

set_lr = LRS(scheduler)


model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])



history=model.fit_generator(datagen.flow(x_train, y_train,batch_size=batch_size),
                            steps_per_epoch=len(x_train) / batch_size, 
                            epochs=epochs,
                            validation_data=(x_test, y_test),
                            callbacks=[set_lr],
                            verbose=1)


score = model.evaluate(x_test, y_test, verbose=0)

print('Test loss:', score[0])
print('Test accuracy:', score[1])