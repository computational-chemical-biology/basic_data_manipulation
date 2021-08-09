import pandas as pd

"""
   INSTRUCTIONS:

   IF YOU DO NOT HAVE PYTHON OR THE PYTHON PACKAGE PANDAS:
   . Install Anaconda: https://docs.continuum.io/anaconda/install/windows/
   . Be sure to have the script and the files you want to transpose in the same folder
   . Open the Anaconda prompt in Windows - Search for it by using the start menu
   . Use "cd directory name" to reach the folder in which the file you want to transpose is located
   . Type in "python transposing_data.py" in the command prompt
   . Start by filling in the name of the file you want to transpose
   
   IF YOU HAVE PYTHON, BUT NOT PANDAS:
   . Open the command prompt in Windows - Search for it by using the start menu
   . Be sure to have the script and the files you want to transpose in the same folder
   . Use "cd" to reach the folder in which the file you want to transpose is located
   . If you do not have the python package pandas, install it (https://pandas.pydata.org/pandas-docs/stable/install.html)
   . Type in "python transposing_data.py" in the command prompt
   . Start by filling in the name of the file you want to transpose
   
OBS: This works for CSV files separated by ';'

"""

#The text below has the purpose of receiving an input from the user

txt = input("Type in the name of the file you want to transpose: ")

#The following text is just to indicate that the file will now be transposed

print("Transposing file...:", txt)

df = pd.read_csv(txt + ".csv", sep = ";")

df.T.head()

dft = df.T

dft.to_csv(txt + "_transposed.csv", header = None)

print("File transposed!")
