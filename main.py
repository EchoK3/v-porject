import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import html5lib


# 定义网站地址
website_url = input("请输入网站域名：")

# 在当前目录下创建名为 "web" 的目录
web_directory = input("请输入保存文件名：")

os.makedirs(web_directory, exist_ok=True)

# 设置 "web" 目录为基础目录
base_directory = os.path.join(os.getcwd(), web_directory)

# 发起GET请求获取网页源代码
response = requests.get(website_url, verify=False)
html = response.text

# 解析HTML内容
soup = BeautifulSoup(html, 'html.parser')

# 去掉链接中的问号后面部分
def remove_query_params(link):
    parsed = urlparse(link)
    cleaned = parsed._replace(query='')
    return urlunparse(cleaned)

# 列出所有的CSS链接
css_links = []
for css_link in soup.find_all('link', {'rel': 'stylesheet'}):
    href = css_link['href']
    if href.strip():  # 如果 href 不为空
        # print("test:", href)
        full_css_link = urljoin(website_url, href)
        css_links.append(remove_query_params(full_css_link))

# 列出所有的JS链接
js_links = []
for js_script in soup.find_all('script', src=True):
    src = js_script['src']
    if src.strip():  # 如果 src 不为空
        full_js_link = urljoin(website_url, src)
        js_links.append(remove_query_params(full_js_link))

# 列出所有的图片链接，线先定义图片文件扩展名列表
valid_image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
# 列出所有的图片链接
img_links = []
for img_tag in soup.find_all('img', src=True):
    src = img_tag['src']
    if src.strip():  # 如果 src 不为空
        full_img_link = urljoin(website_url, src)
        img_link = remove_query_params(full_img_link)

    # 获取链接的文件扩展名（后缀）
    img_extension = os.path.splitext(img_link)[1].lower()

    # 判断是否为合法图片链接
    if img_extension in valid_image_extensions:
        img_links.append(img_link)


# 以下函数部分
def create_directories_from_path(base_directory, path):
    # 去掉开头和结尾的斜杠
    directory_path_string = path.strip("/")
    # 拆分目录名称
    directory_names = directory_path_string.split("/")
    # 当前目录
    current_directory = base_directory
    # 创建目录
    for directory_name in directory_names:
        current_directory = os.path.join(current_directory, directory_name)
        os.makedirs(current_directory, exist_ok=True)
    return current_directory


def download_and_save_file(url, base_directory):
    parsed_url = urlparse(url)
    file_path = parsed_url.path
    file_directory = os.path.dirname(file_path)
    file_directory_path = create_directories_from_path(base_directory, file_directory)

    response = requests.get(url)
    file_name = os.path.basename(file_path)
    file_path = os.path.join(file_directory_path, file_name)

    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path

# 打印结果
print("CSS链接:")
for css_link in css_links:
    print('准备下载CSS:', css_link)
    css_file_path = download_and_save_file(css_link, base_directory)
    print('CSS 文件已下载到:', css_file_path)

print("\nJS链接:")
for js_link in js_links:
    print('准备下载JS:', js_link)
    js_file_path = download_and_save_file(js_link, base_directory)
    print('JS 文件已下载到:', js_file_path)

print("\n图片链接:")
for img_link in img_links:
    print('准备下载图片:', img_link)
    img_file_path = download_and_save_file(img_link, base_directory)
    print('图片已下载到:', img_file_path)

# 保存网页源码为 index.html
index_file_path = os.path.join(base_directory, 'index.html')
with open(index_file_path, 'w', encoding='utf-8') as index_file:
    # index_file.write(html)
    index_file.write(soup.prettify())
    print(html5lib.parse(html))

print("网页源码已保存为:", index_file_path)