import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os
from os.path import basename
import pandas as pd
import sys

'''usage

send_email <email> <password> <recipient table> <path>

recipient table - tsv, should have columns Código, Nome and e-Mail
path - path to files to be sent

optional positional parameters <message> and <subject> can be given, replacing default
'''

def sendEmail(email, password, message, recipient,
              subject, fl):
        server = smtplib.SMTP('smtp.gmail.com', 587)
	#server.starttls()
        server.connect("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email, password)

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = recipient
        msg['Subject'] = subject

        part1 = MIMEText(message, 'plain')
        msg.attach(part1)
        with open(fl, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(fl)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(fl)
        msg.attach(part)

        server.sendmail(email, recipient, msg.as_string())
        server.quit()


if __name__=='__main__':
    email = sys.argv[1]
    password = sys.argv[2]

    df = pd.read_csv(sys.argv[3], sep='\t', dtype={'Código': object})

    path =  sys.argv[4]
    fls = os.listdir(path)

    for i in df.index:
        recipient = df.loc[i, 'e-Mail']
        first_name = df.loc[i, 'Nome'].split()[0]
        print('Sending email to %s...' % recipient)
        if len(sys.argv) > 5:
            message = sys.argv[5]
        else:
            message = f'''Cara(o) {first_name},

            blablabla
            att,
            '''
        if len(sys.argv) > 6:
            subject = sys.argv[6]
        else:
            subject = 'Correção da Prova I - Bioestatística I - 20/09/2021'

        # hardcoded
        fl = '%s_corrigida.pdf' % df.loc[i, 'Código']

        if fl in fls:
            sendEmail(email, password, message, recipient,
                      subject, os.path.join(path, fl))
        else:
            #raise ValueError('File %s not Found' % fl)
            print('File %s not Found' % fl)

