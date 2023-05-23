# -*- coding: utf-8 -*-
"""
Complete implementation of Pan-Tompkins algorithm

# Inputs
ecg : raw ecg vector signal 1d signal
fs : sampling frequency e.g. 200Hz, 400Hz and etc
gr : flag to plot or not plot (set it 1 to have a plot or set it zero not
to see any plots
# Outputs
qrs_amp_raw : amplitude of R waves amplitudes
qrs_i_raw : index of R waves
delay : number of samples which the signal is delayed due to the
filtering
# Method :

# PreProcessing
1) Signal is preprocessed , if the sampling frequency is higher then it is downsampled
and if it is lower upsampled to make the sampling frequency 200 Hz
with the same filtering setups introduced in Pan
tompkins paper (a combination of low pass and high pass filter 5-15 Hz)
to get rid of the baseline wander and muscle noise. 

2) The filtered signal
is derivated using a derivating filter to high light the QRS complex.

3) Signal is squared.4)Signal is averaged with a moving window to get rid
of noise (0.150 seconds length).

5) depending on the sampling frequency of your signal the filtering
options are changed to best match the characteristics of your ecg signal

6) Unlike the other implementations in this implementation the desicion
rule of the Pan tompkins is implemented completely.

# Decision Rule 
At this point in the algorithm, the preceding stages have produced a roughly pulse-shaped
waveform at the output of the MWI . The determination as to whether this pulse
corresponds to a QRS complex (as opposed to a high-sloped T-wave or a noise artefact) is
performed with an adaptive thresholding operation and other decision
rules outlined below

a) FIDUCIAL MARK - The waveform is first processed to produce a set of weighted unit
samples at the location of the MWI maxima. This is done in order to localize the QRS
complex to a single instant of time. The w[k] weighting is the maxima value.

b) THRESHOLDING - When analyzing the amplitude of the MWI output, the algorithm uses
two threshold values (THR_SIG and THR_NOISE, appropriately initialized during a brief
2 second training phase) that continuously adapt to changing ECG signal quality. The
first pass through y[n] uses these thresholds to classify the each non-zero sample
(CURRENTPEAK) as either signal or noise:
If CURRENTPEAK > THR_SIG, that location is identified as a QRS complex
candidate and the signal level (SIG_LEV) is updated:
SIG _ LEV = 0.125 CURRENTPEAK + 0.875 SIG _ LEV

If THR_NOISE < CURRENTPEAK < THR_SIG, then that location is identified as a
noise peak and the noise level (NOISE_LEV) is updated:
NOISE _ LEV = 0.125CURRENTPEAK + 0.875 NOISE _ LEV
Based on new estimates of the signal and noise levels (SIG_LEV and NOISE_LEV,
respectively) at that point in the ECG, the thresholds are adjusted as follows:
THR _ SIG = NOISE _ LEV + 0.25  (SIG _ LEV ? NOISE _ LEV )
THR _ NOISE = 0.5 (THR _ SIG)
These adjustments lower the threshold gradually in signal segments that are deemed to
be of poorer quality.

c) SEARCHBACK FOR MISSED QRS COMPLEXES - In the thresholding step above, if
CURRENTPEAK < THR_SIG, the peak is deemed not to have resulted from a QRS
complex. If however, an unreasonably long period has expired without an abovethreshold
peak, the algorithm will assume a QRS has been missed and perform a
searchback. This limits the number of false negatives. The minimum time used to trigger
a searchback is 1.66 times the current R peak to R peak time period (called the RR
interval). This value has a physiological origin - the time value between adjacent
heartbeats cannot change more quickly than this. The missed QRS complex is assumed
to occur at the location of the highest peak in the interval that lies between THR_SIG and
THR_NOISE. In this algorithm, two average RR intervals are stored,the first RR interval is 
calculated as an average of the last eight QRS locations in order to adapt to changing heart 
rate and the second RR interval mean is the mean 
of the most regular RR intervals . The threshold is lowered if the heart rate is not regular 
to improve detection.

d) ELIMINATION OF MULTIPLE DETECTIONS WITHIN REFRACTORY PERIOD - It is
impossible for a legitimate QRS complex to occur if it lies within 200ms after a previously
detected one. This constraint is a physiological one  due to the refractory period during
which ventricular depolarization cannot occur despite a stimulus[1]. As QRS complex
candidates are generated, the algorithm eliminates such physically impossible events,
thereby reducing false positives.

e) T WAVE DISCRIMINATION - Finally, if a QRS candidate occurs after the 200ms
refractory period but within 360ms of the previous QRS, the algorithm determines
whether this is a genuine QRS complex of the next heartbeat or an abnormally prominent
T wave. This decision is based on the mean slope of the waveform at that position. A slope of
less than one half that of the previous QRS complex is consistent with the slower
changing behaviour of a T wave  otherwise, it becomes a QRS detection.
Extra concept : beside the points mentioned in the paper, this code also
checks if the occured peak which is less than 360 msec latency has also a
latency less than 0,5*mean_RR if yes this is counted as noise

f) In the final stage , the output of R waves detected in smoothed signal is analyzed and double
checked with the help of the output of the bandpass signal to improve
detection and find the original index of the real R waves on the raw ecg
signal

# References :

[1]PAN.J, TOMPKINS. W.J,"A Real-Time QRS Detection Algorithm" IEEE
TRANSACTIONS ON BIOMEDICAL ENGINEERING, VOL. BME-32, NO. 3, MARCH 1985.

# Author : Hooman Sedghamiz
Linkoping university 
email : hoose792@student.liu.se
hooman.sedghamiz@medel.com

Any direct or indirect use of this code should be referenced 
Copyright march 2014
"""
import numpy as np
# import matplotlib.pyplot as plt
import scipy.signal as ss
from scipy.interpolate import interp1d 
import scipy.io as sio

