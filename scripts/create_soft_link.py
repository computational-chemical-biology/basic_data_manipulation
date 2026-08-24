import socket
import os

computer_name = socket.gethostname()
usrs = os.listdir('/home')

for u in usrs:
    if not os.path.exists(f"/var/locally-mounted/{computer_name}/{u}"):
        print('Creating for user', u)
        os.makedirs(f"/var/locally-mounted/{computer_name}/{u}")
        os.system(f'ln -s /var/locally-mounted/{computer_name}/{u} /home/{u}/{u}_nfs')
    else:
        print('Dir already created for user', u)
