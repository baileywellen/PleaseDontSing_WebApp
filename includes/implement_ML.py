# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 10:51:30 2020

@author: baile
"""

from sklearn.linear_model import Ridge 
import pandas as pd 
import numpy as np
from includes.read_mp3 import get_freq_from_mp3
import math

#the below libraries are used to read the csv file from Google Drive, because Heroku wasn't picking it up when I uploaded the csv
from io import StringIO
import requests

#takes a dataframe of the training data, trains with all of our available data, and returns the model
def train_model(training_data):
    #read data into a dataframe 
    features = training_data.drop(['z_score'], axis = 1)
    output = training_data[['z_score']]

    ridge_reg = Ridge()
    #fit the model on ALL of our available data 
    ridge_reg.fit(features, output)
    return ridge_reg
    
#calculate the number of half steps from the tuning pitch (440) to the note
#returns a double
#https://pages.mtu.edu/~suits/NoteFreqCalcs.html
def calculate_num_steps(freq):
    #base is the base of the logarithm. In frequency calculations, this is a constant which is the 12th root of 2 
    base = 2 ** (1.0 / 12) 
    ret_val = math.log(freq / 440, base) 
    
    return ret_val

#turn a list of frequencies into the format we need to enter it into the regression
def transform_data(list_of_freqs):
    #aggregate the data into 25 chunks 
    num_per_section = int(len(list_of_freqs) / 25)
    grouped_frequencies = []
    for chunk in range(25):
        average = sum(list_of_freqs[(chunk * num_per_section) : (chunk * num_per_section) + num_per_section]) / num_per_section
        grouped_frequencies.append(average)
    
    #calculate the number of half steps between each frequency and the tuning A 
    differences = [calculate_num_steps(value) for value in grouped_frequencies]
        
    return differences

def assign_class(z_score):
    ret_val = ""
    if z_score < -0.407:
        ret_val = "bad"
    elif z_score > 0.484:
        ret_val = "good"
    else:
        ret_val = "okay"
        
    return ret_val


#predict a z score of a new mp3 file 
def evaluate_recording(name_of_input):

    #first, train the model on our csv input (which is located in Google Drive )
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    #use the sharing link from Google Drive and format it so it reads directly to the csv (instead of the sharing page )
    url = "https://drive.google.com/file/d/1QkeCYo7BEfiZMMzaZPYOlZZeOM4iYWg_/view?usp=sharing"
    path = 'https://drive.google.com/uc?export=download&id='+url.split('/')[-2]
    #read the requests from that link
    path_requests = requests.get(path, headers= headers).text
    #read the data into a pandas dataframe
    training_data = pd.read_csv(StringIO(path_requests), sep=",")
    
    ridge_reg = train_model(training_data)
    
    pred = []
    valid_input = False 
    #next, get the pitches of the recording we are evaluating
    pitches = get_freq_from_mp3(name_of_input)
    
    #we will only calculate a prediction if the input was valid
    if len(pitches) > 0:
        clean_data = transform_data(pitches)
    
        #create a prediction
        pred = ridge_reg.predict(np.array(clean_data).reshape(1,-1))
    
        valid_input = True
   
    
    return pred, valid_input   
    
    
    
 
    
if __name__ == "__main__":   
     evaluate_recording("C:\\Users\\baile\\OneDrive\\Desktop\\Classes\\Fall2020Classes\\Thesis\\pds_webapp\\test.wav")