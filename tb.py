from requests import Session
from requests_pkcs12 import Pkcs12Adapter
from bs4 import BeautifulSoup
import re
import time
from getpass import getpass
import subprocess

class bcolors:
    WARNING = '\033[93m'
    OK = '\033[92m'
    HEADER = '\033[95m'
    RED = '\033[91m'
    END = '\033[0m'

patterns = [
    'картридж|катридж|краск[а,у,и]|замяти',
    '(уменьшить|сжать|объедин|сохранить|разделить|извлечь|архив).*(файл|pdf|пдф|документ)',
    '(сброс|продл|смен|срок|забыл|созд).*(парол|ldap|лдап|логин)',
    'серт',
    'агент.*оформител',
    '.?жаб.?ер',
    'фото',
    'канц|хоз.?тов|бумаг[а,и]',
    'клавиатур|мыш[ь,к,и]|гарнитур|монитор|батарейк',
    '.?кон.?проф|\(эп\)|вод[а,ы,у]',
    'удал.*(талон|пко|проводк|ордер|номер|реестр)',
    '(обнов|установ).*(комит|ntpro|firefox|браузер|chrome|хром)',
    '(сши|подши).*(док|справ)',
    'доступ.*(реп[е,о,а]|бд|баз|про.?кт|ldap)',
    'смена фио',
    'запис.*(диск|информ)',
    'док.*(архив|сшив)',
    'баз.*знан',
    'антифрод'
]

url_main = "https://helpdesk.bystrobank.ru"
url_list = "https://helpdesk.bystrobank.ru/otrs/index.pl?Action=AgentTicketQueue"
url_block = 'https://helpdesk.bystrobank.ru/otrs/index.pl?Action=AgentTicketLock&Subaction=Lock&TicketID='
overlook = []

cert_pass = getpass(f'{bcolors.WARNING}Пароль от резервной копии сертификата: {bcolors.END}')
session = Session()
session.mount(url_main, Pkcs12Adapter(pkcs12_filename='my.p12', pkcs12_password=cert_pass))

try:
    while True:
        start_time = time.time()
        
        response = session.get(url_list, verify='to_helpdesk.pem')
        print(f'запрос в OTRS, статус: {bcolors.OK}{response.status_code}{bcolors.END}')
        page_otrs = response.text.replace("<!--start Record-->", "<article class='parsing'>").replace("<!--stop Record -->", "</article>")
        soup = BeautifulSoup(page_otrs, 'html.parser')
        html_ticket_list = soup.find_all('article', class_='parsing')
        for html_ticket in html_ticket_list:            
            td_tags_list = html_ticket.find_all('td')
            if td_tags_list[9].div['title'] == 'root@localhost':
                ticket_id = re.search('TicketID=\d+', html_ticket.a['href']).group().replace('TicketID=', '')
                for pattern in patterns:
                    if re.search(pattern, html_ticket.a['title'].lower()):
                        blocking_request = session.get(url_block + ticket_id)
                        print(f'{bcolors.HEADER}запрос на блокировку тикета, статус: {bcolors.OK}{blocking_request.status_code}{bcolors.END}')
                        break
                else:
                    if ticket_id not in overlook:
                        print(f'{bcolors.WARNING}Новый тикет, открытие в браузере{bcolors.END}')
                        appcommand = ['firefox-bin', url_main + html_ticket.a['href']]
                        subprocess.run(appcommand, capture_output=True)
                        overlook.append(ticket_id)
                        if len(overlook) > 15:
                            overlook.clear()
                            overlook.append(ticket_id)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'{bcolors.RED}Затраченное время, сек: {bcolors.OK}{round(elapsed_time, 4)}{bcolors.END}')
        time.sleep(1)

except KeyboardInterrupt:
    print(f'\n{bcolors.WARNING}Выход{bcolors.END}')

