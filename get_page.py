import requests
from lxml import html


def get_page_info(link):
    page = requests.get(link)
    image, title = False, False
    if page.status_code == 200:
        tree = html.fromstring(page.content)
        favicons = tree.xpath('//link[@rel="icon" or @rel="shortcut icon"]/@href')
        titles = tree.xpath('//title/text()')
        if favicons:
            image = favicons[0]
        if titles:
            title = titles[0]
    return image, title
