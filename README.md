# JTeC: A Large Collection of Java Test Classes for Test Code Analysis and Processing
This repository is the companion for the dataset: 
> F. Coro,  R.  Verdecchia,  E.  Cruciani,  B.  Miranda,  and  A.  Bertolino, "JTeC:  A  large  collection  of  Java  test  classes  for test  code  analysisand  processing". Submitted for revision at MSR 2019 Data Showcase. [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2558714.svg)](https://doi.org/10.5281/zenodo.2558714) 
 
It contains the implementation of all the steps required in order generate our dataset, including: (i) filtering of GitHub repositories, (ii) Java repository selection, (iii) test classes identification, (iv) repository selection, and (v) local storage of test classes.

## Dataset replication

In order to replicate the dataset follow these steps:

1. Clone the repository 
   - `git clone https://github.com/MSR19-JTeC/JTeC`
 
2. Make sure to satisfy the following requirements:
    * Have Python 3.0+ installed
    * Possess a valid GitHub username and personal GitHub access token
    
3. Modify the file `token.txt` by changing the fields to your personal GitHub username and access token
   
4. Execute the script which launches in sequential order the JTeC generation steps (see Section "JTeC generation steps")
    - `sh JTeC_generator.sh`

## JTeC generation steps

The steps required in order to generate the dataset are implemented in the following 4 scripts, which have to be executed sequentially in the order given below. A brief description of the scripts is provided below:

1. [repository_filtering.py](https://github.com/MSR19-JTeC/JTeC/blob/master/repository_filtering.py) - Script generating an index of GitHub public repositories (Step 1). <br> The final output of this script consists of a local .csv file containing for each public repository indexed the following fields: _repositoryID_, _username of repository creator_, _name of the repository_, and _programming languages associated to the repository_

2. [selection_test_count.py](https://github.com/MSR19-JTeC/JTeC/blob/master/selection_test_count.py) - Script selecting Java repositories (Step 2) and identifying test classes of the selected repositories (Step 3). This script takes as parameter the programming language to be considered for the generation of the dataset, e.g. `selection_test_count.py Java`.<br>
The final output of this script consists of a local .csv file containing the following information: _user_, _repository_, _id_, _hash_, _date_, _n_tests_, _fork_id_.

3. [select.py](https://github.com/MSR19-JTeC/JTeC/blob/master/selection_test_count.py) - Script selecting among each forked project either the original or forked project according to which one contains more test classes (Step 4). <br>
The final output of this script consists of a local .csv file containing the following information: _user_, _repository_, _id_, _hash_, _date_, _n_tests_, _fork_id_.

4. [download_tests.py](https://github.com/MSR19-JTeC/JTeC/blob/master/download_tests.py) - Script downloading the test classes of the repositories selected by `repository_selection.py` (Step 5). <br>
This script takes as input the list of repositories for which we want to download the test classes and create the dataset. <br>
The final output of this script is: (i) the totality of the source code of the identified test classes, and (ii) a .csv file containing the following fields: _user_, _repository_, _id_,_fork_id_,_hash_, _date_, _n_tests_, _SLOC_, _size_

## Utility files

In addition to the scripts described in Section "JTeC generation steps", the dataset generation process makes use of two utility scripts and one utility file, namely:
* [request_manager.py](https://github.com/MSR19-JTeC/JTeC/blob/master/request_manager.py) - Script managing all GitHub requests and handling possible error arising at request time, returning eventually a specific error-number to the script that first sent the request.
* [credentials.py](https://github.com/MSR19-JTeC/JTeC/blob/master/credentials.py) - Script loading from the file `tokens.txt` the username and access tokens required to query the GitHub API.
* [token.txt](https://github.com/MSR19-JTeC/JTeC/blob/master/token.txt) - Text file containing the GitHub username and personal GitHub access token.
