import asyncio
import json
import re
import time

import aiohttp
import random
import os
from urllib.parse import urlparse

from chrome_driver import ChromeDriver
from user_agents import random_agent
from lxml import etree
import urllib.parse

proxy="http://127.0.0.1:7890"

def cookie():
    bs = ''
    for i in range(32):
        bs += chr(random.randint(97, 122))

    cookie = {
        'platform': 'pc',
        'ss': '367701188698225489',
        'bs': bs,
        'RNLBSERVERID': 'ded6699',
        'FastPopSessionRequestNumber': '1',
        'FPSRN': '1',
        'performance_timing': 'home',
        'RNKEY': '40859743*68067497:1190152786:3363277230:1'
    }
    return cookie

async def fetch(session, url):
    async with session.get(url, proxy=proxy) as response:
        return await response.text()

async def fetch_key(session, url):
    content = await fetch(session, url)
    tree = etree.HTML(content, base_url=url)

    divs = tree.xpath('//div[@class="phimage"]')
    for div in divs:
        context = etree.tounicode(div)
        viewkey = re.findall('viewkey=(.*?)"', context)

        # loop = asyncio.get_event_loop()
        # loop.create_task(fetch_info(session, 'https://www.pornhub.com/embed/%s' % viewkey[0]))
        await fetch_info(session, 'https://www.pornhub.com/embed/%s' % viewkey[0])


    url_next = tree.xpath('//a[@class="orangeButton" and text()="Next "]/@href')
    if len(url_next) > 0:
        return urllib.parse.urljoin(url, url_next[0])


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

async def fetch_info(session, url):
    driver = ChromeDriver()
    await driver.process(url)

    video_xpath = '//*[@id="player"]/script[1]'
    show = EC.presence_of_element_located((By.XPATH, video_xpath))
    driver.wait.until(show)

    video_url = driver.driver.execute_script("return quality_1080p;")

    # html = driver.driver.page_source
    # info = re.findall('var flashvars_\d+ =(.*?)', html)
    # info_json = json.loads(info[0])
    #
    # duration = info_json.get('video_duration')
    # title = info_json.get('video_title')
    # image_url = info_json.get('image_url')
    # link_url = info_json.get('link_url')
    # quality_480p = info_json.get('quality_480p')

    parse_result = urlparse(video_url)
    file_path = parse_result.path
    await download_file(session, video_url, "./tmp/" + file_path)

async def download_file(session, url, file_path):
    async with session.get(url, proxy=proxy, timeout=None) as r:
        path = os.path.dirname(file_path)
        os.makedirs(path, exist_ok=True)
        with open(file_path, 'wb') as file:
            start = time.time()
            total_size = 0
            while True:
                chunk = await r.content.read(8192)
                if not chunk:
                    break
                total_size += len(chunk)
                diff = time.time() - start
                if diff % 10 == 0:
                    print(f'{diff:0.2f}s, downloaded: {total_size / (1024 * 1024):0.2f}MB')
                file.write(chunk)

async def main():
    headers = {"User-Agent":random_agent()}
    connector = aiohttp.TCPConnector(verify_ssl=False)  # 防止ssl报错
    async with aiohttp.ClientSession(cookies=cookie(),
                                     headers=headers,
                                     connector=connector) as session:
        next_url = 'https://www.pornhub.com'
        while not (next_url is None):
            next_url = await fetch_key(session, next_url)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())