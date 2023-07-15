import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing.image import img_to_array, load_img
from keras.preprocessing.image import array_to_img  # Import from 'keras.preprocessing.image.utils'





datagen = ImageDataGenerator(rotation_range=40,
                            width_shift_range=0.2,
                            height_shift_range=0.2,
                            shear_range=0.2,
                            zoom_range=0.2,
                            horizontal_flip=True,
                            )

img = load_img("C:/Users/Kabra/Desktop/employee/Aditya Inamdar.jpg")
x = img_to_array(img)
x=x.reshape((1,) + x.shape)
i=0

for batch in datagen.flow(x,batch_size=1,save_to_dir="C:/Users/Kabra/Desktop/employee/Aditya Inamdar",save_prefix='Aditya Inamdar',save_format='jpeg'):
    i += 1
    if i > 20:
        break
