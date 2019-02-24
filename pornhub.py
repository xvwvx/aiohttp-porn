import asyncio
import json
import re

import aiohttp
import random

from ChromeDriver import ChromeDriver
from user_agents import random_agent
from lxml import etree
import urllib.parse

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
    async with session.get(url,
                           proxy="http://127.0.0.1:1087") as response:

        return await response.text()

async def fetch_key(session, url):
    content = await fetch(session, url)
    tree = etree.HTML(content, base_url=url)

    divs = tree.xpath('//div[@class="phimage"]')
    for div in divs:
        context = etree.tounicode(div)
        viewkey = re.findall('viewkey=(.*?)"', context)

        loop = asyncio.get_event_loop()
        loop.create_task(fetch_info(session, 'https://www.pornhub.com/embed/%s' % viewkey[0]))


    url_next = tree.xpath('//a[@class="orangeButton" and text()="Next "]/@href')
    if len(url_next) > 0:
        return urllib.parse.urljoin(url, url_next[0])


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

async def fetch_info(session, url):
    driver = ChromeDriver()
    await driver.process(url)

    video_xpath = '//*[@id="player"]/div[21]/video/source'
    show = EC.presence_of_element_located((By.XPATH, video_xpath))
    driver.wait.until(show)
    video_url = driver.driver.find_element_by_xpath(video_xpath).get_attribute('src')

    html = driver.driver.page_source
    info = re.findall('var flashvars =(.*?),\n', html)
    info_json = json.loads(info[0])

    duration = info_json.get('video_duration')
    title = info_json.get('video_title')
    image_url = info_json.get('image_url')
    link_url = info_json.get('link_url')
    quality_480p = info_json.get('quality_480p')

    print(video_url)


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