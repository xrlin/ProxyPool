#!/usr/bin/python3

import requests
import re
import threading


def get_page(url):
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
           return resp
        else:
            print('Request page {url} failed with status code {code}.'.format(url=url, code=resp.status_code))
    except Exception as e:
        print('Request page {url} failed with exception {e}}.'.format(url=url, e=e))


def extract_ips(text):
    """
    :param text:
    :return: iter fo Match Objects
    """
    pattern = re.compile(r'(?P<ip>([0-9]{1,3}).[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5})')
    return pattern.finditer(text)


# 封装http请求
def reqs(**kwargs):
    # 传递url，正则表达式，timeout，proxies
    url = kwargs.get('url', '')
    rex = kwargs.get('rex', '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}')
    timeout = kwargs.get('timeout', 10)
    proxies = kwargs.get('proxies', {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    })
    headers = { 'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)' }
    try:
        r = requests.get(url, headers = headers, proxies = proxies, timeout = timeout)
        if r.status_code == 200:
            print('请求 %s 成功' % url)
            # 根据传入的正则返回需要的数据
            return re.findall(rex, r.text)
        else:
            print('%d %s' % (r.status_code, url))
    except Exception as e:
        print('请求 %s 异常 %s' % (url, e))
    return []



# 检查代理是否可用
def check_ip_ports(ip_ports, func):
    timeout = 5
    for ip_port in ip_ports:
        proxies = {
            'http': 'http://%s' % ip_port,
            'https': 'https://%s' % ip_port
        }
        ips = reqs(url='http://1212.ip138.com/ic.asp', rex='\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', proxies=proxies,
                   timeout=timeout)
        if len(ips) > 0 and ips[0] in ip_port:
            print('%s has checked' % ip_port)
            # 如果可用则调用回调函数
            func(ip_port)


# 将可用的代理保存到文件proxies.txt
def save_ip_ports(fname, ip_ports):
    with open(fname, 'w') as f:
        for i in ip_ports:
            f.write(i + '\n')


if __name__ ==  '__main__':
    url_template = 'http://www.66ip.cn/nmtq.php?getnum=&isp=0&anonymoustype=3&start{offset}=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip'

    ip_ports = []
    ip_ports_ok = []

    for i in range(1, 1000, 20):
        resp = get_page(url_template.format(offset=i))
        ip_ports += [ip.group('ip') for ip in extract_ips(resp.text)]

    # 把爬到的代理存到临时文件
    save_ip_ports('temp.txt', ip_ports)


    def checked(ip_port):
        ip_ports_ok.append(ip_port)

    all_threads = []
    # 每20个代理开一个线程，一般代理数量在几千到一万
    for i in range(0, len(ip_ports), 20):
        t = threading.Thread(target=check_ip_ports, args=(ip_ports[i: i + 20], checked))
        all_threads.append(t)
        t.start()

    for t in all_threads:
        t.join()

    # 保存可用的代理到proxies.txt
    save_ip_ports('proxies.txt', ip_ports_ok)

    print('All done : )')

