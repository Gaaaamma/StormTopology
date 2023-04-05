import matplotlib.pyplot as plt

FILE_NAME = "MInf_150_4_f700_D2.txt"
SAVE_IMGFILE = FILE_NAME[0:-3] + "png"

# Open file
fp = open(FILE_NAME, "r")
line = fp.readline()

# Parsing data
latency = []
while line:
    split = line.split("=>")
    if len(split) <= 1:
        line = fp.readline()
        continue
    data = split[1].split("ms")
    latency.append(int(data[0]))
    line = fp.readline()

# Use data in latency to generate report(histogram)
plt.title(FILE_NAME)
plt.xlabel("Latency")
plt.ylabel("Count")
plt.hist(latency)
plt.savefig(SAVE_IMGFILE)
fp.close()