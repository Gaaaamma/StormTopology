from decimal import Decimal
FILE_NAME = "stormTimestamp.txt"
REQUEST_PATIENT_NUM = 70

# Open file
fp = open(FILE_NAME, "r")
line = fp.readline()
 
getEcgTime = []
getStoreDone = {
    'MI': [],
    'HF': [],
    'VF': [],
    'AF': []
}

infDic = {
    'MI': {}, # pid: ms
    'HF': {},
    'VF': {},
    'AF': {}
}
countDic = {
    'MI': {}, # pid: numbers
    'HF': {},
    'VF': {},
    'AF': {}
}
diff = {
    'MI': [], # diff time between getEcg and STO_DONE
    'HF': [],
    'VF': [],
    'AF': []
}

# Parsing data
# HF_InfAVG_1684805_110.4: 1682604557088
# 0  1      2       3
while line:
    split = line.split(": ")
    if (split[0] == "GET_ECG_DATA"):
        getEcgTime.append(int(split[1]))
    else: 
        symptom = split[0][0:2]
        if (split[0][3:9] == "InfAVG"):
            info = split[0].split("_")
            if (info[2] in infDic[info[0]]): # If pid is in "SYMPTOM": {}
                infDic[info[0]][info[2]] += float(info[3])
                countDic[info[0]][info[2]] += 1
            else:
                infDic[info[0]][info[2]] = 0.0
                infDic[info[0]][info[2]] += float(info[3])
                countDic[info[0]][info[2]] = 1

        elif (split[0][3:11] == "STO_DONE"):
            getStoreDone[symptom].append(int(split[1]))
        
    line = fp.readline()

# Calculate each diff (Based on SYMPTOM_STO_DONE.)
for symptom in getStoreDone:
    index = 1
    preGetTime = 0
    preDoneTime = 0
    for i in range(0, len(getStoreDone[symptom])):
        print(f'{symptom} - {index}', end= ': ')
        print(getEcgTime[i], end = ', ')
        print(getStoreDone[symptom][i], end = " => ")
        print(getStoreDone[symptom][i] - getEcgTime[i], end = "ms")
        print(f'   ({getEcgTime[i] - preGetTime}ms, {getStoreDone[symptom][i] - preDoneTime}ms)')
        preGetTime = getEcgTime[i]
        preDoneTime = getStoreDone[symptom][i]
        diff[symptom].append(getStoreDone[symptom][i] - getEcgTime[i])
        index += 1
    print('')
    
###################################################
#                 Generate report                 #
###################################################
print(f'\nReport: {FILE_NAME}')
print(f'Request one time: {REQUEST_PATIENT_NUM}\n')

for symptom in getStoreDone:
    if (len(diff[symptom]) == 0): # No such inference
        continue
    maxLatency = 0
    minLatency = 10000000
    sum = 0
    for num in diff[symptom]:
        if (num > maxLatency):
            maxLatency = num
        if (num < minLatency):
            minLatency = num
        sum += num
    
    allPatient = REQUEST_PATIENT_NUM * len(diff[symptom])
    avg = Decimal(sum / len(diff[symptom])).quantize(Decimal('1.00'))
    print(f'{symptom}:')
    print("Round: " + str(len(diff[symptom])))
    print(f'Patient served: {allPatient}')
    print("AvgLatency: " + str(avg) + "ms")
    print("MinLatency: " + str(minLatency) + "ms")
    print("MaxLatency: " + str(maxLatency) + "ms")
    period = getStoreDone[symptom][len(getStoreDone[symptom]) - 1] - getEcgTime[0]
    print(f"Time cost: {period}ms ({round(period / 1000, 2)}sec)")
    print(f"Throughput: {round(allPatient / round(period / 1000, 2) * 10, 2)} (people/10sec)")
    for p in infDic[symptom]:
        print(f' - pid {p}: {round(infDic[symptom][p] / countDic[symptom][p], 2)}ms')
    print('')

fp.close()