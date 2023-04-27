import os
import neurokit2 as nk
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader

from models.resnet_simclr import moECG, ResNet1D18SimCLR

class LVSDClassifier:
    def __init__(self, checkpoint):
        self.device = torch.device('cpu')
        self.model = moECG(ResNet1D18SimCLR(in_c=3))
        checkpoint = torch.load(os.path.join('weights', checkpoint), map_location=self.device)['state_dict']
        self.model.load_state_dict(checkpoint)
    
    def preprocess(self, ecgDatas):
        '''
        Apply a high-pass 5-order butterworth filter with lowcut 0.5Hz
        Drop the first and the last second

        Input:
            ecgDatas: [patient_num, 3, 3500] (7 seconds of 500Hz)
        Output:
            filteredEcgDatas: [patient_num, 3, 2500] (5 seconds of 500Hz)
        '''
        filteredEcgDatas = []
        for ecgData in ecgDatas:
            filteredEcgData = []
            for ecglead in ecgData:
                ecglead = nk.signal_filter(signal=ecglead, sampling_rate=500, lowcut=0.5, method='butterworth', order=5)
                ecglead = nk.signal_filter(signal=ecglead, sampling_rate=500, method='powerline')
                filteredEcgData.append(ecglead[500:3000])

            filteredEcgDatas.append(filteredEcgData)
        
        filteredEcgDatas = np.stack(filteredEcgDatas)
        return filteredEcgDatas
    
    def predict(self, ecgDatas, needPreprocess=True):
        '''
        Predict LVSD with 3-lead ECG input

        Input:
            ecgDatas:
                [patient_num, 3, 3500], if needPreprocess=True
                [patient_num, 3, 2500], if needPreprocess=False
        Output:
            model_pred: [patient_num]
                0: low-risk
                1: high-risk
        '''
        if needPreprocess:
            ecgDatas = self.preprocess(ecgDatas)
        
        dataset = TensorDataset(torch.tensor(ecgDatas, dtype=torch.float32))
        dataloader = DataLoader(dataset, batch_size=64)
        
        model_pred = []
        self.model.eval()
        with torch.no_grad():
            for X in dataloader:
                X = X[0]
                pred = self.model(X)
                model_pred.append(pred.argmax(1))

        model_pred = torch.cat(model_pred).cpu().numpy()
        return model_pred