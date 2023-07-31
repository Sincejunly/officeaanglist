import os
import mysql.connector

import asyncio
from database_utils import readjson



import argparse

from database_utils import AsyncMysqlPool

parser = argparse.ArgumentParser(description='Script description', add_help=True)

parser.add_argument('-u', '--user', type=str, help='Specify the domain')
parser.add_argument('-d', '--domain', type=str, help='Specify the domain')
parser.add_argument('-p', '--password', type=str, help='Specify the password')


args = parser.parse_args()
DOMAIN = None
PASSWORD = None
USERNAME = None
pydith = os.path.dirname(os.path.realpath(__file__))
if args.domain:
    DOMAIN = args.domain
if args.password:
    PASSWORD = args.password
if args.user:
    USERNAME = args.user

usr = PASSWORD or USERNAME

if not DOMAIN and not usr:
    parser.print_help()
    exit(0)

if usr:
    table = "x_user"
    userData = [
        ('`id`','username','password','type'),
        ('1', USERNAME, PASSWORD,'believe'),
    ]
else:
    table = 'x_setting_items'
    userData =[
        ('`key`', 'value'),
        ('aria2_secret', 'QQ9433841351'),
        ('iframe_previews', '''{{
            "doc,docx,xls,xlsx,ppt,pptx": {{
                "Microsoft":"https://view.officeapps.live.com/op/view.aspx?src=$e_url",
                "office":"{}/viewer?src=$e_url"
            }},
            "pdf": {{
                "PDF.js":"https://alist-org.github.io/pdf.js/web/viewer.html?file=$e_url"
            }},
            "epub": {{
                "EPUB.js":"https://alist-org.github.io/static/epub.js/viewer.html?url=$e_url"
            }}
    }}'''.format(DOMAIN)),
        ('aria2_uri','{}/aria2/jsonrpc'.format(DOMAIN)),
        ("announcement",'''### repo
https://github.com/alist-org/alist     
https://github.com/Sincejunly/officeaanglist''')
    ]


async def main():
    origin = await readjson('./viewer/data.json')
    #print(userData)
    pool = await AsyncMysqlPool.initialize_pool(
        minsize=1,
        maxsize=2,
        echo=True,
        pool_recycle=1800,
        host=origin['mysqlHost'], 
        port=origin['mysqlPort'], 
        user=origin['mysqlUser'], 
        password=origin['mysqlPassword'], 
        db=origin['mysqldataBase'])
    
    user = await pool.get_row_by_value('x_users', 'username', 'admin')
    user['password'] = 'admin'
    await pool.update('x_users', user, True)
    await pool.update(table, userData, True)

    do = await pool.get_row_by_value('x_domain', 'Domain', DOMAIN)

    if do != None:
        do['type'] = 'believe'
        await pool.update('x_domain', do, True)
    else:
        await pool.update('x_domain', {'Domain': DOMAIN, 'type':'believe'})


asyncio.run(main())