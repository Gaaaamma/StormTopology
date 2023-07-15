ORIGINAL_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=~/miniconda3/envs/gputest/lib:$LD_LIBRARY_PATH
~/miniconda3/envs/gputest/bin/python $1

