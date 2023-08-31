# Vipasyana service built on Apache Storm
If you want to use this system, you must install
- Apache Zookeeper (Communication method between nodes in Apache Storm cluster)
- Apache Storm 2.4.0
- Java openjdk 8

You can follow the install instruction from the office<br>
(There is also installation command I gave below)

**Now, you are able to use Apache storm to create your own topology.<br>**
**If you want to use the topology of vipasyana service, you must do more configuration**
- Install Miniconda on all nodes
- Create virtual environment of each ai inference service (Ex: hfonly, mionly, vfonly, tf3to12)
- Install corresponding dependencies in the virtual environment
- Move xxxStart.sh to /usr/xxxStart.sh, and make it executable

## Install Zookeeper
1. Go to Apache-Zookeeper website the get the url of installation<br>
for example (https://dlcdn.apache.org/zookeeper/zookeeper-3.8.2/apache-zookeeper-3.8.2-bin.tar.gz)<br>
You can use the command below to download the file
```shell
wget https://dlcdn.apache.org/zookeeper/zookeeper-3.8.2/apache-zookeeper-3.8.2-bin.tar.gz 
```

2. Extract the file, you will get Zookeeper
```shell
tar -xvf apache-zookeeper-3.8.2-bin.tar.gz
```

3. Set the config file of Zookeeper by your own
```shell
vim /THE/PATH/TO/ZOOKEEPER/conf/zoo.cfg
``` 

4. Suggestion config
```shell
# The number of milliseconds of each tick
tickTime=2000
# The number of ticks that the initial
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just
# example sakes.
dataDir=/home/wnalb/zk/zkDataDir
dataLogDir=/home/wnlab/zk/zkLogDir
# the port at which the clients will connect
clientPort=2181
# the maximum number of client connections.
# increase this if you need to handle more clients
#maxClientCnxns=60
#
# Be sure to read the maintenance section of the
# administrator guide before turning on autopurge.
#
# http://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance
#
# The number of snapshots to retain in dataDir
autopurge.snapRetainCount=20
# Purge task interval in hours
# Set to "0" to disable auto purge feature
autopurge.purgeInterval=24

## Metrics Providers
#
# https://prometheus.io Metrics Exporter
#metricsProvider.className=org.apache.zookeeper.metrics.prometheus.PrometheusMetricsProvider
#metricsProvider.httpPort=7000
#metricsProvider.exportJvmInfo=true
```
5. Now, you can follow (How to Start Up Storm Cluster) to start ZooKeeper

## Check system Java version
**Note: Apache Storm 2.4.0 work fine with openjdk-8-jdk**
1. Check if openjdk-8-jdk is installed
```shell
sudo apt list openjdk-8-jdk
```

2. If you haven't installed the jdk, just install it
```shell
sudo apt install openjdk-8-jdk
```

3. Check avaliable java version and choose to openjdk-8-jdk
```shell
sudo update-alternatives --config java
```

4. Check if the version of java is correct
```shell
java -version
```

5. AFter that you might get the following environment
```
openjdk version "1.8.0_352"
OpenJDK Runtime Environment (build 1.8.0_352-8u352-ga-1~22.04-b08)
OpenJDK 64-Bit Server VM (build 25.352-b08, mixed mode)
```

## Storm Config File
The config file is at<br> 
**$STORM_INSTALLED_DIR/apache-storm-2.4.0/conf/storm.yaml**
```
storm.local.dir: "/home/ytc/storm/local"
storm.zookeeper.servers:
  - "localhost"
#     - "server2"
# 
nimbus.seeds: ["192.168.2.132"]
# 
supervisor.slots.ports:
  - 6700
  - 6701
  - 6702
  - 6703
# 
ui.port: 6750

# Set worker heap size
worker.childopts: "-Xmx2g"
```

## How to Start Up Storm Cluster
1. Start the zookeeper service
```shell
zkServer.sh start
```
2. Start nimbus (on numbus host)
```shell
storm nimbus
```
3. Start supervisor (on all of worker host)
```shell
storm supervisor
```
4. Start storm UI
```shell
storm ui
```

## How to Build and Submit Topology
**Note: it is a simple tutorial**
- Please follow the Makefile to know how to compile and pack Bolt writing in Java and Python 
- Please follow experiment.sh to know how to submit the topology to Apache Storm numbus

1. Compile YYY.java and assign corresponding ClassPath (Some jar file and the path which is concatenated by :)
```shell
javac -cp xxxx.jar:yyy.jar:. YYY.java
```

2. Make jar file commited to nimbus:
```shell
jar cvf test.jar storm-client-2.4.0.jar ExclamationBolt.class WordSpout.class  ExclamationTopology.class
```

3. If there is any external lib, put it in apache-storm-version/extlib (ALL the host must do)
```shell
cp kkk.jar $HOME/apache-storm-2.4.0/extlib/
```

4. Submit the topology to cluster (Under Apache Storm bin directory)
```shell
storm jar ZZZ.jar TopologyClass
```

## Tutorial: About ShellBolt Working directory 
Note that under Apche Storm ShellBolt, the working directory of python file will be<br>
the resources directory in the .jar file which you submit<br>
For example, we can see transfer3to12 service (TfEcgBolt.java)<br>
```Java
super("/usr/tf3to12Start.sh", "./tf3to12/tfEcgServerBolt.py");
```

It will execute tfEcgServerBolt.py under the path of ./resources/./tf3to12/tfEcgServerBolt.py<br>

Thus, all your python file might assume that ./resources is your working directory.<br>
We can see that in resources/tf3to12/tfEcgServerBolt.py<br>
args_parameter() => ('--modelPath',type=str,default='./tf3to12/step99500.ckpt.meta')<br>

It loads model from ./tf3to12/XXX.ckpt.meta rather than ./XXX.ckpt.meta even they are in the same directory<br>
If you load the path ./XXX.ckpt.meta directly, you will get error message telling you that you are not able to find the file<br>

**NOTE: But when you are importing other files in python, you can import directly as they are in the same directory**<br>
(See resources/tf3to12/tfEcgServerBolt.py)
```Python
from torch_model import Model3to12
from dbOperation import MongoDB 
```
That is weird, but just follow it

## ShellBolt python version (Pyenv) (Deprecated)
- Deprecated
- But learning it will help you know miniconda (Using in system now)

Note that in ShellBolt, this might execute /usr/bin/python (Guess)<br>
So it won't be affected by pyenv to switch versions between python<br>
```Python
super("python", "myExector.py")  
```

How do I find this?<br>
**Experiment:**<br>
1. Try to switch python version(By pyenv) to 3.9.16 with no any python librarys installed,
2. All python process works well (No module name doesn't happen)

Then, we are going to modify the super command below<br>
and now we can use pyenv global {version}<br>
and will actually make the system's python version changed<br>
```Java
super("/home/ytc/.pyenv/shims/python", "myExecutor.py")
```
(Now No module name occurs)<br>

Notice that all the command below can't be used<br>
```Java
super("$HOME/.pyenv/shims/python", "myExecutor.py")
super("~/.pyenv/shims/python", "myExecutor.py")
```
So, we write a shell script which will execute ~/.pyenv/shims/python<br>
then, we can execute different python by modifing the content of this shell script<br>
The content in the file is now<br>
```shell
~/.pyenv/shims/python $1 
```

Finally, put it at /usr/pystart.sh (Remember to chmod +x this file)<br>
Now in ShellBolt, the actually command is<br>
```Java
super("/usr/pystart.sh", "myExector.py")  
```

## ShellBolt python version (Miniconda) (Using)
We also need a shellscript to help us execute python under a certain user<br>
because executing $HOME/... or ~/... is invalid<br>
```Java
super("/usr/hfonlyStart.sh", "hfInfServerBolt.py");
```

The content in such file is like this.<br>
And we can know that if we execute python under miniconda3/envs/MYENV/bin/python<br>
we can use the package and dependencies under this environment<br>
```shell
~/miniconda3/envs/hfonly/bin/python $1
```
