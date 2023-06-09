# HF with GPU
1. Insall GPU driver
2. Go to Pytorch website and find the corresponding torch and cuda version (https://pytorch.org/get-started/previous-versions/)
3. Create a conda environment
```shell
conda create -n hfgpu python=3.9.16
```
4. Switch to the environment
```shell
conda activate hfgpu
```
5. Use conda to install pytorch and cuda (HF pytorch version is 1.11.0)
```shell
conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 cudatoolkit=11.3 -c pytorch
```
6. Use pip and requirements_gpu.txt to download HF inference dependencies
```shell
pip install -r requirements_gpu.txt 
```
7. Now you have a conda environment that can run HF service and use the resource of GPU