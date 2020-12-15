# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 09:05:36 2020

@author: baile
"""

from aubio import source, pitch
import numpy as np
from scipy.stats import iqr



def read_frequencies(filename):
    #we will use the original amount of samples in the file
    #samplerate = 44100
    s = source(filename)    
    tolerance = 0.8
    
    #yin is a frequency estimation algorithm
    pitch_o = pitch("yin", samplerate = s.samplerate)
    pitch_o.set_unit("Hz")
    pitch_o.set_tolerance(tolerance)
    
    pitches = []
    confidences = []
        
    # total number of frames read
    total_frames = 0
    while True:
        samples, read = s()
        this_pitch = pitch_o(samples)[0]
        
        confidence = pitch_o.get_confidence()
        
            
        pitches += [this_pitch]
        confidences += [confidence]
        total_frames += read
        if read < s.hop_size: break
    
    
    #close that audio when we are done with it 
    s.close()
    
    return pitches, confidences
 
#we will remove high outliers using the IQR * 1.5 rule for outliers.
def remove_outliers(recording, confidences):
    #cast to a numpy array
    this_recording = np.array(recording)
    
    #find the IQR and the third quartile
    my_iqr = iqr(this_recording)
    q3 = np.quantile(this_recording, 0.75)

    pitches_ret_val = []
    confidences_ret_val  = []
    
    #remove any points that are above the third quartile by more than 1.5 * the IQR 
    #we are only removing high outliers because those seem to be the result of aubio problems... we want to keep low outliers for now
    for index in range(len(recording)):
     #   print(recording)
     if (recording[index] < (1.5 * my_iqr + q3)):
         pitches_ret_val.append(recording[index])
            
         #keep the confidences in line with the pitches
         confidences_ret_val.append(confidences[index])
            
            
    return pitches_ret_val, confidences_ret_val
  
#remove unnecessary, inaccurate, or presumably unhelpful data
def clean_arrays(pitches, confidences):
    #first, if there are non-audible frequencies, we will remove those right away because we know they can't weigh into a person's perspective 
    these_pitches = []
    these_confidences = []
    
    #delete too high or too low notes
    for index in range(len(pitches)):
        #if the pitch is within a reasonable range (1567 is the highest pitch a human can sing, and 20 the lowest a human can hear), we will add it to a temporary list
        if (pitches[index] > 20) and (pitches[index] < 1567):
            these_pitches.append(pitches[index])
            these_confidences.append(confidences[index])
            index -= 1
        
    pitches = these_pitches
    confidences = these_confidences
    
     #first, we will try to reduce some of the "noise" in the background of the recordings
    these_pitches, these_confidences = remove_outliers(pitches, confidences)
    
    pitches = these_pitches
    confidences = these_confidences
    
    
    
    # next, we will strip zeros from beginning and end of each list 
    while (len(pitches) > 0) and (pitches[0] == 0) :
        pitches.pop(0)
        confidences.pop(0)
            
    while (len(pitches) > 0) and  (pitches[-1] == 0) :
        pitches.pop(-1)
        confidences.pop(-1)
    
    return pitches, confidences
    
    

#here, we are trying to make them all the same length to be fed into the machine learning algorithm
def make_arrays_same_length(pitches, confidences):
    pitches, confidences = clean_arrays(pitches, confidences)
    #if we need to delete any frequencies
    if len(pitches) > 1000:    
             
        #we will delete the frequencies with the lowest confidence 
        total_to_delete = len(pitches) - 1000
        
        while total_to_delete > 0:
            #print("current confidence:" , sum(confidences) / len(confidences))
            #find the frequency that we are the least confident about 
            min_value = min(confidences)
            min_index = confidences.index(min_value)
                
            #we will delete that value from the confidences and the pitches array so that they don't get out of sync
            del confidences[min_index]
            del pitches[min_index]
            
            total_to_delete -= 1
            
            
    # if we need to add any frequencies       
    elif len(pitches) < 1000:
        total_added = 0 
        total_to_add = 1000 - len(pitches)
        last_confidence = 1

        #we will add repeats of the frequencies with the highest confidence 
        while total_added < total_to_add:
            current_confidence = sum(confidences) / len(confidences)
            
            #if we are starting to add low confidence values, we will reset and start adding the high confidence values again
            if current_confidence < last_confidence:
                temp_confidences = confidences.copy()
            
            
            #find the frequency that we are the most confident about 
            max_value = max(temp_confidences)
            max_index = temp_confidences.index(max_value)
            
         
            #we will add that value to the confidences array again
            confidences.insert(max_index, max_value)
            pitches.insert(max_index, pitches[max_index])
            
            #so we don't keep getting the same value as the max 
            temp_confidences[max_index] = 0
            
            #keep it in line with the confidences
            temp_confidences.insert(max_index, 0)
    
            total_added += 1
            last_confidence = current_confidence
            
    return pitches
  
#call all of our other functions from here - takes the filename of an mp3 file, processes the audio, and returns a list of length 1000
def get_freq_from_mp3(filename):
    pitches, confidences = read_frequencies(filename)
    shortened_pitches = make_arrays_same_length(pitches, confidences)
    return shortened_pitches
    


#read in the 88 training files and write them to a csv
def read_training_data():
    #write all of our training data to a csv file
    f = open("C://Users//baile//OneDrive//Desktop//Classes//Fall2020Classes//Thesis//Please_Dont_Sing//complete_audio_freqs.csv", "w")
    csv_titles= []
    for i in range(1000):
        csv_titles.append("frequency{}".format(i))
    
    f.write(','.join(csv_titles))
    f.write('\n')
    
    for recording_num in range(0, 88):
        filename = 'C://Users//baile//OneDrive//Desktop//Classes//Fall2020Classes//Thesis//Please_Dont_Sing//www//recording' + str(recording_num) + '.mp3'
        cleaned_freqs = get_freq_from_mp3(filename)
        cleaned_freqs_strings = ["%.2f" % number for number in cleaned_freqs]
        f.write(','.join(cleaned_freqs_strings))
        f.write('\n')
        print("Wrote Index {} to file".format(recording_num))
        
    f.close()
    

#we only want to run the last function when this file is run, NOT When it is imported
if __name__ == "__main__":
    read_training_data()





