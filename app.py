import streamlit as st
from io import StringIO 
import numpy as np
import altair as alt
import pandas as pd
import altair as alt
from astropy.io import fits
from urllib.error import URLError
from utils import fits_io, noise_reduction,get_and_segregate_peaks, analyse_wavelets, classify_flare
import matplotlib.pyplot as plt
import os

# @st.cache()
def save_uploadedfile(uploadedfile):
     with open(os.path.join("cacheDir",uploadedfile.name),"wb") as f:
         f.write(uploadedfile.getbuffer())
     return st.success("Saved File:{} to cacheDir".format(uploadedfile.name))

# def fits_io(path_to_fits):
#     """
#     I/O for fits files
#     Input: Fits file/lc file path
#     Output: Time and Rate arrays
#     """
#     fits_lc = fits.open(path_to_fits)
#     fits_data = fits_lc[1].data
#     time=fits_data.field("TIME")
#     rate=fits_data.field("RATE")
#     error = fits_data.field('ERROR')
#     fracexp = fits_data.field('FRACEXP')
#     background_count = np.mean(rate)

#     return time, rate, background_count

try:
    uploaded_file = st.file_uploader("Choose a file", type=['lc','csv','ascii', 'txt', 'xls', 'xlsx', 'xlsm', 'xlsb', 'odf', 'ods' and 'odt'])
    if uploaded_file is not None:

        # To read file as bytes:
        save_uploadedfile(uploaded_file)
        time, rate, background_count = fits_io("cacheDir/%s" %uploaded_file.name)
        os.remove("cacheDir/%s" %uploaded_file.name)


        # time, rate = fits_io('data/ch2_xsm_20211022_v1_level2.lc')
        # st.write(dataframe)

        st.header("Raw data input:")
        st.write("First, we take in the light curve file and get the ‘Time’ and ‘Rate’ values from the file and store those in an array for further processing. This is the calibrated data.")
        df = pd.DataFrame({'time':time/1e8,'rates':rate})
        df = df.set_index(time/1e8)
        # df.index = time/1e8
        # fig, ax = plt.subplots()
        # ax.plot(time,rate)
        # st.pyplot(fig)
        st.line_chart(df)
        # st.write(df.astype(str))


        st.write("Background Count is %d " %background_count)


        st.header("Data after Noise Reduction")
        st.write("Now we perform noise reduction of rate using time averaging. To remove unnecessary background noise in the ‘Rate’ data, we apply a simple noise reduction technique to improve the signal to noise ratio, called ‘Time Averaging’ where we use a window length of 500 samples. We take the mean for 500 consecutive samples and store it as the denoised value. This is the filtered data that can be seen in the app.")
        filtered_time, filtered_rate = noise_reduction(time, rate)
        # fig1, ax1 = plt.subplots()
        # ax1.plot(filtered_time, filtered_rate)
        filtered_df = pd.DataFrame({'Time':filtered_time/1e8, 'Rate': filtered_rate})
        filtered_df = filtered_df.set_index(filtered_time/1e8)
        st.line_chart(filtered_df)
        # st.pyplot(fig1)
        # st.write(filtered_df)


        st.header("Peaks observed from Input Data")
        st.subheader("Peak Detection")
        st.write("Since there can be multiple peaks, meaning multiple flares, in a single light curve, we need to detect all of them. We use the find_peaks() and peak_prominences() already implemented in SciPy to find the peaks and their index values in the ‘Time’ and ‘Rate’ arrays.")
        num_bursts, bursts_rate, bursts_time = get_and_segregate_peaks(filtered_time, filtered_rate)
        st.subheader("Peaks Segregation")
        st.write("Once all the peaks are detected, they are separated using a devised algorithm. For each peak, we get the minimum value of the rate between that particular peak and the peak before it(or the start of data, whichever is available first), and assign it as the start time for that wavelet. Similarly, we take the minimum value of the rate between this peak and the peak after it(or the end of data, whichever is available first), and assign it as the end time for that wavelet. The Rate and Time values for each of the wavelets are stored for further analysis. These are the multiple peaks that are plotted in the app (if the number of peaks is more than 1).")
        cols = st.columns(num_bursts)
        for i in range(num_bursts):      
            # c = alt.Chart(pd.DataFrame({'burst rates': bursts_rate[i], 'burst times': bursts_time[i]}).astype(str)).mark_line().encode(
            #     x='burst rates',
            #     y='burst times'
            # )
            # fig, ax = plt.subplots()
            # ax.plot(bursts_time[i], bursts_rate[i])
            # cols[i].pyplot(fig)
            cols[i].line_chart(pd.DataFrame({"Times": bursts_time[i]/1e8, "Rates": bursts_rate[i]}, index=bursts_time[i]/1e8))
        # df_properties = pd.DataFrame({'Burst Rates': list(bursts_rate.values()), 'Burst Times': list(bursts_time.values())})    
        # st. write(df_properties)
        st.caption("There were %s peaks observed from today's LC data!" % num_bursts)


        st.header("Wavelet Analysis")
        st.write("Once we get the wavelets, we can run an analysis on each of them and extract all of the necessary parameters from the information available. We first get the Mean and Standard Deviation of the data using regular methods. Then we find the Peak Flux for the data in counts per second and use it further to find the Rise and Decay Time. For Rise Time and Decay Time, we use the general definition of Rise Time (The time taken by the signal to rise from 10% of peak value to 90% of peak value) and Decay Time (The time taken by the signal to decay from 90% of peak value to 10% of peak value). We find the start and endpoint for the wavelet (i.e. Where the rate value is 10% of the peak value) and calculate Rise Time as T(90% of peak) - T(10% of peak) and Decay Time as T(10% of peak) - T(90% of peak).")
        st.write("The Total Flux of the wavelet is calculated as the area under the curve between the starting and ending points of the wavelet. This is calculated by integrating between these two points using simps() method implemented in SciPy.")
        df_analysis = {"rise_time":[], "decay_time":[], "flare_duration":[], "peak_count":[], "total_count":[]}
        # df = pd.DataFrame({""})
        for key in bursts_rate.keys():
            rate = bursts_rate[key]
            time = bursts_time[key]
            params=analyse_wavelets(time, rate)
            # df_analysis["mean"].append(params[0])
            # df_analysis["stdev"].append(params[1])
            df_analysis['rise_time'].append(params[0])
            df_analysis["decay_time"].append(params[1])
            df_analysis["flare_duration"].append(params[2])
            df_analysis["peak_count"].append(params[3])
            df_analysis["total_count"].append(params[4])
        # print(analysis)
        st.dataframe(pd.DataFrame(df_analysis).astype(str))


        st.header("LC Solar Flare Classification")
        st.write("Solar flares can be classified using the Soft X-ray classification or the H-alpha classification. The Soft X-ray classification is the modern classification system. Here 5 letters, A, B, C, M, or X are used according to the peak flux (Watt/m2). This classification system divides solar flares according to their strength. The smallest ones are ‘A-class’, followed by ‘B’, ‘C’, ‘M’ and ‘X’. Each letter here represents a 10-fold increase in energy output. And within each scale, there exists a finer scale from 1 to 9. And then comes the X-class flares, these are the most powerful flares of all. These flares can go higher than 9.")
        df_classify = {"Classification":[]}
        for i in range(num_bursts):
            df_classify["Classification"].append(classify_flare(df_analysis["peak_count"][i]))
        st.dataframe(pd.DataFrame(df_classify))


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
