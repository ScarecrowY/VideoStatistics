# -*- coding: utf-8 -*-
# Sample Python code for youtube.search.list

import os
import json
import argparse

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
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
    
    try:
        response = request.execute()
    except Exception as e:
        print(e)

    video_ids = [d['id']['videoId'] for d in response['items']]
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

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "oauth_client_creds.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
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
    for id_seq in video_ids:
        # retrieve video statistics given ids
        request = youtube.videos().list(
            part='snippet,statistics',
            id=id_seq
        )

        response = request.execute()
        cur_result = [{
            'id': d['id'],
            'title': d['snippet']['title'],
            'description': d['snippet']['description'],
            'statistics': d['statistics']
        } for d in response['items']]

        search_result += cur_result

    with open('query_result.json', 'w') as output:
        json.dump(search_result, output, indent=4)


if __name__ == "__main__":
    main()
