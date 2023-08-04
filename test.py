import re

def extract_part_from_url(url, position=0):
    # Regular expression pattern to find the desired part
    pattern = r'([^/]+)'

    # Extract all parts separated by "/"
    parts = re.findall(pattern, url)

    # Return the part at the specified position (default: 0)
    return parts[position]

# Example URL
url = "https://office.homura.top:82/cache/files/new.docx3Fsign3Did_7188/output.docx/output.docx?md5=bSncuDb8dptNoXggcJ9ygQ&expires=1691038933&filename=output.docx"

import time
from datetime import datetime

# 获取当前时间的秒级时间戳
seconds_timestamp = int(time.time())

# 将秒级时间戳转换为标准日期时间格式
date_time_str = datetime.fromtimestamp(seconds_timestamp).strftime('%Y-%m-%d %H:%M:%S')
print(date_time_str)