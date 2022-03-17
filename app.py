import streamlit as st
import altair as alt
import pandas as pd
import altair as alt
from astropy.io import fits
from urllib.error import URLError
from utils import noise_reduction,get_and_segregate_peaks, analyse_wavelets, classify_flare
import matplotlib.pyplot as plt

@st.cache
def fits_io(path_to_fits):
    """
    I/O for fits files
    Input: Fits file/lc file path
    Output: Time and Rate arrays
    """
    fits_lc = fits.open(path_to_fits)
    fits_data = fits_lc[1].data
    time=fits_data.field("TIME")
    rate=fits_data.field("RATE")
    error = fits_data.field('ERROR')
    fracexp = fits_data.field('FRACEXP')
    return time, rate

try:
    st.header("Raw data input:")
    time, rate = fits_io('data/ch2_xsm_20211022_v1_level2.lc')
    #data = {'time':time/1e8,'rates':rate}
    df = pd.DataFrame({'time':time/1e8,'rates':rate})
    #df = df.set_index(time/1e8)
    st.line_chart(df)
    fig, ax = plt.subplots()
    ax.plot(time,rate)
    st.pyplot(fig)
    st.write(df.astype(str))

    st.header("Data after Noise Reduction")
    filtered_time, filtered_rate = noise_reduction(time, rate)
    fig1, ax1 = plt.subplots()
    ax1.plot(filtered_time, filtered_rate)
    # filtered_df = pd.DataFrame({'Time':filtered_time, 'Rate': filtered_rate}).astype(str)
    st.pyplot(fig1)
    # st.write(filtered_df)


    st.header("Peaks observed from Input Data")
    num_bursts, bursts_rate, bursts_time = get_and_segregate_peaks(filtered_time, filtered_rate)
    cols = st.columns(num_bursts)
    for i in range(num_bursts):      
        # c = alt.Chart(pd.DataFrame({'burst rates': bursts_rate[i], 'burst times': bursts_time[i]}).astype(str)).mark_line().encode(
        #     x='burst rates',
        #     y='burst times'
        # )
        fig, ax = plt.subplots()
        ax.plot(bursts_time[i], bursts_rate[i])
        cols[i].pyplot(fig)
    # df_properties = pd.DataFrame({'Burst Rates': list(bursts_rate.values()), 'Burst Times': list(bursts_time.values())})    
    # st. write(df_properties)
    st.caption("There were %s peaks observed from today's LC data!" % num_bursts)


    st.header("Wavelet Analysis")
    df_analysis = {"mean":[], "stdev":[], "rise_time":[], "decay_time":[], "flare_duration":[], "peak_flux":[], "total_flux":[]}
    # df = pd.DataFrame({""})
    for key in bursts_rate.keys():
        rate = bursts_rate[key]
        time = bursts_time[key]
        params=analyse_wavelets(time, rate)
        df_analysis["mean"].append(params[0])
        df_analysis["stdev"].append(params[1])
        df_analysis["rise_time"].append(params[2])
        df_analysis["decay_time"].append(params[3])
        df_analysis["flare_duration"].append(params[4])
        df_analysis["peak_flux"].append(params[5])
        df_analysis["total_flux"].append(params[6])
    # print(analysis)
    st.dataframe(pd.DataFrame(df_analysis).astype(str))


    st.header("LC Solar Flare Classification")
    df_classify = {"Classification":[]}
    for i in range(num_bursts):
        df_classify["Classification"].append(classify_flare(df_analysis["peak_flux"][i]))
    st.dataframe(pd.DataFrame(df_classify))


except URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
