txt = '''PWY-3022
PWY-5706
PWY-6531
PWY-7957
PWY-8190
PWY-8273
PWY-8475
PWY-8477
PWY-8483
PWY-8484
PWY-8492
PWY-8493
PWY-8494
PWY-8495
PWY-8496
PWY-8498
PWY-8504
PWY-8505
PWY-8506
PWY-8508
PWY-8511
PWY-8512
PWY-8523
PWY-8524
PWY-8525
PWY-8526
PWY-8527
PWY-8528
PWY-8529
PWY-8531
PWY-8532
PWY-8543
PWY2PN3-13
PWY2PN3-14
PWY2SK3-2'''
txt.split('\n')
pth = txt.split('\n')
url = 'https://websvc.biocyc.org/getxml?id=META:%s'
import xmltodict
import requests
for p in pth:
    tmp = url % p
    r = requests.get(tmp)
    with open(f'{p}.xml', 'w') as f:
        f.write(r.text)
%history -f download_pwy.py
