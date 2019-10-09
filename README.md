## Basic data manipulation

This repository aims to collect basic methods to help people  with little programming background, to perform simple tasks, such as transposing a large matrix.

In order to do that, users are advised to read a starting guide to github [here](https://computational-chemical-biology.github.io/ccbl_tutorials/git/) and [here](https://guides.github.com/activities/hello-world/).

After that, users should `Fork` this repository, by clicking the `Fork` bottom on the top right hand corner of this repository. This will create a copy to the users account, where they can add code to their copies, and after that communicate the copies to the `master`repository with a [pull request](https://help.github.com/en/articles/creating-a-pull-request-from-a-fork).

## 1. Transposing Data

This script was made to help users transpose data easily. To use it, please follow the instructions below:

   IF YOU DO NOT HAVE PYTHON OR THE PYTHON PACKAGE PANDAS:
   * Install Anaconda: https://docs.continuum.io/anaconda/install/windows/
   * Be sure to have the script and the files you want to transpose in the same folder
   * Open the Anaconda prompt in Windows - Search for it by using the start menu
   * Use "cd directory name" to reach the folder in which the file you want to transpose is located
   * Type in "python transposing_data.py" in the command prompt
   * Start by filling in the name of the file you want to transpose
   
   IF YOU HAVE PYTHON, BUT NOT PANDAS:
   * Open the command prompt in Windows - Search for it by using the start menu
   * Be sure to have the script and the files you want to transpose in the same folder
   * Use "cd" to reach the folder in which the file you want to transpose is located
   * If you do not have the python package pandas, install it (https://pandas.pydata.org/pandas-docs/stable/install.html)
   * Type in "python transposing_data.py" in the command prompt
   * Start by filling in the name of the file you want to transpose

OBS: This works for CSV files separated by ';'

Example: 

``` 
Reaching the folder I have the script and files I want to transpose:

$ cd Documents/Scripts

Running the script:

$ python transposing_data.py

Fill in the information that is asking and press enter:

$ Type in the name of the file you want to transpose: 'NAME OF FILE'

Data will be transposed:

$ File transposed!

```






