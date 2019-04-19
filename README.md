# Semantic-Role-Labeling-For-News
Semantic Role Labeling for News.

We provide two demo for the news: 

> - Coreference Resolution Demo
> - Semantic Role Labeling Demo



## Coreference Resolution Demo

### > Play with Jupyter Notebook

#### 1. Enter the coreference resolution folder

```Bash
cd ./Source/COREF/
```

#### 2. Start jupyter notebook from command line, it will automatically open your browser 

```Bash
jupyter notebook
```

#### 3. Click coref_demo.ipynb

#### 4. Click run 



### > Play with terminal 

#### 1. Modify configuration

```bash
./Source/COREF/coref_config.py
```

#### 2. Start coref_visualization.py

```Bash
python3 coref_visualization.py 
```

Note that: if ./Result/COREF/Allennlp_Coref does not exist, it will automatically generate one and start predicting data using allennlp coreference resolution model. You can also do that by simply typing the command below from command line.

```Bash
python3 allen_coref_on_input_data.py
```





## Semantic Role Labeling Demo

### > Play with Jupyter Notebook

#### 1. Enter the semantic role labeling folder

```Bash
cd ./Source/SRL/
```

#### 2. Start jupyter notebook from command line, it will automatically open your browser 

```Bash
jupyter notebook
```

#### 3. Click srl_demo.ipynb

#### 4. Click run 



### > Play with terminal 

#### 1. Modify configuration

```bash
./Source/SRL/srl_config.py
```

#### 2. Start srl_visualization.py

```Bash
python3 srl_visualization.py 
```



Note that: Semantic role labeling may depend on the result of coreference resolution if the flag enable_coreference_resolution is set to true.

1. if ./Result/SRL/Allennlp_Srl does not exist, it will automatically generate one and start predicting data using allennlo semantic role labeling mode. 
2. For coreference resolution, as mentioned above, semantic role labeling may rely on its result. if ./Result/COREF/Allennlp_Coref does not exist, semantic role labeling will also automatically generate one and start predicting data using allennlp coreference resolution model. You can also do that by simply typing the command below from command line.

```Bash
python3 allen_coref_on_input_data.py
```

