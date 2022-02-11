import gspread
import requests
import tqdm

from oauth2client.service_account import ServiceAccountCredentials

scopes = ["https://spreadsheets.google.com/feeds",
          "https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scopes)
client = gspread.authorize(creds)

sheet = client.open('YouTubeData_Updated_n=163').sheet1

urls = sheet.col_values(3)[1:]
unaccessible_urls = []

# user progressbar to print the progress
for url in tqdm.tqdm(urls):
    response = requests.get(url)
    if response.status_code != 200:
        unaccessible_urls.append(url)

print(unaccessible_urls)
