import pymongo
import numpy as np
from scipy import signal
from  r_peak_align import pan_tompkinV3
from util import filter_
import sys

class MongoDB():
    def __init__(self, args):
        self.myclient = pymongo.MongoClient(args.mongoaddress)
        self.mydb = self.myclient[args.db]
        self.patient_time = {} # map[userId]lasttime_12lead
        self.patient_info = [] # array of patient info => {userId, Status, Denoise_ON, lasttime_3lead}
        self.history_patientList = []
        self.timeinterval = args.timeinterval
        self.SampleRate=args.SampleRate
        self.args = args
        self.cor_hist = [0 for _ in range(10)]
        self.count = [0 for _ in range(10)]
        self.cor_each = np.zeros([5,100])
        
    def pack_patientInfo(self, userId, lasttime_3lead, status=1, denoise_ON=0):
        patient_info ={}
        patient_info['userId'] = userId
        patient_info['lasttime_3lead'] = lasttime_3lead
        patient_info['Status'] = status
        patient_info['Denoise_ON'] = denoise_ON # Set default to off

        # New patient => get its lasttime_12lead from mongoDB and update patient_time
        if patient_info['userId'] not in self.patient_time:
            collection = self.mydb['user']
            query = {'userId': userId}
            result = collection.find_one(query)
            self.patient_time[patient_info['userId']] = result['lasttime_12lead']
                
        self.patient_info = [patient_info]
        return patient_info
    
    def find_rr(self, patientInfo, datas):
        '''
        input : patient user --> ID status lasttime_3lead lasttime_12lead
        return : the r r start time
        '''
        start_time = patientInfo['lasttime_3lead'] - self.args.timeinterval - self.args.rpeak_time #100-5-5 = 90
        try:
            print(f'Patient:{patientInfo["userId"]} into qeury 3 lead ecg', file=sys.stderr)
            ecg3, sec = self.pack_3leadEcg(datas, start_time, patientInfo['lasttime_3lead'])
        except:
            print(f'Error: in query 3lead\nEcg shape: {ecg3.shape}\nSec: {sec}\nPatientInfo: {self.patient_info}', file=sys.stderr)

        if sec <= 0 or sec != self.args.rpeak_time + self.timeinterval:
            print(f'Error: find_rr data length <= 0 || data length != rpeak_time + timeinterval', file=sys.stderr)
            return False, 0, 0
        
        print(f'Patient:{patientInfo["userId"]} find r peak', file=sys.stderr)
        _, r_list, _= pan_tompkinV3(ecg3[0,:,0], fs=256, gr=0)
        if len(r_list) < 2:
            print(f'Error: len(r_list) < 2 (Lack of R peak)', file=sys.stderr)
            return False, 'no two r_peak', 0
        
        # Get the middle point of the first two RR point
        r_wave = int((r_list[1] + r_list[0])/2) 
        start_time = start_time + 1 + r_wave // self.args.hz 
        r_dicimal = r_wave % self.args.hz
        if r_wave // self.args.hz > self.args.rpeak_time:
            print(f'Error: r_wave index is too big', file=sys.stderr)
            return False, _, _
        
        # Cut ecg3 starting with middle RR end with middle RR + 1280 (256Hz * 5sec)
        ecg3 = ecg3[:,r_wave:r_wave+1280,:]
        if ecg3.shape[1] != 1280:
            print(f'Error: ecg3.shape[1] != 1280', file=sys.stderr)
            return False, 'shape not 1280', _
        
        print(f'Patient:{patientInfo["userId"]} set rr mid point in mongo', file=sys.stderr)
        for info in self.patient_info:
            if info['userId'] == patientInfo['userId']:
                info['start_time'] = start_time 
                info['r_decimal'] = r_dicimal
                break
        return start_time, r_dicimal, ecg3 
    
    def pack_3leadEcg(self, datas, start_time, end_time):
        diff1=np.array([])
        diff2=np.array([])
        diff3=np.array([])
        second = 0
        interval = end_time - start_time
        
        for getdata in datas:
            second += 1
            diff1_tmp = np.array(getdata['Diff_1'])
            diff2_tmp = np.array(getdata['Diff_2'])
            diff3_tmp = np.array(getdata['Diff_3'])
            diff1 = np.append(diff1, diff1_tmp)
            diff2 = np.append(diff2, diff2_tmp)
            diff3 = np.append(diff3, diff3_tmp)
            
        test_in = np.array([diff1,diff2,diff3])*1000 # unit: volt to mV    
        test_in = test_in.transpose((1,0)).reshape([1,-1,3])
        if len(test_in) == 0:
            return test_in, 0
        
        # filter 
        if test_in.shape[1] == 256:
            test_in = filter_(data=test_in, fs=256.0, sec=interval)
        elif test_in.shape[1] == 500:
            test_in = filter_(data=test_in, fs=500.0, sec=interval)
        
        if test_in.shape[1] != interval * 256:
            test_in = signal.resample(test_in, interval * 256, axis=1)
        return test_in, second
                
    def ECG_Update(self, patientID, output):
        '''
        Convert 9 Leads ECG into 12 Leads ECG 
        [b,1280,9]
        Input: output (9 Leads ECG), LI LII aVR V1 V2 V3 V4 V5 V6 
        synthesizedECG (12 Leads ECG) LI LII LIII aVR aVF aVL V1 V2 V3 V4 V5 V6
        insert and update time
        '''  
        A=[[-1,0,1],[-1,1,0],[1,-1/2,-1/2]]
        A=np.array(A)  #(3,3)
        out = np.array([])
        for i in range(output.shape[0]):
            b_syn=[output[i,:,0],output[i,:,1],output[i,:,2]] #LI LII aVR
            b_syn2=np.array(b_syn) #(3, 1280)
            syn=np.linalg.pinv(A).dot(b_syn2)  #(3, 1280) #RA LL LA
            RA_syn=syn[0,:] #(1280,)
            LL_syn=syn[1,:]
            LA_syn=syn[2,:]
            LeadIII_syn=LL_syn-LA_syn #(1280,) LIII = LL -LA
            aVL_syn=LA_syn-1/2*(RA_syn+LL_syn) #(1280,) aVL = LA-0.5*(RA+LL)
            aVF_syn=LL_syn-1/2*(RA_syn+LA_syn) # aVF = LL-0.5*(RA+LA)
            synthesizedECG=np.array([output[i,:,0],output[i,:,1],LeadIII_syn,output[i,:,2],aVL_syn,aVF_syn,output[i,:,3] \
                                    ,output[i,:,4],output[i,:,5],output[i,:,6],output[i,:,7],output[i,:,8]]) #(12,1280)
            synthesizedECG = np.expand_dims(synthesizedECG,axis=0)
            if i == 0:
                out = synthesizedECG
            else:
                out = np.concatenate([out,synthesizedECG],axis=0)
        # print(f'out shape {out.shape}')
        
        try:
            self.ECG12_Insert(out)
        except:
            print(f'Error: ECG12_Insert', file=sys.stderr)
            
        try:
            self.Update_Time(patientID)
        except KeyError as e:
            print(f'Error: Update_Time() {e}', file=sys.stderr)

    def ECG12_Insert(self, syn12):
        '''
        realtime  12lead insert Mongo
        '''
        mycol = self.mydb[self.args.collection_12lead]
        ecgdata = []
        p_n = 0
        err = False
        for p in range(syn12.shape[0]):
            while 'start_time' not in self.patient_info[p_n].keys():
                if p_n >= len(self.patient_info):
                    err = True
                    break
                p_n += 1

            if err:
                print(f'Error: ECG12_Insert - no patient has start_time filed\npatient info: {self.patient_info}', file=sys.stderr)
                
            syn12_p = syn12[p,:,:] #[12,1280]
            userId = str(self.patient_info[p_n]['userId'])
            starttime = int(self.patient_info[p_n]['start_time'])+1
            r_decimal = int(self.patient_info[p_n]['r_decimal'])
            s_point = self.args.hz-r_decimal 
            e_point = self.args.hz*(1+self.args.timeinterval-1-self.args.cut_sec) - r_decimal 
            syn12_p = syn12_p[:,s_point:e_point]
            print(f"userId:{userId}", file=sys.stderr)
            for i in range(self.timeinterval - 1 - self.args.cut_sec):
                if starttime + i <= self.patient_time[userId]:
                    continue
                syn12_list = syn12_p[:,self.SampleRate*i:self.SampleRate*(i+1)].tolist()
                mydic={"userId":userId,'time':starttime+i,'I':syn12_list[0],'II':syn12_list[1],'III':syn12_list[2],\
                        'aVR':syn12_list[3],'aVL':syn12_list[4],'aVF':syn12_list[5],'V1':syn12_list[6],'V2':syn12_list[7],\
                        'V3':syn12_list[8],'V4':syn12_list[9],'V5':syn12_list[10],'V6':syn12_list[11]}
                print(f'InsertTime:{starttime+i}', file=sys.stderr)
                self.patient_time[userId] = starttime+i
                ecgdata.append(mydic)
            p_n+=1
        
        if len(ecgdata) > 0:
            mycol.insert_many(ecgdata)
    
    def Update_Time(self, userId):
        '''
        realtime : update the last ecg12 time
        '''
        lasttime = self.patient_time[userId]
        mycol = self.mydb["user"]
        myquery={'userId':userId}
        UpdateTime = {"$set":{'lasttime_12lead':lasttime}} #97
        mycol.update_one(myquery, UpdateTime)
     