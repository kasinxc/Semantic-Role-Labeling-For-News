## Git clone repo

```Bash
git clone https://github.com/kasinxc/Semantic-Role-Labeling-For-News.git
```



## Install Python3 from Anaconda

https://docs.anaconda.com/anaconda/install/linux/

This is because, allennlp is python 3 dependent.



```Bash
bash Anaconda3-2019.03-Linux-x86_64.sh
source <path to conda>/bin/activate
conda init
```



## Intall Allennlp

``` Bash
pip install allennlp
```

or if failed

```Bash
conda create -n allennlp python=3.7
conda activate allennlp
```



## Install other dependencies

```bash
pip install networkx
pip install matplotlib
```

