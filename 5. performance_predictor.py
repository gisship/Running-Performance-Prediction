import pickle
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_lottie import st_lottie
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import requests
import warnings
warnings.filterwarnings("ignore")

# Global presentation
st.set_page_config(page_title = "Running Performance Predictor", page_icon = ":runner:", layout = "wide")
st.subheader("Welcome to the only running performance predictor based exclusively on real world data!")
st.write("Let's get started! Please fill in the information below to get your performance prediction.")
st.write("---")

# Height, weight, gender
col1, col2, col3 = st.columns(3)

with col1:
    height = st.number_input("Height (cm)*", min_value = 0, max_value = 300, step = 1)    
with col2:
    weight = st.number_input("Weight (kg)*", min_value = 0, max_value = 300, step = 1)
with col3:
    gender = st.selectbox("Gender*", ("M", "F"))

# Distance of interest, projected age
distance_codes = np.array([["800m", "1000m", "1500m", "3000m", "5km", "10km", "15km", "Half-Marathon", "Marathon", "100km"],
                           [0.8, 1.0, 1.5, 3.0, 5.0, 10.0, 15.0, 21.097, 42.195, 100.0]])

col1, col2 = st.columns(2) 

with col1:
    pred_dist = st.selectbox("Select the distance on which to predict future performance*", tuple(distance_codes[0,:]))
with col2:
    age_pred= st.number_input("How old will you be?*", min_value = 0, max_value = 150, step = 1)

# Collect PBs and relevant associated information
perf_dist = []
hours, minutes, seconds = [], [], []
delta_age_perf = []
counter = 1
check_pb = st.checkbox("Check to add a personal best*", key = "check_pb" + str(counter))

while (counter < distance_codes.shape[1]-1) & check_pb:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        perf_dist.append(st.selectbox("Distance*", 
                                      tuple([dist for dist in distance_codes[0,:] 
                                             if (dist not in perf_dist) & (dist != pred_dist)]), 
                                      key = "perf_dist" + str(counter)))
    with col2:
        hours.append(st.number_input("Hours**", min_value = 0, max_value = 20, step = 1, key = "hours" + str(counter)))
    with col3:
        minutes.append(st.number_input("Minutes**", min_value = 0, max_value = 60, step = 1, key = "minutes" + str(counter)))
    with col4:
        seconds.append(st.number_input("Seconds**", min_value = 0, max_value = 60, step = 1, key = "seconds" + str(counter)))
    with col5:
        delta_age_perf.append(st.number_input("How old is this performance (years)?", min_value = 0, max_value = 50, step = 1, 
                                              key = "delta_age_perf" + str(counter)))
    
    counter += 1
    check_pb = st.checkbox("Add another a personal best", key = "check_pb" + str(counter))

# Random forest regression
get_prediction_rf = st.button("Get your prediction")

if get_prediction_rf:    
    # Fill in input data frame
    perf_time = [hours[i]*3600 + minutes[i]*60 + seconds[i] for i in range(len(perf_dist))]
    inputs_df = pd.DataFrame(0, index = range(len(perf_dist)), columns = ["PredDist", "AgePred", "PerfTime", "PerfDist", 
                                                                          "DeltaAgePerf", "Height", "Weight", "Gender",
                                                                          "Alpha", "Beta", "IsAlphaBeta"])
    inputs_df.AgePred = age_pred
    inputs_df.PredDist = float(distance_codes[1, np.where(distance_codes == pred_dist)[1][0]])
    inputs_df.PerfTime = perf_time
    inputs_df.PerfDist = [float(distance_codes[1, np.where(distance_codes == dist)[1][0]]) for dist in perf_dist]
    inputs_df.DeltaAgePerf = delta_age_perf
    inputs_df.Height = height 
    inputs_df.Weight = weight
    inputs_df.Gender = (gender == "M")*1

    # When possible, compute alpha and beta    
    if inputs_df.shape[0] >= 2:
        t = perf_time
        d = [float(distance_codes[1, np.where(distance_codes == dist)[1][0]]) for dist in perf_dist]
        reg = LinearRegression()
        reg.fit(np.log(d).reshape(-1,1), np.log(t).reshape(-1,1))        
        inputs_df.Alpha = reg.intercept_[0]
        inputs_df.Beta = reg.coef_[0][0]
        inputs_df.IsAlphaBeta = 1
    else:
        inputs_df.Alpha = 0
        inputs_df.Beta = 0
        inputs_df.IsAlphaBeta = 0
    
    # Make and format prediction  
    if (height == 0) | (weight == 0) | (age_pred == 0) | (~check_pb & counter == 1) | ((hours == 0) & (minutes == 0) & (seconds == 0)):
        st.write("Please make sure you entered all the required arguments")
    
    else:
        inputs = inputs_df.values
        f = open("rf_regressor.pckl", "rb")
        reg = pickle.load(f)
        f.close()    
        selector = np.abs(inputs_df.PerfDist - inputs_df.PredDist)
        selector = np.where(selector == np.min(selector))[0]        
        pred_time = reg.predict(inputs)#[selector]
        h_pred = int(pred_time // 3600)
        min_pred = int((pred_time - h_pred*3600) // 60)
        s_pred = int((pred_time - h_pred*3600 - min_pred*60))
        
        if h_pred < 10:
            h_pred = "0"+str(h_pred)
        else:
            h_pred = str(h_pred)
        if min_pred < 10:
            min_pred = "0"+str(min_pred)
        else:
            min_pred = str(min_pred)
        if s_pred < 10:
            s_pred = "0"+str(s_pred)
        else:
            s_pred = str(s_pred)
        
        st.write(h_pred+":"+min_pred+":"+s_pred)

# Footnotes
st.write("---")
st.write("*Note 1: The prediction assumes that the training plan you have intended to follow for your future race is similar in terms of intensity to those that led to your previous personal bests.*")
st.write("*Note 2: For higher prediction accuracy, please make sure that your personal bests are less than 3 years old.*")
st.write("*Note 3: The more personal bests you enter, the more the displayed prediction will match your runner profile.*")
st.write("**required information*")
st.write("***cannot be all equal to 0*")