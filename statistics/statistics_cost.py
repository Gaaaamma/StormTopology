from decimal import Decimal
FILE_NAME = "stormTimestamp.txt"

# Open file
fp = open(FILE_NAME, "r")
line = fp.readline()
 
index = 1
getEcgTime = []
getStoreDone = []
diff = []

infDic = {}
infAvgCount = 0

# Parsing data
while line:
    split = line.split(": ")
    if (split[0] == "GET_ECG_DATA"):
        getEcgTime.append(int(split[1]))
    
    if (split[0] == "MI_STO_DONE."):
        getStoreDone.append(int(split[1]))

    if (split[0][0:6] == "InfAVG"):
        infAvgCount += 1
        info = split[0].split("_")
        if (info[1] in infDic) :
            infDic[info[1]] += float(info[2])
        else:
            infDic[info[1]] = 0.0
            infDic[info[1]] += float(info[2])

    line = fp.readline()

# Calculate each diff
for i in range(0, len(getEcgTime)):
    print(index, end = ": ")
    print(getEcgTime[i], end = ", ")
    print(getStoreDone[i], end = " => ")
    print(getStoreDone[i] - getEcgTime[i], end = "ms\n")
    diff.append(getStoreDone[i] - getEcgTime[i])
    index += 1

# Generate report
maxLatency = 0
minLatency = 100000
sum = 0
for num in diff:
    if (num > maxLatency):
        maxLatency = num
    if (num < minLatency):
        minLatency = num
    sum += num

avg = Decimal(sum / len(diff)).quantize(Decimal('1.00'))
print("\nReport: " + FILE_NAME)
print("Round: " + str(len(diff)))
print("AvgLatency: " + str(avg) + "ms")
print("MinLatency: " + str(minLatency) + "ms")
print("MaxLatency: " + str(maxLatency) + "ms\n")

for k in infDic:
    print(f'pid {k}: {round(infDic[k] / (infAvgCount / len(infDic)), 2)}ms')

fp.close()