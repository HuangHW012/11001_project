# -*- coding: utf-8 -*-
# 參考: https://github.com/brandons209/dermatologist-CNN

import numpy as np
from tensorflow.keras.models import load_model

import warnings
warnings.filterwarnings('ignore')

#size of image, inceptionv3 is 299x299, resnet50 is 224x224
img_size = 299
from keras.preprocessing import image as image_processor
#processes single image to test in test_model.py. Need to expand dimensions so to get a tensor with shape (1, img_size, img_size, 3)
def process_single_image(img_path):
    img = image_processor.load_img(img_path, target_size=(img_size,img_size))
    return np.expand_dims(image_processor.img_to_array(img), axis=0)

class Skin_classification():
    def __init__(self, img_path):
        ## load saved model
        #self.model = load_model('./models/skin_cancer_full_model_sample.h5')
        self.model = load_model('./Diagnosis/Skin/models/skin_cancer_full_model_sample.h5')

        # store image path
        self.img_path = img_path

    def predict(self):
        diease_names = ['Melanoma', 'Nevus', 'Seborrheic Keratosis']
        return diease_names[np.argmax(self.model.predict(process_single_image(self.img_path)))]

if __name__ == '__main__':
    test = Skin_classification('../../Data/Skin/ISIC_0000336.jpg')
    print(test.predict())




