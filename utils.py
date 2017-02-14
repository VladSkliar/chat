from apiclient.discovery import build
from lxml import html
from models import User
import requests

languages = ["af", "sq", "ar", "be", "bg", "ca", "zh-CN", "zh-TW", "hr",
             "cs", "da", "nl", "en", "et", "tl", "fi", "fr", "gl", "de",
             "el", "iw", "hi", "hu", "is", "id", "ga", "it", "ja", "ko",
             "lv", "lt", "mk", "ms", "mt", "no", "fa", "pl", "pt", "ro",
             "ru", "sr", "sk", "sl", "es", "sw", "sv", "th", "tr", "uk",
             "vi", "cy", "yi"]


def translate(text, language):
    service = build('translate', 'v2', developerKey="AIzaSyDG6Qe-2DCfGSPkk-PwXsLh9i611wqhGiM")
    if language in languages:
        request = service.translations().list(q=text, target=language)
        response = request.execute()
        return response['translations'][0]['translatedText']
    else:
        return 'This languages is not avalible'


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


def generate_roomname(username1, username2):
    user1 = User.get(User.username == username1)
    user2 = User.get(User.username == username2)
    list_id = [user1.id, user2.id]
    list_id.sort()
    roomname = '&'.join([str(x) for x in list_id])
    return roomname
