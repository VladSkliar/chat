from apiclient.discovery import build


def translate(text, language):
    service = build('translate', 'v2', developerKey="AIzaSyDG6Qe-2DCfGSPkk-PwXsLh9i611wqhGiM")
    request = service.translations().list(q=text, target=language)
    responce = request.execute()
    print responce
