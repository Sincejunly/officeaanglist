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
parser.add_argument('-t', '--trust', type=str, help='Trust the domain')

parser.add_argument('-i', '--init',action='store_true')

args = parser.parse_args()
DOMAIN = None
PASSWORD = None
USERNAME = None
TDOMAIN = None
init = args.init
pydith = os.path.dirname(os.path.realpath(__file__))
if args.domain:
    DOMAIN = args.domain
if args.password:
    PASSWORD = args.password
if args.user:
    USERNAME = args.user

users = PASSWORD or USERNAME

# if not DOMAIN and not usr:
#     parser.print_help()
#     exit(0)

if DOMAIN:
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
    while True:
        try:
            origin = await readjson(os.path.join(pydith, './viewer/data.json'))
            pool = await AsyncMysqlPool.initialize_pool(
                minsize=1,
                maxsize=2,
                echo=True,
                pool_recycle=1800,
                host=origin['mysqlHost'], 
                port=int(origin['mysqlPort']), 
                user=origin['mysqlUser'], 
                password=origin['mysqlPassword'], 
                db=origin['mysqlDataBase'])
            

            
            if users:
                user = await pool.get_row_by_value('x_users', 'username', 'admin')
                if init:
                    
                    user['username'] = USERNAME
                    user['password'] = PASSWORD
                    await pool.update('x_users', user, True)
                else:
                    userd = await readjson(os.path.join(pydith, './viewer/pd'))
                    user['password'] = userd['password']
                    await pool.update('x_users', user, True)
                    user['password'] = userd['hashed_password']
                    user.pop('base_path')
                    await pool.update('x_user', user, True)

                
            if DOMAIN:
                await pool.update('x_domain', {'id':1, 'Domain':DOMAIN, 'type': 'believe'}, True)
                await pool.update(table, userData, True)
            if TDOMAIN:
                do = await pool.get_row_by_value('x_domain', 'Domain', DOMAIN)
                if do != None:
                    do['type'] = 'believe'
                    await pool.update('x_domain', do, True)
                else:
                    await pool.update('x_domain', {'Domain': DOMAIN, 'type':'believe'})
                    
            break
        except Exception as e:
            await asyncio.sleep(5)
            print('init: '+str(e))

   

asyncio.run(main())