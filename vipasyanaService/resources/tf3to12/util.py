import numpy as np
import scipy.signal as ss
import scipy.io as sio

def filter_(data: np.ndarray, fs: float,sec:int) -> np.ndarray:
    """
    PREPROCESS will apply a FIR-high-pass-filter on input data,
    and return the result.

    Parameters
    ----------
    data : np.ndarray
        Input ECG signal with dims (N, 10*fs, 3)
    
    fs : float 
        Input data sampling frequency
    Returns
    -------
    output : np.ndarray
        Outputs are the ECG without baseline wandering noise.
    """
    # print(f'input shape {data.shape}')
    if fs!=500:
        data = ss.resample(data, num=500*sec, axis=1)
    # print(f'data shape {data.shape}')
    fir_param = sio.loadmat("./FIR_500_order300.mat")['FIR_500_order300'].flatten() # (301, )
    output = np.zeros(data.shape)
    for i in range(data.shape[0]):
        for k in range(data.shape[2]):
            output[i,:,k] = ss.convolve(data[i,:,k], fir_param, mode='same')   
    return output

def evaluate(synthesized_data: np.ndarray, real_12_lead: np.ndarray):
    """
    synthesized_data : np.ndarray
        Data with dimension of (N, 1280, L)
        N - data number
        L - lead number. Default 12.
        
    real_12_lead : np.ndarray
        Data with dimension of (N, 1280, L)
        
    Returns
        Output dimension (N, L)
    """
    x_s = np.asarray(synthesized_data) 
    x_r = np.asarray(real_12_lead)
    cor_matrix = np.zeros([x_s.shape[0],x_s.shape[2]])
    for i in range(x_s.shape[0]):
        for j in range(x_s.shape[2]):
            xs = x_s[i,:,j] #1280
            xr = x_r[i,:,j] #1280
            xs_std = xs-np.mean(xs)
            xr_std = xr-np.mean(xr)
            upnum = np.sum(xs_std*xr_std)
            downnum = np.sqrt(np.sum(xs_std**2))*np.sqrt(np.sum(xr_std**2))
            cor_matrix[i,j] = np.divide(upnum,downnum)
    cc = np.divide(
        np.abs((x_s*x_r).sum(axis=1)),
        np.sqrt( ((x_s**2).sum(axis=1)) * ((x_r**2).sum(axis=1))) 
    )
    return cc

def get_user(lss):
    return lss.get('userId')