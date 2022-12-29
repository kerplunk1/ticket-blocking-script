import re
import quopri
import os
import time
import subprocess


path_mfile = '~/.mozilla/seamonkey/sqafjadz.default/Mail/Local Folders-1/1'
open(path_mfile, 'w').close()
print('Processing...')

try:
    while True:
        if os.stat(path_mfile).st_size > 0:
            start_time = time.time()
            with open(path_mfile, 'r+') as mfile:
                context = mfile.read()
                mfile.truncate(0)
            decoded = quopri.decodestring(context).decode('utf-8', 'ignore')
            url = re.findall(r'https:\/\/helpdesk.bystrobank.ru\/otrs\/index.pl\?Action=AgentZoom&TicketID=\d+&ZoomExpand=1', decoded)
            subprocess.call(['firefox-bin', url[0]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            finish_time = time.time()
            print(finish_time - start_time)
        time.sleep(0.7)
except KeyboardInterrupt:
    print('\nExit')
    exit()