def pan_tompkinV3(ecg:np.ndarray, fs:float, gr:int=1):
# def pan_tompkinV3(ecg, fs, gr=1):
    assert isinstance(ecg, np.ndarray) and np.prod(ecg.shape)==np.max(ecg.shape),\
        "'ecg' must be a row or column vector."

    ecg = ecg.flatten()
    
    # Initialize
    qrs_c =[]       # amplitude of R
    qrs_i =[]       # index
    
    SIG_LEV = 0 
    nois_c =[]
    nois_i =[]
    
    delay = 0
    skip = 0        # becomes one when a T wave is detected
    not_nois = 0    # it is not noise when not_nois = 1
    selected_RR =[] # Selected RR intervals
    
    m_selected_RR = 0
    mean_RR = 0
    
    qrs_i_raw =[]
    qrs_amp_raw=[]
    ser_back = 0 
    test_m = 0
    
    SIGL_buf = []
    NOISL_buf = []
    THRS_buf = []
    SIGL_buf1 = []
    NOISL_buf1 = []
    THRS_buf1 = []
    ax = np.full(6, None)
    az = np.full(3, None)
    if gr==1: 
        plt.figure()
    
    # Step1: Noise cancelation(Filtering) # Filters (Filter in between 5-15 Hz)
    if fs == 200:
        # start figure
        if (gr==1): 
            ax[0] = plt.subplot(321)
            plt.plot(ecg)
            plt.axis('tight')
            plt.title('Raw signal')
            
        # remove the mean of Signal
        ecg = ecg - np.mean(ecg)
          
        # Low Pass Filter  H(z) = ((1 - z^(-6))^2)/(1 - z^(-1))^2
        # It has come to my attention the original filter doesnt achieve 12 Hz
        #     b = [1 0 0 0 0 0 -2 0 0 0 0 0 1]
        #     a = [1 -2 1]
        #     ecg_l = filter(b,a,ecg) 
        #     delay = 6
        # 
        Wn = 12*2/fs
        N = 3 # order of 3 less processing
        [a,b] = ss.butter(N,Wn,'low') #bandpass filtering
        ecg_l = ss.filtfilt(a,b,ecg) 
        ecg_l = ecg_l/ max(abs(ecg_l))
        if (gr==1):
            ax[1] = plt.subplot(322, sharex=ax[0])
            plt.plot(ecg_l)
            plt.axis('tight')
            plt.title('Low pass filtered')
            
        ### High Pass filter H(z) = (-1+32z^(-16)+z^(-32))/(1+z^(-1))
        # It has come to my attention the original filter doesn achieve 5 Hz
        #     b = zeros(1,33)
        #     b(1) = -1 b(17) = 32 b(33) = 1
        #     a = [1 1]
        #     ecg_h = filter(b,a,ecg_l)    # Without Delay
        #     delay = delay + 16
        #
        Wn = 5*2/fs
        N = 3 # order of 3 less processing
        [a,b] = ss.butter(N,Wn,'high') #bandpass filtering
        ecg_h = ss.filtfilt(a,b,ecg_l) 
        ecg_h = ecg_h/ max(abs(ecg_h))
        if (gr==1):
            ax[2] = plt.subplot(323)
            plt.plot(ecg_h)
            plt.axis('tight')
            plt.title('High Pass Filtered')
           
    else:
        if (gr==1):
            ax[0] = plt.subplot(3,2,(1,2))
            plt.plot(ecg)
            plt.axis('tight')
            plt.title('Raw Signal')
        
        # bandpass filter for Noise cancelation of other sampling frequencies(Filtering)
        f1 = 5    # cut-off low frequency to get rid of baseline wander
        f2 = 15   # cut-off frequency to discard high frequency noise
        Wn = np.array([f1,f2])*2/fs     # cut-off based on fs
        N = 3     # order of 3 less processing
        a, b = ss.butter(N,Wn,'bandpass') # bandpass filtering
        ecg_h = ss.filtfilt(a,b,ecg)
        ecg_h = ecg_h / max(abs(ecg_h))
        if (gr==1):
            ax[2] = plt.subplot(323, sharex=ax[0])
            plt.plot(ecg_h)
            plt.axis('tight')
            plt.title('Band Pass Filtered')
    
    # Step2: derivative filter H(z) = 1/(8T)*(-z^(-2) - 2z^(-1) + 2z + z^(2))
    if fs != 200:
        int_c = (5-1)/(fs*1/40)
        b = interp1d(np.arange(1,5+1e-5), np.array([1,2,0,-2,-1])*(1/8)*fs) # return function
        b = b(np.arange(1,5+1e-5,int_c))
    else:   
        b = np.array([1,2,0,-2,-1])*(1/8)*fs   
    
    ecg_d = ss.filtfilt(b,1,ecg_h)
    ecg_d = ecg_d/max(ecg_d)
    
    if (gr==1):
         ax[3] = plt.subplot(324, sharex=ax[0])
         plt.plot(ecg_d)
         plt.axis('tight')
         plt.title('Filtered with the derivative filter')
          
    # Part1. Squaring nonlinearly enhance the dominant peaks
    ecg_s = ecg_d**2
    if (gr==1):
         ax[4]= plt.subplot(325, sharex=ax[0]) 
         plt.plot(ecg_s)
         plt.axis('tight')
         plt.title('Squared')
    
    # Part2. Moving average Y(nt) = (1/N)[x(nT-(N - 1)T)+ x(nT - (N - 2)T)+...+x(nT)]
    ecg_m = ss.convolve(ecg_s, np.ones(round(0.150*fs))/round(0.150*fs))
    delay = delay + round(0.150*fs)/2
    
    if(gr==1):
        ax[5]= plt.subplot(326, sharex=ax[0]) 
        plt.plot(ecg_m)
        plt.axis('tight')
        plt.title('Averaged with 30 samples length, Black noise, Green Adaptive Threshold, RED Sig Level, Red circles QRS adaptive threshold')
        plt.axis('tight')
    
    # Step3: Fiducial Mark 
    # Note : a minimum distance of 40 samples is considered between each R wave
    # since in physiological point of view no RR wave can occur in less than
    # 200 msec distance
    locs, _ = ss.find_peaks(ecg_m, distance=round(0.2*fs))
    pks = ecg_m[locs]
    
    # initialize the training phase (2 seconds of the signal) to determine the THR_SIG and THR_NOISE
    THR_SIG = max(ecg_m[1:2*fs])*1/3 # 0.25 of the max amplitude 
    THR_NOISE = np.mean(ecg_m[1:2*fs])*1/2 # 0.5 of the mean signal is considered to be noise
    SIG_LEV= THR_SIG
    NOISE_LEV = THR_NOISE
    
    
    # Initialize bandpath filter threshold(2 seconds of the bandpass signal)
    THR_SIG1 = max(ecg_h[1:2*fs])*1/3 # 0.25 of the max amplitude 
    THR_NOISE1 = np.mean(ecg_h[1:2*fs])*1/2 #
    SIG_LEV1 = THR_SIG1 # Signal level in Bandpassed filter
    NOISE_LEV1 = THR_NOISE1 # Noise level in Bandpassed filter
    
    # Thresholding and online desicion rule
    for i in range(len(pks)):
        # locate the corresponding peak in the filtered signal 
        if locs[i]-round(0.150*fs)>=1 and locs[i]<= len(ecg_h):
            y_i = np.max(ecg_h[locs[i]-round(0.150*fs):locs[i]])
            x_i = np.argmax(ecg_h[locs[i]-round(0.150*fs):locs[i]])
        else:
            if i == 0:
                y_i, x_i = np.max(ecg_h[1:locs[i]]), np.argmax(ecg_h[1:locs[i]])
                ser_back = 1
            elif locs[i]>= len(ecg_h):
                y_i, x_i = np.max(ecg_h[locs[i]-round(0.150*fs):]),\
                    np.argmax(ecg_h[locs[i]-round(0.150*fs):])
        
        # update the heart_rate (Two heart rate means one the moste recent and the other selected)
        if len(qrs_c) >= 9:
            
            diffRR = np.diff(qrs_i[-9:]) #calculate RR interval
            mean_RR = np.mean(diffRR) # calculate the mean of 8 previous R waves interval
            comp = qrs_i[-1]-qrs_i[-2] #latest RR
            
            if comp <= 0.92*mean_RR or comp >= 1.16*mean_RR:
                # lower down thresholds to detect better in MVI
                THR_SIG = 0.5*(THR_SIG)
                #THR_NOISE = 0.5*(THR_SIG) 
                 
                # lower down thresholds to detect better in Bandpass filtered 
                THR_SIG1 = 0.5*(THR_SIG1)
                #THR_NOISE1 = 0.5*(THR_SIG1) 
                    
            else:
                m_selected_RR = mean_RR #the latest regular beats mean
    
            
            # calculate the mean of the last 8 R waves to make sure that QRS is not
            # missing(If no R detected , trigger a search back) 1.66*mean
               
            if m_selected_RR:
                test_m = m_selected_RR #if the regular RR availabe use it   
            elif mean_RR and m_selected_RR == 0:
                test_m = mean_RR   
            else:
                test_m = 0
                
            if test_m:
                if (locs[i] - qrs_i[-1]) >= round(1.66*test_m): # it shows a QRS is missed 
                    pks_temp = np.max(ecg_m[qrs_i[-1]+ round(0.200*fs):locs[i]-round(0.200*fs)]) # search back the max in this interval
                    locs_temp = np.argmax(ecg_m[qrs_i[-1]+ round(0.200*fs):locs[i]-round(0.200*fs)]) # search locate the max in this interval
                    locs_temp = qrs_i[-1]+ round(0.200*fs) + locs_temp -1 #location 
                       
                    if pks_temp > THR_NOISE:
                        qrs_c.append(pks_temp)
                        qrs_i.append(locs_temp)
                        
                        # find the location in filtered sig
                        if locs_temp <= len(ecg_h):
                            y_i_t = np.max(ecg_h[locs_temp-round(0.150*fs):locs_temp])
                            x_i_t = np.argmax(ecg_h[locs_temp-round(0.150*fs):locs_temp])
                        else:
                            y_i_t = np.max(ecg_h[locs_temp-round(0.150*fs):])
                            x_i_t = np.argmax(ecg_h[locs_temp-round(0.150*fs):])
                        # take care of bandpass signal threshold
                        if y_i_t > THR_NOISE1:
                             qrs_i_raw.append(locs_temp-round(0.150*fs)+ (x_i_t-1))# save index of bandpass 
                             qrs_amp_raw.append(y_i_t) #save amplitude of bandpass 
                             SIG_LEV1 = 0.25*y_i_t + 0.75*SIG_LEV1 #when found with the second thres 
                      
                        not_nois = 1
                        SIG_LEV = 0.25*pks_temp + 0.75*SIG_LEV   #when found with the second threshold             
                else:
                    not_nois = 0
              
            
        # find noise and QRS peaks
        if pks[i] >= THR_SIG:
            
            # if a QRS candidate occurs within 360ms of the previous QRS,
            # the algorithm determines if its T wave or QRS
            if len(qrs_c) >= 3:
                 if (locs[i]-qrs_i[-1]) <= round(0.3600*fs):
                    Slope1 = np.mean(np.diff(ecg_m[locs[i]-round(0.075*fs):locs[i]])) #mean slope of the waveform at that position
                    Slope2 = np.mean(np.diff(ecg_m[qrs_i[-1]-round(0.075*fs):qrs_i[-1]])) #mean slope of previous R wave
                    if abs(Slope1) <= abs(0.5*(Slope2)):  # slope less then 0.5 of previous R
                        nois_c.append(pks[i])
                        nois_i.append(locs[i])
                        skip = 1 # T wave identification
                        # adjust noise level in both filtered and
                        # MVI
                        NOISE_LEV1 = 0.125*y_i + 0.875*NOISE_LEV1
                        NOISE_LEV = 0.125*pks[i] + 0.875*NOISE_LEV 
                    else:
                        skip = 0
    
            if skip == 0:  # skip is 1 when a T wave is detected       
                qrs_c.append(pks[i])
                qrs_i.append(locs[i])
              
                # bandpass filter check threshold
                if y_i >= THR_SIG1:
                      if ser_back:
                         qrs_i_raw.append(x_i)  # save index of bandpass 
                      else:
                         qrs_i_raw.append(locs[i]-round(0.150*fs) + (x_i - 1))# save index of bandpass 
                      qrs_amp_raw.append(y_i)# save amplitude of bandpass 
                      SIG_LEV1 = 0.125*y_i + 0.875*SIG_LEV1# adjust threshold for bandpass filtered sig
             
                # adjust Signal level
                SIG_LEV = 0.125*pks[i] + 0.875*SIG_LEV 
            
        elif (THR_NOISE <= pks[i]) and (pks[i] < THR_SIG):
             #adjust Noise level in filtered sig
             NOISE_LEV1 = 0.125*y_i + 0.875*NOISE_LEV1
             #adjust Noise level in MVI
             NOISE_LEV = 0.125*pks[i] + 0.875*NOISE_LEV 
        
        elif pks[i] < THR_NOISE:
            nois_c.append(pks[i])
            nois_i.append(locs[i])
            
            # noise level in filtered signal
            NOISE_LEV1 = 0.125*y_i + 0.875*NOISE_LEV1     
             #adjust Noise level in MVI
            NOISE_LEV = 0.125*pks[i] + 0.875*NOISE_LEV  
            
    
        # adjust the threshold with SNR
        if NOISE_LEV != 0 or SIG_LEV != 0:
            THR_SIG = NOISE_LEV + 0.25*(abs(SIG_LEV - NOISE_LEV))
            THR_NOISE = 0.5*(THR_SIG)
        
        # adjust the threshold with SNR for bandpassed signal
        if NOISE_LEV1 != 0 or SIG_LEV1 != 0:
            THR_SIG1 = NOISE_LEV1 + 0.25*(abs(SIG_LEV1 - NOISE_LEV1))
            THR_NOISE1 = 0.5*(THR_SIG1)
            
            
        # take a track of thresholds of smoothed signal
        SIGL_buf.append(SIG_LEV)
        NOISL_buf.append(NOISE_LEV)
        THRS_buf.append(THR_SIG)
        
        # take a track of thresholds of filtered signal
        SIGL_buf1.append(SIG_LEV1)
        NOISL_buf1.append(NOISE_LEV1)
        THRS_buf1.append(THR_SIG1)
    
        skip = 0        # reset parameters
        not_nois = 0    # reset parameters
        ser_back = 0    # reset bandpass param   
        
    if (gr==1):
        plt.scatter(qrs_i, qrs_c, marker='o', c='w', edgecolors='m')
        plt.plot(locs, NOISL_buf, linestyle='--', c='k', linewidth=2)
        plt.plot(locs, SIGL_buf, linestyle='--', c='r', linewidth=2)
        plt.plot(locs, THRS_buf, linestyle='--', c='g', linewidth=2)
        plt.show()
        if any(ax):
            ax[np.logical_not(ax).astype('bool')] = None 

    # modify by yenchun@nctu
    new_qrs_i_raw =[]
    windowSize = 0.1
    
    for ii in range(len(qrs_i_raw)):
        maxI = qrs_i_raw[ii]
        if(maxI-round(fs*windowSize) <= 0 ): 
            start = 0 
        else:
            start = maxI-round(fs*windowSize) 
        if(maxI+round(fs*windowSize) >= len(ecg)):
            endd = len(ecg)-1
        else: 
            endd = maxI+round(fs*windowSize)
        
        tmpWin = np.arange(start,endd+1e-5).astype(int)
        maxA, maxI = ecg[tmpWin].max(), ecg[tmpWin].argmax()
        maxI = tmpWin[maxI]
        if( 1 < maxI < len(ecg)-1):
            rightSlpoe = ecg[maxI+1]-ecg[maxI]
            leftSlope  = ecg[maxI] - ecg[maxI-1]
            if(rightSlpoe<=0 and leftSlope >=0):
                new_qrs_i_raw = [new_qrs_i_raw, maxI]

    # overlay on the signals
    if (gr==1):
        plt.figure()
        az[0] = plt.subplot(311) 
        plt.plot(ecg_h)
        plt.title('QRS on Filtered Signal')
        plt.axis('tight')
        plt.scatter(qrs_i_raw,qrs_amp_raw,c='w',edgecolors='m')
        plt.plot(locs,NOISL_buf1,linewidth=2,linestyle='--',c='k')
        plt.plot(locs,SIGL_buf1,linewidth=2,linestyle='--',c='r')
        plt.plot(locs,THRS_buf1,linewidth=2,linestyle='--',c='g')
        
        az[1] = plt.subplot(312) 
        plt.plot(ecg_m)
        plt.title('QRS on MVI signal and Noise level(black),Signal Level (red) and Adaptive Threshold(green)')
        plt.axis('tight')
        plt.scatter(qrs_i,qrs_c,c='w',edgecolors='m')
        plt.plot(locs,NOISL_buf,linewidth=2,linestyle='--',c='k')
        plt.plot(locs,SIGL_buf,linewidth=2,linestyle='--',c='r')
        plt.plot(locs,THRS_buf,linewidth=2,linestyle='--',c='g')
        
        az[2] = plt.subplot(313) 
        plt.plot(ecg-np.mean(ecg)) # data
        plt.title('Pulse train of the found QRS on ECG signal')
        plt.axis('tight')
        plt.plot(np.tile(qrs_i_raw,[2, 1]), # R peak bar
             np.tile([min(ecg-np.mean(ecg))/2, max(ecg-np.mean(ecg))/2], [len(qrs_i_raw),1]).T,
             linewidth=2.5,linestyle='--',c='r')
        plt.show()
    return qrs_amp_raw,qrs_i_raw,delay

