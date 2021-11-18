import ftplib
import sys

if __name__=='__main__':
    user = sys.argv[1]
    password = sys.argv[2]
    filename = sys.argv[3]
    session = ftplib.FTP('massive.ucsd.edu', user, password)
    file = open(filename,'rb')
    session.storbinary('STOR NIST17/%s' % filename, file)
    file.close()
    session.quit()
