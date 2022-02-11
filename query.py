# -*- coding: utf-8 -*-
# Sample Python code for youtube.search.list

import os
import json
import argparse

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import gspread
from oauth2client.service_account import ServiceAccountCredentials

youtube_scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
gspread_scopes = ["https://spreadsheets.google.com/feeds",
                  "https://www.googleapis.com/auth/spreadsheets",
                  "https://www.googleapis.com/auth/drive.file",
                  "https://www.googleapis.com/auth/drive"]

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "oauth_client_creds.json"

url_prefix = 'https://www.youtube.com/watch?v='
max_result_limit = 50   # YouTube API limit its maxResults (result for each page) to be 50


def get_video_ids(youtube, query, num_videos, page_token=None):
    if num_videos > 50:
        max_results = 50
    else:
        max_results = num_videos
    num_videos -= max_results

    # search for the video ids given a query
    if not page_token:
        request = youtube.search().list(
            part="id",
            q=query,
            maxResults=max_results
        )
    else:
        request = youtube.search().list(
            part="id",
            q=query,
            maxResults=max_results,
            pageToken=page_token
        )

    response = None
    try:
        response = request.execute()
    except Exception as e:
        print(e)

    video_ids = [d['id']['videoId'] if 'videoId' in d['id'] else '' for d in response['items']]
    video_ids = ','.join(video_ids)

    return video_ids, num_videos, response['nextPageToken']
    

def main():
    parser = argparse.ArgumentParser(description='search for YouTube videos and return their information')
    parser.add_argument('query', type=str, help='a query describing the videos you want to search')
    parser.add_argument('--num_videos', type=int, default=5, help='number of videos to be displayed')
    args = parser.parse_args()

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, youtube_scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    query = args.query
    num_videos = args.num_videos
    video_ids = []

    # get required number of video ids
    page_token = None
    while num_videos > 0:
        new_video_ids, num_videos, page_token = get_video_ids(youtube, query, num_videos, page_token)
        video_ids.append(new_video_ids)

    search_result = []
    json_responses = []
    for id_seq in video_ids:
        # retrieve video statistics given ids
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=id_seq
        )

        response = request.execute()
        json_responses.append(response)
        cur_result = [[
            url_prefix + item['id'],
            item['snippet']['title'],
            item['snippet']['publishedAt'],
            item['snippet']['description'],
            item['contentDetails']['duration'],
            item['statistics']['viewCount'] if 'viewCount' in item['statistics'] else '0',
            item['statistics']['likeCount'] if 'likeCount' in item['statistics'] else '0',
            item['statistics']['favoriteCount'] if 'favoriteCount' in item['statistics'] else '0',
            item['statistics']['commentCount'] if 'commentCount' in item['statistics'] else '0'
        ] for item in response['items']]

        search_result += cur_result

    # write result to json file
    with open('query_result.json', 'w') as output:
        json.dump(json_responses, output, indent=4)

    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', gspread_scopes)
    client = gspread.authorize(creds)
    spread_sheet = client.open('YouTube Video Metrics')
    work_sheet = spread_sheet.sheet1
    sheet_name = work_sheet.title

    # create a new work sheet if the first sheet is not empty
    if len(work_sheet.get_values()) != 0:
        sheet_name = 'Sheet%d' % (len(spread_sheet.worksheets()) + 1)
        print('Created new work sheet: %s' % sheet_name)
        work_sheet = spread_sheet.add_worksheet(sheet_name, 1000, 10)

    # write to the work sheet
    work_sheet.append_row(['Video URL', 'Title', 'Publish Time', 'Description', 'Duration', 'View Count', 'Like Count', 'Favorite Count', 'Comment Count'])
    work_sheet.append_rows(search_result, insert_data_option='OVERWRITE')
    print('The result is written to %s' % sheet_name)


if __name__ == "__main__":
    main()
