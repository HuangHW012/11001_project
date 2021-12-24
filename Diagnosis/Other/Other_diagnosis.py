# -*- coding: utf-8 -*-
# 參考: https://github.com/kritikaparmar-programmer/HealthCheck
# [Kaggle]
# DIABETES: https://www.kaggle.com/uciml/pima-indians-diabetes-database
# STROKE: https://www.kaggle.com/fedesoriano/stroke-prediction-dataset

import pickle
import numpy as np
import joblib
from tensorflow.keras.models import load_model
from PIL import Image
import tensorflow as tf
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

class Other_diagnosis():
    def __init__(self, diagnosis_type = None, data = None):
        self.diagnosis_type = diagnosis_type
        ## load saved model
        if self.diagnosis_type == 'DIABETES':
            #self.model = pickle.load(open('./models/diabetes-model.pkl', 'rb'))
            self.model = pickle.load(open('./Diagnosis/Other/models/diabetes-model.pkl', 'rb'))
        elif self.diagnosis_type == 'STROKE':
            #self.model = joblib.load('./models/model.pkl')
            self.model = joblib.load('./Diagnosis/Other/models/model.pkl')
        self.data = data

    def predict(self):
        prediction = None
        if self.diagnosis_type == 'DIABETES':
            # [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]])
            #self.data = np.array([[6, 148, 72, 35, 0, 50, 0.627, 50]])
            prediction = self.model.predict(self.data)
            #print(prediction)
            if prediction[0] == 1:
                prediction = 'Diabetes!'
            else:
                prediction = 'Normal'
        elif self.diagnosis_type == 'STROKE':
            # [[gender, age, hypertension, heart_disease, ever_married, work_type, Residence_type, avg_glucose_level, bmi, smoking_status])
            stroke_data= pd.read_csv('./Diagnosis/Other/datasets/stroke_data.csv')
            min_gender, max_gender = 0, 1
            min_age, max_age = stroke_data['age'].min(), stroke_data['age'].max()
            min_hypertension, max_hypertension = stroke_data['hypertension'].min(), stroke_data['hypertension'].max()
            min_heart_disease, max_heart_disease = stroke_data['heart_disease'].min(), stroke_data['heart_disease'].max()
            min_ever_married, max_ever_married = 0, 1
            min_work_type, max_work_type = 0, 4
            min_Residence_type, max_Residence_type = 0, 1
            min_avg_glucose_level, max_avg_glucose_level = stroke_data['avg_glucose_level'].min(), stroke_data['avg_glucose_level'].max()
            min_bmi, max_bmi = stroke_data['bmi'].min(), stroke_data['bmi'].max()
            min_smoking_status, max_smoking_status = 0, 3

            self.data[0][0] = (self.data[0][0] - min_gender) / (max_gender - min_gender)
            self.data[0][1] = (self.data[0][1] - min_age) / (max_age - min_age)
            self.data[0][2] = (self.data[0][2] - min_hypertension) / (max_hypertension - min_hypertension)
            self.data[0][3] = (self.data[0][3] - min_heart_disease) / (max_heart_disease - min_heart_disease)
            self.data[0][4] = (self.data[0][4] - min_ever_married) / (max_ever_married - min_ever_married)
            self.data[0][5] = (self.data[0][5] - min_work_type) / (max_work_type - min_work_type)
            self.data[0][6] = (self.data[0][6] - min_Residence_type) / (max_Residence_type - min_Residence_type)
            self.data[0][7] = (self.data[0][7] - min_avg_glucose_level) / (max_avg_glucose_level - min_avg_glucose_level)
            self.data[0][8] = (self.data[0][8] - min_bmi) / (max_bmi - min_bmi)
            self.data[0][9] = (self.data[0][9] - min_smoking_status) / (max_smoking_status - min_smoking_status)

            prediction = self.model.predict(self.data)
            if prediction[0] == 1:
                prediction = 'Stroke!'
            else:
                prediction = 'Normal'
        return prediction

if __name__ == '__main__':
    test = Other_diagnosis('STROKE')
    print(test.predict())