def pan_tompkinRest(ecg, fs, gr=1):
# def pan_tompkinRest(ecg:np.ndarray, fs:float, gr:int or bool=1) -> tuple[list,list,float]:
    assert isinstance(ecg, np.ndarray) and np.prod(ecg.shape)==np.max(ecg.shape),\
        "'ecg' must be a row or column vector."

    ecg = ecg.flatten()
    
    # Initialize
    qrs_c =[]       # amplitude of R
    qrs_i =[]       # index
    
    SIG_LEV = 0 
    nois_c =[]
    nois_i =[]
    
    delay = 0
    skip = 0        # becomes one when a T wave is detected
    not_nois = 0    # it is not noise when not_nois = 1
    selected_RR =[] # Selected RR intervals
    
    m_selected_RR = 0
    mean_RR = 0
    
    qrs_i_raw =[]
    qrs_amp_raw=[]
    ser_back = 0 
    test_m = 0
    
    SIGL_buf = []
    NOISL_buf = []
    THRS_buf = []
    SIGL_buf1 = []
    NOISL_buf1 = []
    THRS_buf1 = []
    ax = np.full(6, None)
    az = np.full(3, None)
    if gr==1: 
        plt.figure()
    
    # Step1: Noise cancelation(Filtering) # Filters (Filter in between 5-15 Hz)
    if fs == 200:
        # start figure
        if (gr==1): 
            ax[0] = plt.subplot(321)
            plt.plot(ecg)
            plt.axis('tight')
            plt.title('Raw signal')
            
        # remove the mean of Signal
        ecg = ecg - np.mean(ecg)
          
        # Low Pass Filter  H(z) = ((1 - z^(-6))^2)/(1 - z^(-1))^2
        # It has come to my attention the original filter doesnt achieve 12 Hz
        #     b = [1 0 0 0 0 0 -2 0 0 0 0 0 1]
        #     a = [1 -2 1]
        #     ecg_l = filter(b,a,ecg) 
        #     delay = 6
        # 
        Wn = 12*2/fs
        N = 3 # order of 3 less processing
        [a,b] = ss.butter(N,Wn,'low') #bandpass filtering
        ecg_l = ss.filtfilt(a,b,ecg) 
        ecg_l = ecg_l/ max(abs(ecg_l))
        if (gr==1):
            ax[1] = plt.subplot(322, sharex=ax[0])
            plt.plot(ecg_l)
            plt.axis('tight')
            plt.title('Low pass filtered')
            
        ### High Pass filter H(z) = (-1+32z^(-16)+z^(-32))/(1+z^(-1))
        # It has come to my attention the original filter doesn achieve 5 Hz
        #     b = zeros(1,33)
        #     b(1) = -1 b(17) = 32 b(33) = 1
        #     a = [1 1]
        #     ecg_h = filter(b,a,ecg_l)    # Without Delay
        #     delay = delay + 16
        #
        Wn = 5*2/fs
        N = 3 # order of 3 less processing
        [a,b] = ss.butter(N,Wn,'high') #bandpass filtering
        ecg_h = ss.filtfilt(a,b,ecg_l) 
        ecg_h = ecg_h/ max(abs(ecg_h))
        if (gr==1):
            ax[2] = plt.subplot(323)
            plt.plot(ecg_h)
            plt.axis('tight')
            plt.title('High Pass Filtered')
           
    else:
        if (gr==1):
            ax[0] = plt.subplot(3,2,(1,2))
            plt.plot(ecg)
            plt.axis('tight')
            plt.title('Raw Signal')
        
        # bandpass filter for Noise cancelation of other sampling frequencies(Filtering)
        f1 = 5    # cut-off low frequency to get rid of baseline wander
        f2 = 15   # cut-off frequency to discard high frequency noise
        Wn = np.array([f1,f2])*2/fs     # cut-off based on fs
        N = 3     # order of 3 less processing
        a, b = ss.butter(N,Wn,'bandpass') # bandpass filtering
        ecg_h = ss.filtfilt(a,b,ecg)
        ecg_h = ecg_h / max(abs(ecg_h))
        if (gr==1):
            ax[2] = plt.subplot(323, sharex=ax[0])
            plt.plot(ecg_h)
            plt.axis('tight')
            plt.title('Band Pass Filtered')
    
    # Step2: derivative filter H(z) = 1/(8T)*(-z^(-2) - 2z^(-1) + 2z + z^(2))
    if fs != 200:
        int_c = (5-1)/(fs*1/40)
        b = interp1d(np.arange(1,5+1e-5), np.array([1,2,0,-2,-1])*(1/8)*fs) # return function
        b = b(np.arange(1,5+1e-5,int_c))
    else:   
        b = np.array([1,2,0,-2,-1])*(1/8)*fs   
    
    ecg_d = ss.filtfilt(b,1,ecg_h)
    ecg_d = ecg_d/max(ecg_d)
    
    if (gr==1):
         ax[3] = plt.subplot(324, sharex=ax[0])
         plt.plot(ecg_d)
         plt.axis('tight')
         plt.title('Filtered with the derivative filter')
          
    # Part1. Squaring nonlinearly enhance the dominant peaks
    ecg_s = ecg_d**2
    if (gr==1):
         ax[4]= plt.subplot(325, sharex=ax[0]) 
         plt.plot(ecg_s)
         plt.axis('tight')
         plt.title('Squared')
    
    # Part2. Moving average Y(nt) = (1/N)[x(nT-(N - 1)T)+ x(nT - (N - 2)T)+...+x(nT)]
    ecg_m = ss.convolve(ecg_s, np.ones(round(0.150*fs))/round(0.150*fs))
    delay = delay + round(0.150*fs)/2
    
    if(gr==1):
        ax[5]= plt.subplot(326, sharex=ax[0]) 
        plt.plot(ecg_m)
        plt.axis('tight')
        plt.title('Averaged with 30 samples length, Black noise, Green Adaptive Threshold, RED Sig Level, Red circles QRS adaptive threshold')
        plt.axis('tight')
    
    # Step3: Fiducial Mark 
    # Note : a minimum distance of 40 samples is considered between each R wave
    # since in physiological point of view no RR wave can occur in less than
    # 200 msec distance
    locs, _ = ss.find_peaks(ecg_m, distance=round(0.2*fs))
    pks = ecg_m[locs]
    
    # initialize the training phase (2 seconds of the signal) to determine the THR_SIG and THR_NOISE
    THR_SIG = max(ecg_m)*1/3 # 0.25 of the max amplitude 
    THR_NOISE = np.mean(ecg_m)*1/2 # 0.5 of the mean signal is considered to be noise
    SIG_LEV= THR_SIG
    NOISE_LEV = THR_NOISE
    
    
    # Initialize bandpath filter threshold(2 seconds of the bandpass signal)
    THR_SIG1 = max(ecg_h[1:2*fs])*1/3 # 0.25 of the max amplitude 
    THR_NOISE1 = np.mean(ecg_h[1:2*fs])*1/2 #
    SIG_LEV1 = THR_SIG1 # Signal level in Bandpassed filter
    NOISE_LEV1 = THR_NOISE1 # Noise level in Bandpassed filter
    
    # Thresholding and online desicion rule
    for i in range(len(pks)):
        # locate the corresponding peak in the filtered signal 
        if locs[i]-round(0.150*fs)>=1 and locs[i]<= len(ecg_h):
            y_i = np.max(ecg_h[locs[i]-round(0.150*fs):locs[i]])
            x_i = np.argmax(ecg_h[locs[i]-round(0.150*fs):locs[i]])
        else:
            if i == 0:
                y_i, x_i = np.max(ecg_h[1:locs[i]]), np.argmax(ecg_h[1:locs[i]])
                ser_back = 1
            elif locs[i]>= len(ecg_h):
                y_i, x_i = np.max(ecg_h[locs[i]-round(0.150*fs):]),\
                    np.argmax(ecg_h[locs[i]-round(0.150*fs):])
        
        # update the heart_rate (Two heart rate means one the moste recent and the other selected)
        if len(qrs_c) >= 9:
            
            diffRR = np.diff(qrs_i[-9:]) #calculate RR interval
            mean_RR = np.mean(diffRR) # calculate the mean of 8 previous R waves interval
            comp = qrs_i[-1]-qrs_i[-2] #latest RR
            
            if comp <= 0.92*mean_RR or comp >= 1.16*mean_RR:
                # lower down thresholds to detect better in MVI
                THR_SIG = 0.5*(THR_SIG)
                #THR_NOISE = 0.5*(THR_SIG) 
                 
                # lower down thresholds to detect better in Bandpass filtered 
                THR_SIG1 = 0.5*(THR_SIG1)
                #THR_NOISE1 = 0.5*(THR_SIG1) 
                    
            else:
                m_selected_RR = mean_RR #the latest regular beats mean
    
            
            # calculate the mean of the last 8 R waves to make sure that QRS is not
            # missing(If no R detected , trigger a search back) 1.66*mean
               
            if m_selected_RR:
                test_m = m_selected_RR #if the regular RR availabe use it   
            elif mean_RR and m_selected_RR == 0:
                test_m = mean_RR   
            else:
                test_m = 0
                
            if test_m:
                if (locs[i] - qrs_i[-1]) >= round(1.66*test_m): # it shows a QRS is missed 
                    pks_temp = np.max(ecg_m[qrs_i[-1]+ round(0.200*fs):locs[i]-round(0.200*fs)]) # search back the max in this interval
                    locs_temp = np.argmax(ecg_m[qrs_i[-1]+ round(0.200*fs):locs[i]-round(0.200*fs)]) # search locate the max in this interval
                    locs_temp = qrs_i[-1]+ round(0.200*fs) + locs_temp -1 #location 
                       
                    if pks_temp > THR_NOISE:
                        qrs_c.append(pks_temp)
                        qrs_i.append(locs_temp)
                        
                        # find the location in filtered sig
                        if locs_temp <= len(ecg_h):
                            y_i_t = np.max(ecg_h[locs_temp-round(0.150*fs):locs_temp])
                            x_i_t = np.argmax(ecg_h[locs_temp-round(0.150*fs):locs_temp])
                        else:
                            y_i_t = np.max(ecg_h[locs_temp-round(0.150*fs):])
                            x_i_t = np.argmax(ecg_h[locs_temp-round(0.150*fs):])
                        # take care of bandpass signal threshold
                        if y_i_t > THR_NOISE1:
                             qrs_i_raw.append(locs_temp-round(0.150*fs)+ (x_i_t-1))# save index of bandpass 
                             qrs_amp_raw.append(y_i_t) #save amplitude of bandpass 
                             SIG_LEV1 = 0.25*y_i_t + 0.75*SIG_LEV1 #when found with the second thres 
                      
                        not_nois = 1
                        SIG_LEV = 0.25*pks_temp + 0.75*SIG_LEV   #when found with the second threshold             
                else:
                    not_nois = 0
              
            
        # find noise and QRS peaks
        if pks[i] >= THR_SIG:
            
            # if a QRS candidate occurs within 360ms of the previous QRS,
            # the algorithm determines if its T wave or QRS
            if len(qrs_c) >= 3:
                 if (locs[i]-qrs_i[-1]) <= round(0.3600*fs):
                    Slope1 = np.mean(np.diff(ecg_m[locs[i]-round(0.075*fs):locs[i]])) #mean slope of the waveform at that position
                    Slope2 = np.mean(np.diff(ecg_m[qrs_i[-1]-round(0.075*fs):qrs_i[-1]])) #mean slope of previous R wave
                    if abs(Slope1) <= abs(0.5*(Slope2)):  # slope less then 0.5 of previous R
                        nois_c.append(pks[i])
                        nois_i.append(locs[i])
                        skip = 1 # T wave identification
                        # adjust noise level in both filtered and
                        # MVI
                        NOISE_LEV1 = 0.125*y_i + 0.875*NOISE_LEV1
                        NOISE_LEV = 0.125*pks[i] + 0.875*NOISE_LEV 
                    else:
                        skip = 0
    
            if skip == 0:  # skip is 1 when a T wave is detected       
                qrs_c.append(pks[i])
                qrs_i.append(locs[i])
              
                # bandpass filter check threshold
                if y_i >= THR_SIG1:
                      if ser_back:
                         qrs_i_raw.append(x_i)  # save index of bandpass 
                      else:
                         qrs_i_raw.append(locs[i]-round(0.150*fs) + (x_i - 1))# save index of bandpass 
                      qrs_amp_raw.append(y_i)# save amplitude of bandpass 
                      SIG_LEV1 = 0.125*y_i + 0.875*SIG_LEV1# adjust threshold for bandpass filtered sig
             
                # adjust Signal level
                SIG_LEV = 0.125*pks[i] + 0.875*SIG_LEV 
            
        elif (THR_NOISE <= pks[i]) and (pks[i] < THR_SIG):
             #adjust Noise level in filtered sig
             NOISE_LEV1 = 0.125*y_i + 0.875*NOISE_LEV1
             #adjust Noise level in MVI
             NOISE_LEV = 0.125*pks[i] + 0.875*NOISE_LEV 
        
        elif pks[i] < THR_NOISE:
            nois_c.append(pks[i])
            nois_i.append(locs[i])
            
            # noise level in filtered signal
            NOISE_LEV1 = 0.125*y_i + 0.875*NOISE_LEV1     
             #adjust Noise level in MVI
            NOISE_LEV = 0.125*pks[i] + 0.875*NOISE_LEV  
            
    
        # adjust the threshold with SNR
        if NOISE_LEV != 0 or SIG_LEV != 0:
            THR_SIG = NOISE_LEV + 0.25*(abs(SIG_LEV - NOISE_LEV))
            THR_NOISE = 0.5*(THR_SIG)
        
        # adjust the threshold with SNR for bandpassed signal
        if NOISE_LEV1 != 0 or SIG_LEV1 != 0:
            THR_SIG1 = NOISE_LEV1 + 0.25*(abs(SIG_LEV1 - NOISE_LEV1))
            THR_NOISE1 = 0.5*(THR_SIG1)
            
            
        # take a track of thresholds of smoothed signal
        SIGL_buf.append(SIG_LEV)
        NOISL_buf.append(NOISE_LEV)
        THRS_buf.append(THR_SIG)
        
        # take a track of thresholds of filtered signal
        SIGL_buf1.append(SIG_LEV1)
        NOISL_buf1.append(NOISE_LEV1)
        THRS_buf1.append(THR_SIG1)
    
        skip = 0        # reset parameters
        not_nois = 0    # reset parameters
        ser_back = 0    # reset bandpass param   
        
    if (gr==1):
        plt.scatter(qrs_i, qrs_c, marker='o', c='w', edgecolors='m')
        plt.plot(locs, NOISL_buf, linestyle='--', c='k', linewidth=2)
        plt.plot(locs, SIGL_buf, linestyle='--', c='r', linewidth=2)
        plt.plot(locs, THRS_buf, linestyle='--', c='g', linewidth=2)
        plt.show()
        if any(ax):
            ax[np.logical_not(ax).astype('bool')] = None 

    # modify by yenchun@nctu
    new_qrs_i_raw =[]
    windowSize = 0.1
    
    for ii in range(len(qrs_i_raw)):
        maxI = qrs_i_raw[ii]
        if(maxI-round(fs*windowSize) <= 0 ): 
            start = 0 
        else:
            start = maxI-round(fs*windowSize) 
        if(maxI+round(fs*windowSize) >= len(ecg)):
            endd = len(ecg)-1  
        else: 
            endd = maxI+round(fs*windowSize)
        
        tmpWin = np.arange(start,endd+1e-5).astype(int)
        maxA, maxI = ecg[tmpWin].max(), ecg[tmpWin].argmax()
        maxI = tmpWin[maxI]
        if( 0 < maxI < len(ecg)-1):
            rightSlpoe = ecg[maxI+1]-ecg[maxI]
            leftSlope  = ecg[maxI] - ecg[maxI-1]
            if(rightSlpoe<=0 and leftSlope >=0):
                new_qrs_i_raw = [new_qrs_i_raw, maxI]

    # overlay on the signals
    if (gr==1):
        plt.figure()
        az[0] = plt.subplot(311) 
        plt.plot(ecg_h)
        plt.title('QRS on Filtered Signal')
        plt.axis('tight')
        plt.scatter(qrs_i_raw,qrs_amp_raw,c='w',edgecolors='m')
        plt.plot(locs,NOISL_buf1,linewidth=2,linestyle='--',c='k')
        plt.plot(locs,SIGL_buf1,linewidth=2,linestyle='--',c='r')
        plt.plot(locs,THRS_buf1,linewidth=2,linestyle='--',c='g')
        
        az[1] = plt.subplot(312) 
        plt.plot(ecg_m)
        plt.title('QRS on MVI signal and Noise level(black),Signal Level (red) and Adaptive Threshold(green)')
        plt.axis('tight')
        plt.scatter(qrs_i,qrs_c,c='w',edgecolors='m')
        plt.plot(locs,NOISL_buf,linewidth=2,linestyle='--',c='k')
        plt.plot(locs,SIGL_buf,linewidth=2,linestyle='--',c='r')
        plt.plot(locs,THRS_buf,linewidth=2,linestyle='--',c='g')
        
        az[2] = plt.subplot(313) 
        plt.plot(ecg-np.mean(ecg)) # data
        plt.title('Pulse train of the found QRS on ECG signal')
        plt.axis('tight')
        plt.plot(np.tile(qrs_i_raw,[2, 1]), # R peak bar
             np.tile([min(ecg-np.mean(ecg))/2, max(ecg-np.mean(ecg))/2], [len(qrs_i_raw),1]).T,
             linewidth=2.5,linestyle='--',c='r')
        plt.show()
        
        if (gr==2):
            plt.figure(2)
            tm = np.arange(len(ecg))
            plt.plot(ecg, c='b',linewidth=1, label='ecg')
            plt.plot(ecg_m, c='r', linewidth=3, label='Moving Window') 
            plt.scatter(tm[new_qrs_i_raw], ecg(new_qrs_i_raw),
                        c='w', edgecolors='g', marker='o', linewidth=3.0,
                        label='R point')
            plt.legend(fontsize=25)
            name = 'Pan-tompkinRest'
            plt.title(name)
            plt.grid()
            plt.savefig('%s.png'%name)
    
    return qrs_amp_raw,qrs_i_raw,delay

