import time
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from multiprocessing import Pool
from fake_useragent import UserAgent

proxies_arr = []

proxies = open('proxies.txt', 'r')
proxy = proxies.readline()
PROXY_HOST = f'{proxy.split(":")[0]}'.strip()  # rotating proxy or host
PROXY_PORT = int(f'{proxy.split(":")[1]}'.strip())  # port
PROXY_USER = 'vlemhmdm' # username
PROXY_PASS = '05kxhdvidoh4' # password

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""
background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
urls_list = []

wallets = open('wallets.txt', 'r')
while True:
    # считываем строку
    wallet = wallets.readline()
    url = f'https://debank.com/profile/{wallet.strip()}'
    urls_list.append(url)
    # прерываем цикл, если строка пустая
    if not wallet:
        break


# Creating driver with proxy and user agent
def get_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(pluginfile)

    if user_agent:
        ua = UserAgent()
        user_agent = ua.random
        chrome_options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=chrome_options)
    return driver


def get_ip(url):
    driver = get_chromedriver(use_proxy=True)
    driver.get(url=url)
    # To wait
    time.sleep(20)
    address = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/div[2]/span").text
    balance = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[2]/div[1]/div").text
    if '+0%' in balance:
        balance = balance.replace('+0%', '')
    # Printing the text by XPATH
    print('========================')
    print(address)
    print(balance.strip())


# Creating 5 threads
if __name__ == '__main__':
    p = Pool(processes=5)
    p.map(get_ip, urls_list)



