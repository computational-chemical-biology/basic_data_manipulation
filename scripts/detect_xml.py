import xmltodict
import os
fls = [x for x in os.listdir() if '.xml' in x]

for f in fls:
    try:
       with open(f) as fd:
            doc = xmltodict.parse(fd.read())
       print(f'The file {f} is a xml')
    except:
       print(f'The file {f} is not a xml')