def miniPTV2(batchSize, data, Fs):
    point = 0
    rTimeArray = np.array([])
    # 在資料兩個batchSize寬內找R點
    while( (point + 2*batchSize)-1 <= len(data) ):
        miniData = data[point:point+batchSize-1]
        qrs_amp_raw, r_time, delay = pan_tompkinV3(miniData,Fs,0)
        if(len(r_time)==0): # if not a empty list
            point = point + batchSize
        else:
            r_time = np.asarray(r_time) + point -1     # 修正時間點
            point = r_time[-1]+1          # 找下一次的開頭
            rTimeArray = np.append(rTimeArray, r_time)

    
    # 在資料剩餘sample中找R點
    miniData = data[point:]
    qrs_amp_raw, r_time, delay = pan_tompkinRest(miniData,Fs,0)
    if(len(r_time)==0):
        point = point + batchSize
    else:
        r_time = np.asarray(r_time) + point -1 
        point = r_time[-1]+1
        rTimeArray = np.append(rTimeArray, r_time)
            
    # --------- find misssing R ----------
    deltaR = np.array([])     # RR interval
    for j in range(len(rTimeArray)-1):
        deltaR = np.append(deltaR, abs(rTimeArray[j+1]-rTimeArray[j]))

    FinalR = rTimeArray
    return FinalR, deltaR

