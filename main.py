import argparse
from os import path
import psutil
import requests
import re
from datetime import datetime, timedelta
import os
import time
import subprocess
from regex import regex
import urllib3

urllib3.disable_warnings()

def get_unica_cookie():
    client = requests.session()
    x = client.get("https://id.unica.vn", verify=False).text
    token = regex.findall('input type="hidden" name="_token" value="(.*?)" autocomplete="off"', x)
    headers = {'accept': 'application/json',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
               'cookie': "XSRF-TOKEN=" + client.cookies['XSRF-TOKEN'] + "; id_unica_session=" + client.cookies[
                   'id_unica_session'],
               'x-xsrf-token': client.cookies['XSRF-TOKEN'],
               'x-csrf-token': token[0],
               'email': 'hoctap.tranthanhbinh@gmail.com'}
    k = requests.post('https://id.unica.vn/login',
                      files={'_token': (None, str(token[0])), '_method': (None, "POST"), 'type': (None, '1'),
                             'email': (None, 'hoctap.tranthanhbinh@gmail.com'), 'password': (None, 'Tranthanhbinh1@'),
                             'remember_me': (None, 'on')}, verify=False, headers=headers)
    rooturl = k.json()["url"]
    cokkies = requests.get(rooturl, stream=True, allow_redirects=False).headers['Set-Cookie']
    uid = regex.findall("uid=(.*?);", str(cokkies))
    PHPSESSID = regex.findall("PHPSESSID=(.*?);", str(cokkies))
    user_id = regex.findall("user_id=(.*?);", str(cokkies))
    return "uid=" + uid[0] + "; PHPSESSID=" + PHPSESSID[0] + "; user_id=" + user_id[0]


parser = argparse.ArgumentParser(description="UNICA CHECKING")
parser.add_argument(
    "-file",
    dest="file",
    type=str,
    help="File list course",
)
parser.add_argument(
    "-dir",
    dest="dir",
    type=str,
    help="Dir course to check",
)
parser.add_argument(
    "-out",
    dest="out",
    type=str,
    help="Output file write",
)
args = parser.parse_args()
API_KEY_TELE = '6416805129:AAFa4ttGiws3Q2txFHTYy9bSj5aquh5D7fI'

def check_disk():
    return psutil.disk_usage("C:/").free / (1024.0 ** 3) < 0.5

def send_message(id):
    data = {"chat_id": "5727411972",
            "text": f'Có vẻ như ổ đĩa sắp đầy. Hãy exit Mountain Duck, chờ 3s rồi bật lại.\nID đã đi được đến: {id}'
            }
    requests.post(f"https://api.telegram.org/bot{API_KEY_TELE}/sendMessage", json=data)

def get_duration(filename):
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", filename],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        return float(result.stdout)
    except:
        return 0


def compare(date1, date2):
    if date1 < date2:
        date1 += timedelta(seconds=1)
    elif date1 > date2:
        date2 += timedelta(seconds=1)
    return date1 == date2


def rename_file(s):
    k = str(s).replace("\\", '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"',
                                                                                                             '').replace(
        '<',
        '').replace(
        '>', '').replace('|', '').replace('\t', ' ').strip()
    k = k.replace("Bài 1 ", "Bài 01 ").replace("Bài 2 ", "Bài 02 ").replace("Bài 3 ", "Bài 03 ").replace("Bài 4 ",
                                                                                                         "Bài 04 ").replace(
        "Bài 5 ", "Bài 05 ").replace("Bài 6 ", "Bài 06 ").replace("Bài 7 ", "Bài 07 ").replace("Bài 8 ",
                                                                                               "Bài 08 ").replace(
        "Bài 9 ",
        "Bài 09 ")
    while str(k).find('  ') != -1:
        k = str(k).replace('  ', ' ')
    return k


def scan(id, dir_root):
    header = {'Cookie': get_unica_cookie(),
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
              'Referer': 'https://unica.vn/'
              }
    print(id)
    x = requests.get(f"https://unica.vn/learn/{id}/overview?group=2", headers=header).text
    list_time = re.findall('<div class="time">(.*?)</div>', x)
    video_line = re.findall('class="btn btn-default" href="(.*?)">.*?</a>', x, re.DOTALL)
    x = requests.get("https://unica.vn" + str(video_line[0]), headers=header).text
    name_course = rename_file(str(re.findall('<div class="mln-name-course">.*?<p>(.*?)</p>.*?</div>', x, re.DOTALL)[0]))
    date_format = "%H:%M:%S"
    list_time_compare = []
    for i in range(0, int(len(list_time) / 2)):
        if len(list_time[i]) == 0:
            date_obj = datetime.strptime("00:00:00", date_format)
        else:
            date_obj = datetime.strptime(str(list_time[i]).replace(" ", ""), date_format)
        list_time_compare.append(date_obj)
    if len(list_time_compare) > 0:
        str_regex = 'Bài (.*?) '
        DIR_SCAN = dir_root + '/' + name_course + '/'
        res = []
        if not path.exists(DIR_SCAN):
            os.mkdir(DIR_SCAN)
        for file_path in os.listdir(DIR_SCAN):
            if os.path.isfile(os.path.join(DIR_SCAN, file_path)):
                res.append((int(re.findall(str_regex, file_path)[0]), file_path))
        list_error = []
        for i in range(0, len(list_time_compare)):
            chapter_index = i + 1
            isMiss = True
            isError = False
            if check_disk():
                send_message(id)
                while True:
                    time.sleep(1)
            for z in range(0, len(res)):
                if chapter_index == res[z][0]:
                    isMiss = False
                    file_name = DIR_SCAN + '/' + res[z][1]
                    if os.path.splitext(file_name)[1] == ".mp4":
                        if not compare(datetime.strptime(time.strftime(date_format, time.gmtime(get_duration(file_name))),
                                                         date_format), list_time_compare[i]):
                            list_error.append(chapter_index)
                    break
            if isMiss or isError:
                list_error.append(chapter_index)
        if len(list_error) > 0:
            with open(args.out, "a", encoding='utf-8') as f:
                f.write(id + "\n" + name_course + "\n")
                for i in list_error:
                    f.write(str(i) + " ")
                f.write("\n")

if not args.file:
    print('NOT HAVE FILE LIST COURSE')
elif not args.dir:
    print('NOT HAVE DIR COURSE TO CHECK')
elif not args.out:
    print('NOT HAVE FILE OUTPUT')
else:
    lines = open(args.file, "r", encoding='utf-8').readlines()
    for i in range(0, len(lines), 3):
        scan(str(int(lines[i])), args.dir)
