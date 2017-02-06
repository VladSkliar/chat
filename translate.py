from apiclient.discovery import build

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