def miniPTV3( batchSize, data, Fs, delta):
    point = 0 
    rTimeArray = np.array([])
    while( (point + batchSize)-1 <= len(data) ):
        miniData = data[point:point+batchSize-1]
        qrs_amp_raw, r_time, delay = pan_tompkinV3(miniData,Fs,0)        
        r_time = np.asarray(r_time) + point -1 
        rTimeArray = np.append(rTimeArray,r_time)
        point = point + int(delta)
        # 這裡多餘，可把while改成小於
        if( (point + batchSize)-1 == len(data)):
            break

    
    rTimeArray = sorted(rTimeArray)
    rTimeArray = np.unique(rTimeArray)
    
    deltaR = np.array([])
    for j in range(len(rTimeArray)-1):
        deltaR = np.append(deltaR, abs(rTimeArray[j+1]-rTimeArray[j]) )
        
    return rTimeArray, deltaR

def makeCNNdata(inputData, sampleRate, QRSid2, blockNumber, blocklength,
                pngtitle, saveOP, pngnameFilePath):

    fig1 = plt.figure(0)
    fig1.set_visible(False)
    # set(gcf, 'Units', 'Normalized', 'OuterPosition', [0 0 1 1])
    
    pixel_width = 20
    QRSid2 = np.asarray(QRSid2).astype(int)
    RRid = np.zeros(blockNumber,dtype=int) # 各段起始sample index
    inputData1 = np.zeros([blockNumber, blocklength])
    tmN = np.zeros([blockNumber, blocklength])
    
    for k in range(blockNumber):
        RRid[k] = QRSid2[QRSid2 > sampleRate*(k)][0]
    
    for k in range(blockNumber):
        inputData1[k,:] = inputData[RRid[k]:RRid[k]+blocklength]
        tmN[k,:] =  np.arange(RRid[k],RRid[k]+blocklength)/sampleRate
    
    for k in range(blockNumber):
        plt.subplot(blockNumber,1,k+1)
        plt.plot(tmN[k,:],inputData1[k,:], linewidth=1.5)
        plt.xlim([min(tmN[k,:]), max(tmN[k,:])])
    
    inputData2 = inputData1
    
    tmp = np.zeros([blockNumber*pixel_width, blocklength])
    for k in range(blockNumber):
        tmp[k*pixel_width:(k+1)*pixel_width,:] = np.tile(inputData2[k,:], [pixel_width,1]) # 像素厚度為20
    
    inputData3 = tmp
    inputData3 = (inputData3-np.min(inputData3))/np.max(inputData3) # map [0,1]
    
    output = inputData3
    
    plt.subplot(blockNumber+1,1,blockNumber+1)
    plt.imshow(inputData3)
    plt.xlim([0, blocklength])
    plt.suptitle(pngtitle)
    
    if saveOP:
        plt.savefig(fig1, pngnameFilePath, 'png')

    return np.array(output)
