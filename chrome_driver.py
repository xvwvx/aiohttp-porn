
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ChromeDriver(object):
    def __init__(self, user_agent=None,
                 proxy=None,
                 binary_locaion=None):

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        if not (user_agent is None):
            options.add_argument("user-agent=%s" % user_agent)

        if not (user_agent is None):
            options.add_argument('--proxy=%s' % proxy)

        if not (binary_locaion is None):
            options.binary_locaion = binary_locaion

        self.driver = webdriver.Chrome(chrome_options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def __del__(self):
        self.driver.close()

    async def process(self, url, cookies=None, headers=None):
        self.driver.get(url=url)

        if not (cookies is None):
            # 删除原来的cookie
            self.driver.delete_all_cookies()
            # 必须先加载网站，才能设置cookie
            for key, value in cookies.items():
                self.driver.add_cookie({'name': key, 'value': value})

            self.driver.get(url=url)

