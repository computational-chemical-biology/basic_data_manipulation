import ftplib
import re
import sys

#ftp://massive-ftp.ucsd.edu/v02/MSV000083183/
def downloadMassIVE(massive_url):
    ftp = ftplib.FTP("massive-ftp.ucsd.edu")
    ftp.login('anonymous', 'password')
    dr = re.sub('.+edu/(.+)', '\\1', massive_url)
    ftp.cwd(dr)
    # print mzxml files 
    fls = ftp.nlst('peak/mzxml')
    if len(fls):
        for f in fls:
            fo = f.split('/')[-1]
            print(f'Downloading {fo}...')
            ftp.retrbinary("RETR " +f, open(fo, 'wb').write)
    else:
        print('No mzxml file found')
    ftp.quit()


if __name__=='__main__':
    downloadMassIVE(sys.argv[1])
