# -*- coding: utf-8 -*-
# 參考: https://github.com/brandons209/dermatologist-CNN

import numpy as np
from tensorflow.python.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
IMG_WIDTH, IMG_HEIGHT = 150, 150

import warnings
warnings.filterwarnings('ignore')

class Chest_classification():
    def __init__(self, img_path):
        ## load saved model
        #self.model = load_model('./models/sequential_1214_0812')
        self.model = load_model('./Diagnosis/Chest/models/sequential_1214_0812')

        img = load_img(img_path, target_size=(IMG_WIDTH, IMG_HEIGHT))
        img = img_to_array(img)
        self.img = np.expand_dims(img, axis=0)


    def predict(self):
        rs = self.model.predict(self.img)
        #print(rs[0][0])
        if rs[0][0] >= 0.5:
            prediction = 'Pneumonia!'
        else:
            prediction = 'Normal'
        #print(prediction)
        return prediction

if __name__ == '__main__':
    test = Chest_classification('../../Data/Chest/person1_bacteria_2.jpeg')
    print(test.predict())




