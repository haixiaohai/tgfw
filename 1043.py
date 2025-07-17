import requests
import urllib3
urllib3.disable_warnings()
from time import sleep
from datetime import datetime

import requests
import json

header = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.9",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Content-Length": "279",
"Content-Type": "application/x-www-form-urlencoded",
"Cookie": "cookie_username=admin; cookie_password=Ngfw123; save_cookie=1; cookie_is_mobile=1",
"Host": "10.113.52.252",
"Origin": "http://10.113.52.252",
"Referer": "http://10.113.52.252/",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}
count = 1
date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def down(power_no: int):
    global count
    global date
    from_data = {
            "save_handcontrol_btn": "td2_" + str(power_no),
            "radio_function": "1",
            "socket_check"+str(power_no): "0",
            "aircond_type": "0",
            "aircond_model": "0",
            "aircond_temperature": "24",
            "aircond_action": "1",
            "radio_function_1": "0",
            "radio_function_2": "0",
            "radio_function_3": "0",
            "radio_function_4": "0",
            "radio_function_5": "0",
            "radio_function_6": "0",
            "radio_function_7": "0",
            "radio_function_8": "0",
            "is_mobile": "1"}
    try:
        r1 = requests.post(url="http://10.113.52.252/", data=from_data,
                           headers=header)  # json.dumps(from_data)  , cookies=cookie, verify=False
    except requests.RequestException as e:
        print(date, count, "成功下电")
        # sleep(900)
def up(power_no: int):
    global count
    global date
    from_data = {
            "save_handcontrol_btn": "td2_" + str(power_no),
            "radio_function": "0",
            "socket_check"+str(power_no): "0",
            "aircond_type": "0",
            "aircond_model": "0",
            "aircond_temperature": "24",
            "aircond_action": "1",
            "radio_function_1": "0",
            "radio_function_2": "0",
            "radio_function_3": "0",
            "radio_function_4": "0",
            "radio_function_5": "0",
            "radio_function_6": "0",
            "radio_function_7": "0",
            "radio_function_8": "0",
            "is_mobile": "1"}
    try:
        r1 = requests.post(url="http://10.113.52.252/", data=from_data,
                               headers=header)  # json.dumps(from_data)  , cookies=cookie, verify=False
    except requests.RequestException as e:
        print(date, count, "成功上电")
        # sleep(180)

def request():
    response = None
    global count
    global date
    try:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        response = requests.request("GET", "https://10.113.55.142", verify=False)
        if response.status_code == 200:
            print(date, count, "成功访问")
            sleep(60)
        else:
            print(date, count, "异常，访问不成功，状态码为", response.status_code)
    except Exception as e:
        print(date, '错误', response, e)
        sleep(10)


if __name__ == '__main__':
    while count < 11:
        down(2)
        # request()
        sleep(600)
        up(2)
        sleep(600)
        count += 1

