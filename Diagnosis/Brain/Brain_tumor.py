# -*- coding: utf-8 -*-
# 參考: https://github.com/ferasbg/glioAI

import numpy as np 
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input

import warnings
warnings.filterwarnings('ignore')
from tensorflow.python.keras.models import load_model

class Brain_tumor():
    def __init__(self, img_path):
        ## load saved model
        #self.model = load_model('./models/tumor_prediction.h5')
        self.model = load_model('./Diagnosis/Brain/models/tumor_prediction.h5')

        # route to any of the labaled malignant images that model hasn't seen before 
        #img_path = ('../../dataset/yes/Y42.jpg')
        self.img = tf.keras.preprocessing.image.load_img(img_path, target_size=(224,224))
        x = image.img_to_array(self.img)
        x = np.expand_dims(x, axis = 0)
        self.img_data = preprocess_input(x)

    def predict(self):
        # make prediction
        rs = self.model.predict(self.img_data)

        #print(rs)
        #print(rs[0][0])
        #print(rs[0][1])

        if rs[0][0] >= 0.9:
            prediction = 'Normal'
        elif rs[0][0] <= 0.9:
            prediction = 'Tumor!'
        #print(prediction)
        return prediction

if __name__ == '__main__':
    test = Brain_tumor('../../Data/Brain/8 no.jpg')
    print(test.predict())




