from decimal import Decimal
FILE_NAME = "FInf_100_4_1.txt"

# Open file
fp = open(FILE_NAME, "r")
line = fp.readline()
 
index = 1
getEcgTime = 0
getStoreDone = 0
diff = []

# Parsing data
while line:
    split = line.split(": ")
    if (split[0] == "GET_ECG_DATA"):
        getEcgTime = int(split[1])
    
    if (split[0] == "MI_STO_DONE."):
        getStoreDone = int(split[1])
        print(index, end = ": ")
        print(getEcgTime, end = ", ")
        print(getStoreDone, end = " => ")
        print(getStoreDone - getEcgTime, end = "ms\n")
        diff.append(getStoreDone - getEcgTime)
        index += 1

    line = fp.readline()

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

fp.close()