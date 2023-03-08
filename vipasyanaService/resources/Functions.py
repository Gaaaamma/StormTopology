# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 23:22:29 2021
History:
    20211011 -- Create Function.py
    20211029 -- Add Freq removal filter

@author: mbwcl
"""
import numpy as np
import os
import time
import scipy.signal as ss
import scipy.io as sio
from scipy.fft import fft,ifft,fftshift
import matplotlib.pyplot as plt

from yenchun_make_data import pan_tompkinV3, miniPTV2, miniPTV3, makeCNNdata

def MakeDir(serialNumber):
    List = os.listdir()
    if "result" not in List:
        os.mkdir("result")
        resDir = os.listdir("result")   
    else:
        resDir = os.listdir("result")   
        
        
    if "statistic" not in resDir:
        os.mkdir("result/statistic")
        staDir = os.listdir("result/statistic")
    else:
        staDir = os.listdir("result/statistic")
    if serialNumber not in staDir:
        os.mkdir("result/statistic/"+serialNumber)
        
        
    if "confusionMatrix" not in resDir:
        os.mkdir("result/confusionMatrix")
        conDir = os.listdir("result/confusionMatrix")
    else:
        conDir = os.listdir("result/confusionMatrix")
    if serialNumber not in conDir:
        os.mkdir("result/confusionMatrix/"+serialNumber)
                
        
    if "output_model" not in List:
        os.mkdir("output_model")    
    
    if "pic" not in List:
        os.mkdir("pic")

def acc(predict, answer):
    N = len(predict)
    acc = 0 
    for i in range(N):
        if sum(abs(predict[i,:]-answer[i,:]))==0:
            acc = acc+1
    acc = acc/N*100
    print("Comprehensive accuracy = %2.3f%%" % acc)
    return N

def confusionMatrix(predict, answer):
    cMat = np.zeros([3,3]) if predict.shape[1]==3 else np.zeros([2,2])
    N = len(predict)
    for i in range(N):
        p = np.array(predict[i,:]).reshape(-1,1)
        a = np.array(answer[i,:]).reshape(-1,1)
        cMat = cMat + a @ p.T    
    return cMat

def statistic(conf_mat, N):
    epsilon = 1e-10 # 避免出現divided by 0 
    TN = conf_mat[0,0]
    TP = conf_mat[1,1]
    FP = conf_mat[0,1]
    FN = conf_mat[1,0]
    
    accu = (TP + TN) / N
    print("accurarcy=\t%3.3f" % accu)
    speci = TN / (TN + FP + epsilon)
    print("specificity=\t%3.3f" % speci)
    prec = TP / (TP + FP + epsilon)
    print("precision=\t%3.3f" % prec)
    recall = TP / (TP + FN + epsilon)
    print("recall=\t\t%3.3f" % recall)
    F1_score = 2/(1/(prec+epsilon)+1/(recall+epsilon))
    print("F1_score=\t%3.3f" % F1_score)

    return accu,speci,prec,recall,F1_score

def hotBit(inputs, threshold=0.7):
    """
    將輸出機率轉換成0 或 1
    """
    outputs = np.zeros(inputs.shape)
    outputs = inputs>=threshold
    outputs = np.array(outputs,dtype=int)
    return outputs

def checkNormal(scores):
    """
    確保有MI的標記的人沒有Normal的標記
    """
    scores = np.asarray(scores).reshape(-1,1)
    labels = np.zeros([scores.shape[0],2])
    labels[:,0:1] = np.asarray(np.logical_not(scores),dtype=int) 
    labels[:,1:2] = scores
    return labels

def merge3lead(ch1,ch2,ch3):
    x = np.zeros([8042,120,368,3])
    
    ch1 = np.asarray(ch1)
    ch2 = np.asarray(ch2)
    ch3 = np.asarray(ch3)
    for j in range(8042):
        x[j,:,:,0] = ch1[:,:,j].T
        x[j,:,:,1] = ch2[:,:,j].T
        x[j,:,:,2] = ch3[:,:,j].T
    return x

def shuffle(x, y, idx=None,  Nfold=0, seed=309513023):
    y = y.flatten()
    np.random.seed(seed)
    N = len(x)  # Total patient number
    rndList = np.arange(N)
    np.random.shuffle(rndList)
    
    # Get interval
    trainInterval = np.append(np.arange(N//10*min(0,Nfold), N//10*(Nfold)), 
                              np.arange(N//10*(Nfold+1), N//10*(max(10,Nfold))))
    trainInterval = np.append(trainInterval, np.arange(N//10*10, N))
    testInterval = np.arange(N//10*Nfold, N//10*(Nfold+1))
    
    x_ta, x_te = x[rndList[trainInterval],...], x[rndList[testInterval],...]
    y_ta, y_te = y[rndList[trainInterval],...], y[rndList[testInterval],...]
    idx_ta, idx_te = idx[rndList[trainInterval],...], idx[rndList[testInterval],...]
    return x_ta,y_ta,idx_ta,x_te,y_te,idx_te
        
def make_2d_temp(x, verbose=0):
    """將10秒心電圖資料轉成條紋圖"""
    start = time.time() # count cost time
    
    x = ss.resample(x,1250,axis=1)
    n_data, *_, n_lead = x.shape
        
    is_save_png_name = 0
    
    sample_rate = 125
    data_length = sample_rate*10
    
    block_length = round(sample_rate*2.94)    # 區間為 3 sec
    block_number = 6                          # 6個區間

    bigCNN2D = np.zeros([n_data, 120, block_length, n_lead],dtype=np.float32)
    MI_data = np.full(n_lead, None)
    output = np.full(n_lead, None)
    
    if verbose==1: print(f"Generate 2D temporal data\nNow processing on:{' '*9}", end="", flush=True)
    outlier = []
    # For i-th data
    for i in range(n_data):
        if verbose==1: print('\b'*9+f"{i+1:4d}/{n_data:4d}", end="", flush=True)
        
        for c in range(n_lead):
            MI_data[c] = x[i,:data_length,c]
    
        # 使用第一導極第一次取 R peak
        qrs_amp_raw, QRSid, delay = pan_tompkinV3(MI_data[0],sample_rate,0)
        batchSize = 3*sample_rate
        # 第二次取 R peak並找出R-R區間長的中位數
        FinalR, deltaR = miniPTV2(batchSize, MI_data[0], sample_rate)
        shiftDelta = np.round(np.median(deltaR)/2)
        # 第三次取 R peak
        QRSid2, deltaR = miniPTV3(batchSize, MI_data[0], sample_rate, shiftDelta)
        deltaR = deltaR/sample_rate
        
        tm = np.arange(len(MI_data[0]))
        tm = tm/sample_rate
        
        png_name_file_path = 'png/%d_CNN' % (i)     
        png_title = ""
    
        for c in range(n_lead):
            MI_data[c] = (MI_data[c]-MI_data[c].mean())/MI_data[c].std()
            output[c] = makeCNNdata(MI_data[c], sample_rate, QRSid2, block_number,
                                    block_length, png_title, is_save_png_name,
                                    png_name_file_path)
            
            bigCNN2D[i,:,:,c] = output[c]
            
    cost_time = time.time()-start
    if verbose==1: 
        print("\nComplete data: %4d/%4d, Cost: %d hr %d min %d sec" \
          %(len(bigCNN2D),n_data, cost_time//3600, cost_time%3600//60, cost_time%60))

    return bigCNN2D

def stft(x, fs=500, pt=120, step=50):
    '''
    將data以fs為區間做fs點的FFT後，取pt間距。
    '''
    operN = (x.shape[1]-fs)//step+1 # 做FFT次數
    y = np.zeros([len(x),120,int(operN),3])
    for j in range(len(x)):
        for k in range(x.shape[-1]):
            data = np.array(x[j,:,k])   
            for i in range(operN):
                data_select = data[step*i:step*i+fs] * np.hamming(fs)
                data_fft = np.abs(fft(data_select,fs))**2 # 做Fs-pt FFT
                data_fft = (data_fft[0:pt])/fs # 取0以及正頻
                y[j,:,i:i+1,k] = data_fft.reshape(-1,1)             
    return y

def freq_removal(x, fs=256, f_stop=0.3,is_clip=False):
    fft_len = x.shape[1]
    eps = 1e-6
    X = fft(x, fft_len, axis=1)
    f = np.arange(fft_len)/fft_len*fs
    f_cut = f_stop+eps
    freq_mask = np.logical_or(f<=f_cut, f>=fs-f_cut)
    X[:,freq_mask,:] = 0
    y = np.real(ifft(X,fft_len, axis=1))
    # 如果為two-step filter那就只取第3~8秒來移除暫態效應
    if is_clip:
        fs = 256
        time_mask = np.arange(3*fs,8*fs)
        y = y[:,time_mask,:]
    return y

def HPF_by_butter(x, is_pad=False):
    sos = sio.loadmat('butter_6_order_256Hz_fc_1e-2.mat')['sos']
    sos = np.ascontiguousarray(sos)
    if is_pad: 
        x = np.append(x,x,axis=1)
        x = np.append(x,x,axis=1)
    y = ss.sosfilt(sos,x,axis=1)
    if is_pad: y = y[:,-2560:,:]
    return y

def get_3_diff(x):
    if x.shape[-1]==12:
        y = np.stack([x[...,6]-x[...,7],x[...,8]-x[...,9],x[...,10]-x[...,11]],axis=-1)
    else:
        y = x
    return y


def pre_processing(x, is_clip=False, is_pad=False):
    tmp = HPF_by_butter(x, is_pad=is_pad)
    tmp = freq_removal(tmp,is_clip=is_clip)
    tmp = get_3_diff(tmp)
    return tmp

def tfplot(x, fs, mode=0,name=None):
    fft_n = len(x)
    
    t = np.arange(len(x))/fs
    f = (np.arange(fft_n)-fft_n//2)/fft_n*fs
    X = abs(fftshift(fft(x,fft_n)))/fft_n
    fig = plt.figure(figsize=(16,5),dpi=300) if mode==0 else plt.figure(figsize=(8,5))
    
    if mode==0 or mode==1:
        if mode==0: plt.subplot(121)
        plt.plot(t,x)
        plt.title(name+':time-domain' if name else 'time-domain')
        plt.xlabel('sec')
        plt.ylabel('mV')

    if mode==0 or mode==2:
        if mode==0: plt.subplot(122)
        plt.plot(f,X)
        plt.title(name+'frequency-domain' if name else 'frequency-domain')
        plt.xlabel('Hz')
        plt.ylabel('Amplitude')
        plt.xlim((-5,5))
        
    plt.show()














    
    
    