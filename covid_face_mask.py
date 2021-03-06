import os
os.environ['KAGGLE_USERNAME'] = "*********" # username from the json file
os.environ['KAGGLE_KEY'] = "************" # key from the json file
!kaggle datasets download -d prithwirajmitra/covid-face-mask-detection-dataset # api copied from kaggle
!unzip -qq covid-face-mask-detection-dataset.zip
!rm -r covid-face-mask-detection-dataset.zip

# Commented out IPython magic to ensure Python compatibility.
from tensorflow.keras.models import Sequential 
from tensorflow.keras import layers,models
from tensorflow.keras.layers import Conv2D, MaxPooling2D , Dropout , Flatten , Dense 
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import tensorflow_hub as hub
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
# %matplotlib inline

main_dir = "/content/New Masks Dataset"
train_dir = "/content/New Masks Dataset/Train"
test_dir = "/content/New Masks Dataset/Test"
valid_dir = "/content/New Masks Dataset/Validation"
 
train_mask_dir = os.path.join(train_dir,"Mask")
train_nonmask_dir = os.path.join(train_dir,"Non Mask")

train_mask_name = os.listdir(train_mask_dir)
print(train_mask_name[:20])
 
train_nonmask_name = os.listdir(train_nonmask_dir)
print(train_nonmask_name[:20])

import random
nrows = 5
ncols = 5
plt.figure(figsize=(12,12))
 
mask_pic=[]
for i in train_mask_name[0:10]:
    mask_pic.append(os.path.join(train_mask_dir,i))
    
nonmask_pic = []    
for i in train_nonmask_name[0:10]:
    nonmask_pic.append(os.path.join(train_nonmask_dir,i))
    
print(mask_pic)
print(nonmask_pic)
 
merge_list = mask_pic+nonmask_pic
random.shuffle(merge_list)
for i in range(0 , len(merge_list)):
    data=merge_list[i].split('/',4)[4]
    sp = plt.subplot(nrows,ncols,i+1)
    sp.axis('Off')
    image = mpimg.imread(merge_list[i])
    sp.set_title(data,fontsize = 10)
    plt.imshow(image,cmap='gray')
    
plt.show()    
image=mpimg.imread(merge_list[1])
image.shape

train_datagen = ImageDataGenerator(rescale = 1./255,
                                  zoom_range = 0.1,
                                  rotation_range=39,
                                  horizontal_flip=True,
                                  vertical_flip=False,
                                  )
test_datagen = ImageDataGenerator(rescale=1./255)
valid_datagen = ImageDataGenerator(rescale=1./255)
 
train_datagen = train_datagen.flow_from_directory(train_dir,
                                                 target_size=(200,200),
                                                 batch_size =36 , #how much image is insert at a time
                                                 class_mode='binary'#what type of classification is
                                                 )
 
test_datagen = test_datagen.flow_from_directory(test_dir,
                                                 target_size=(200,200),
                                                 batch_size =36 , #how much image is insert at a time
                                                 class_mode='binary'#what type of classification is
                                                 )
 
valid_datagen = valid_datagen.flow_from_directory(valid_dir,
                                                 target_size=(200,200),
                                                 batch_size =36 , #how much image is insert at a time
                                                 class_mode='binary'#what type of classification is
                                                 )

train_datagen.class_indices

from tensorflow.keras.applications.inception_v3 import  *
first=InceptionV3(input_shape=(200,200,3),include_top=False,weights='imagenet')
for layer in first.layers:
  layer.trainable=False

#first.summary()

#x=MaxPooling2D(pool_size=(2,2))(first.output)
#x=Dropout(0.4)(x)

x=layers.Flatten()(first.output)
x=layers.Dense(250,activation='relu')(x)
x=layers.Dropout(0.5)(x)
x=layers.Dense(1,activation='sigmoid')(x)

model = models.Model(first.input,x)
model.summary()

model.compile(Adam(lr=0.001),
              loss='binary_crossentropy'
              ,metrics='accuracy')

history=model.fit(train_datagen,
                 epochs=30,
                 validation_data=valid_datagen
                 )
 
N = np.arange(0, 30)

model.save("/content/drive/MyDrive/Colab Notebooks/model.h5")

plt.plot(N,history.history['loss'])
plt.plot(N,history.history['val_loss'])
plt.legend(['training','validation'])
plt.title('Training and validation loss')
plt.xlabel('epoch')
plt.savefig("Loss.png")

plt.plot(N,history.history['accuracy'])
plt.plot(N,history.history['val_accuracy'])
plt.legend(['training','validation'])
plt.title('Training and validation accuracy')
plt.xlabel('epoch')
plt.savefig("Accuracy.png")

test_loss , test_acc = model.evaluate(test_datagen)

print(test_loss)
print(test_acc)
