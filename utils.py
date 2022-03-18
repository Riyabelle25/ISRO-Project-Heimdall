import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.io import fits
from astropy.table import Table
from scipy.signal import find_peaks, peak_prominences
from scipy.integrate import simps
import pandas as pd

def fits_io(path_to_file):
    """
    I/O for fits files
    Input: ASCII/FITS/LC/CSV/XLS file path
    Output: Time and Rate arrays
    """
    if path_to_file.endswith('.txt') or path_to_file.endswith('.ascii'):
      data = Table.read(path_to_file, format='ascii')
      time=data.field("TIME")
      rate=data.field("RATE")
    elif path_to_file.endswith('.lc') or path_to_file.endswith('.fits'):
      data = Table.read(path_to_file, format='fits')
      time=data.field("TIME")
      rate=data.field("RATE")
    elif path_to_file.endswith('.csv'):
      data = Table.read(path_to_file, format='csv')
      time=data.field("TIME")
      rate=data.field("RATE")
    elif path_to_file.endswith('.xlsx') or path_to_file.endswith('.xls') or path_to_file.endswith('.xlsm') or path_to_file.endswith('.xlsb') or path_to_file.endswith('.odt') or path_to_file.endswith('.odf'):
      data = pd.read_excel(path_to_file)
      time=data["TIME"]
      rate=data["RATE"]
    background_count = np.mean(rate)
    return time, rate, background_count


def noise_reduction(time, rate):
    """
    Noise reduction of rate using time averaging
    Input: time, rate arrays
    Output: Filtered time and rate arrays
    """
    n = len(time)
    rate_filtered = []
    window = 500
    for i in range(n-window):
        rate_filtered.append(np.mean(rate[i:i+window]))
    rate_filtered = np.array(rate_filtered)
    time_filtered = time[:n-window]

    return time_filtered, rate_filtered


def get_and_segregate_peaks(time_filtered, rate_filtered):
    """
    Recognizes peaks in the time vs rate data and segregates out the peaks
    Input: time_filtered, rate_filtered
    Output: Number of bursts==Number of peaks, 2 dictionaries(bursts_rate containing the rate of bursts and bursts_time containing time of the bursts)
    Dict format:
    {'key is the index of burst': [rate array for bursts_rate, time array for bursts_time]}
    """
    # Peaks recognition
    peaks, _ = find_peaks(rate_filtered)
    prominences, _, _ = peak_prominences(rate_filtered, peaks)
    selected = prominences > 0.25 * (np.min(prominences) + np.max(prominences))
    top = peaks[selected]   # Contains indexes of all peak values in rate array

    num_bursts = len(top)   # Assuming each peak for corresponds to a burst

    # Peaks segregation
    rise_pt_idx=[]
    decay_pt_idx=[]
    for i in range(num_bursts):
        peak_idx = top[i]
        if i==0:
            rise_pt_idx.append(np.where(rate_filtered==min(rate_filtered[:peak_idx])))
        else:
            rise_pt_idx.append(np.where(rate_filtered==min(rate_filtered[top[i-1]:peak_idx])))

        if i==num_bursts-1:
            decay_pt_idx.append(np.where(rate_filtered==min(rate_filtered[peak_idx:])))
        else:
            decay_pt_idx.append(np.where(rate_filtered==min(rate_filtered[peak_idx:top[i+1]])))

    bursts_rate={}
    bursts_time={}
    for i in range(len(rise_pt_idx)):
        start=rise_pt_idx[i][0][0]
        end=decay_pt_idx[i][0][0]
        
        bursts_rate[i] = rate_filtered[start:end]
        bursts_time[i] = time_filtered[start:end]

    return num_bursts, bursts_rate, bursts_time


def analyse_wavelets(time, rate):
    """
    NEED TO IMPROVE RISE TIME AND DECAY TIME CALC
    Run this function for each wavelet in the dictionaries in get_and_segregate_peaks()
    Returns desired parameters(rise time, decay time, peak flux etc)
    Input: filtered time and rate arrays
    Output: desired Parameters
    """
    peak_count=max(rate)
    peak_idx = np.where(rate==max(rate))[0][0]
    print(peak_idx)
    y_values = (rate-np.mean(rate)) / np.std(rate)
    x_values = (time-np.mean(time)) / np.std(time)
    mean = np.mean(rate)
    stdev = np.std(rate)
    arr_prev_rev = list(rate[:peak_idx])
    arr_prev_rev = arr_prev_rev[::-1]
    for i in arr_prev_rev:
      rise_start_idx=arr_prev_rev[::-1].index(i)
      if i<=0.1*peak_count:
        break
  
    arr_fwd = list(rate[peak_idx:])
    for i in arr_fwd:
      decay_end_idx = arr_fwd.index(i)+peak_idx
      if i<=0.1*peak_count:
        break
    rise_time = time[peak_idx]-time[rise_start_idx]
    decay_time = time[decay_end_idx]-time[peak_idx]
    flare_duration = rise_time+decay_time
    peak_count = int(max(rate))
    # Calculating total count for each wavelet
    total_count = simps(rate, dx = time[decay_end_idx]-time[rise_start_idx])

    return rise_time, decay_time, flare_duration, peak_count, total_count

def classify_flare(peak_count):
    """
    CLassifies the flare based on peak flux
    Input: peak flux of the flare
    Output: Class 
    """
    if(peak_count > 1e5):
        return "X"
    if(peak_count > 1e4):
        return "M"
    if(peak_count > 1e3):
        return "C"
    if(peak_count > 1e2):
        return "B"
    else:
        return "A"
if __name__ == "__main__":
    time, rate = fits_io('data/ch2_xsm_20211022_v1_level2.lc')
    time_filtered, rate_filtered = noise_reduction(time, rate)
    num_bursts, bursts_rate, bursts_time = get_and_segregate_peaks(time_filtered, rate_filtered)
    for key in bursts_rate.keys():
        rate = bursts_rate[key]
        time = bursts_time[key]
        ans=analyse_wavelets(time, rate)
        print(ans)

