## Notice
gputest can run both mi and vtvf with GPU resource\n
The start up script is gputestStart.sh\n

When you install tensorflow, it will automatically install corresponding tensorflow-gpu resource.\n

What you need to do is shown below:\n

1. conda create -n gputest python=3.9.16 (Create conda virtual env)
2. pip install -r requirements.txt (Install dependencies) 
3. conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0 (Install corresponding cuda) 
4. Modify LD_LIBRARY_PATH to make tensorflow know where to find cuda
(You don't need to do step-4 yourself, gputestStart.sh will do it for you as you start the program)\n
Reference: https://blog.csdn.net/ly869915532/article/details/127126915
 
