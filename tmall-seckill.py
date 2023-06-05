import datetime
import time
import requests
import re
import json
import urllib
import urllib.parse

from selenium import webdriver
from selenium.common import NoSuchFrameException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
from enum import Enum
from datetime import datetime

options = webdriver.ChromeOptions()  # 连接Chrome浏览器
options.add_argument("--disable-blink-features=AutomationControlled")  # 避免简单滑块验证码失效
driver = webdriver.Chrome(options=options)
session = requests.Session()
confirm_order_url_prefix = "https://buy.tmall.com/order/confirm_order.htm"
auction_order_url_prefix = "https://buy.tmall.com/auction/confirm_order.htm"


# 抢购状态
class Status(Enum):
    SUCCESS = 1
    FAIL = 2
    PROCEED = 3


# 简单滑块验证码
def verification():
    try:
        driver.switch_to.frame("")

        punish_button = driver.find_element(By.XPATH, "")

        if punish_button.get_attribute("id") == "":
            print("出现滑块验证码")
            punish_area = driver.find_element(By.XPATH, "")
            ActionChains(driver).drag_and_drop_by_offset(punish_button, punish_area.size["width"],
                                                         punish_area.size["height"]).perform()
            print("滑块验证码已通过")
            driver.switch_to.default_content()

    except NoSuchFrameException:
        pass


# 登陆认证
def login(account, password):
    driver.get("https://login.taobao.com/member/login.jhtml")

    account_input = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "")))
    account_input.send_keys(account)

    password_input = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "")))
    password_input.send_keys(password)

    login_button = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, "")))

    login_button.click()

    if WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, ""))).get_attribute("") == "":
        print("登陆成功")

        # 填充所有Cookie
        cookies = driver.get_cookies()
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"])

        # 填充部分请求头
        session.headers.clear()
        session.headers.setdefault("Accept", "")
        session.headers.setdefault("Accept-Encoding", "")
        session.headers.setdefault("Accept-Language", "")
        session.headers.setdefault("Content-Type", "")
        session.headers.setdefault("User-Agent", "")

        time.sleep(2)

    else:
        print("登陆失败")
        return


# URL参数解析
def extract_url_param(url):
    params = re.findall(r"(\w+)=(\w+)", url)
    return dict(params)


# 自动抢购
def auto_buy(detail_url, buy_time_str):

    # 1.打开商品页面
    driver.get(detail_url)

    time.sleep(2)

    buy_status = Status.FAIL
    confirm_retry_num = 1
    auction_retry_num = 1

    while buy_status != Status.SUCCESS or buy_status == Status.PROCEED:

        start_time = datetime.now()
        buy_time = datetime.strptime(buy_time_str, "%Y-%m-%d %H:%M:%S")

        if start_time < buy_time:
            print("活动尚未开始", start_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
            interval_time = (buy_time - start_time).seconds
            if interval_time > 5:
                print("等待{}秒后再抢购".format(interval_time))
                time.sleep(interval_time - 5)
            continue

        print("开始抢购", start_time.strftime("%Y-%m-%d %H:%M:%S.%f"))

        # 2.订单确认
        confirm_order_url = ""
        confirm_order_request_body = {}

        confirm_order_response = session.post(confirm_order_url, data=confirm_order_request_body)

        confirm_time = datetime.now()
        confirm_order_response_body = confirm_order_response.text
        soup = BeautifulSoup(confirm_order_response_body, "")

        if "" in soup.title.text:
            print("确认订单成功", confirm_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
        else:
            if confirm_retry_num <= 3:
                print("确认订单失败, 进行第{}次重试".format(confirm_retry_num), confirm_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
                confirm_retry_num = confirm_retry_num + 1
                buy_status = Status.PROCEED
                continue
            else:
                print("确认订单失败, 超过重试次数", confirm_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
                print(soup.get_text)
                break

        # 3.订单提交
        order_data_json = json.loads("")
        data = order_data_json.get("")

        if data.get("") is None:
            invalid_title = data.get("")
            print("无法提交订单:", invalid_title)
            break

        auction_order_url = ""
        auction_order_request_body = {}

        # 避免下单太快被检测拦截
        # time.sleep(0.6)

        auction_order_response = session.post(auction_order_url, data=auction_order_request_body)

        end_time = datetime.now()
        auction_order_response_body = auction_order_response.text
        soup = BeautifulSoup(auction_order_response_body, "")

        if "" in soup.p.text:
            buy_status = Status.SUCCESS
            print("提交订单成功", end_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
        else:
            if auction_retry_num <= 3:
                print("提交订单失败, 进行第{}次重试".format(auction_retry_num), end_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
                auction_retry_num = auction_retry_num + 1
                buy_status = Status.PROCEED
                continue
            else:
                print("提交订单失败, 超过重试次数", end_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
                print(soup.get_text)
                break

        print("耗时: {}秒".format(round((end_time - start_time).total_seconds(), 3)))

    input("抢购结束! 按Enter键退出...")


def main():
    print("Hi! 欢迎使用Tmall-Seckill (仅用于技术学习和交流)")
    account = input("请输入登陆账号: ")
    password = input("请输入登陆密码: ")
    start_time = input("请输入抢购时间: ")
    buy_url = input("请输入抢购地址: ")

    print("抢购开始!")

    login(account, password)
    auto_buy(buy_url, start_time)


if __name__ == "__main__":
    main()
