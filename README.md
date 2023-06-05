# Tmall-Seckill

[![License](https://img.shields.io/badge/License-Apache%202.0-339966.svg)](https://www.apache.org/licenses/LICENSE-2.0.html)

通过淘宝天猫下单API，在极短的时间里完成商品订单提交，实现秒杀抢购

![vn5um](http://img.miilnvo.com/vn5um.jpg)

<br/>

### 技术栈

Python 3.7.7

Selenium 4.9.1

ChromeDriver（WebDriver） 114.0.5735.90

<br/>

### 实现步骤

1. 利用Selenium和WebDriver模拟用户登陆，登陆后获取Cookies，之后的请求都需要加上这些Cookies

2. 下单流程：商品详情页面 ===立即购买===> 订单确认页面 ===提交订单===> 支付页面，所以要依次发起两个请求来模拟点击"立即购买"和"提交订单"按钮

3. "立即购买"按钮对应的API：`https://buy.tmall.com/order/confirm_order.htm`，具体的请求参数可以在商品详情页面和Cookies中找到

3. "提交订单"按钮对应的API：`https://buy.tmall.com/auction/confirm_order.htm`，具体的请求参数可以在订单确认页面和Cookies中找到

<br/>

### 开发细节

* 为WebDriver添加`--disable-blink-features=AutomationControlled`参数可以避免登陆时出现滑块验证码

* 本地时间最好与服务器的时间保持同步，淘宝时间服务器API：`http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp`

* 如果两次请求的时间间隔太短，那么在多次请求后，请求订单确认页面会被风控拦截，此时切换到页面上点击"立即购买"按钮会出现滑块验证码

<br/>

### 其他

目前仅支持天猫商品，不支持淘宝商品。为了避免侵权，暂时不提供完整代码。有任何问题、建议、想法，都可以通过`issues`或者`miilnvo@qq.com`进行联系

<br/>
