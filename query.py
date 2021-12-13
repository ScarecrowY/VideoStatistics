# -*- coding: utf-8 -*-
# Sample Python code for youtube.search.list

import os
import json
import argparse

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def main():
    parser = argparse.ArgumentParser(description='search for YouTube videos and return their information')
    parser.add_argument('query', type=str, help='a query describing the videos you want to search')
    parser.add_argument('--max_result', type=int, default=5, help='maximum number of videos to be displayed from 1 to 50 inclusive')
    args = parser.parse_args()
    print(args.max_result)

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

    # search for the video ids given a query
    request = youtube.search().list(
        part="id",
        q=args.query,
        maxResults=args.max_result
    )

    response = request.execute()

    video_ids = [d['id']['videoId'] for d in response['items']]
    video_ids = ','.join(video_ids)
    print(video_ids)

    # retrieve video statistics given ids
    request = youtube.videos().list(
        part='snippet,statistics',
        id=video_ids
    )

    response = request.execute()
    search_result = [{
        'id': d['id'],
        'title': d['snippet']['title'],
        'description': d['snippet']['description'],
        'statistics': d['statistics']
    } for d in response['items']]

    with open('query_result.json', 'w') as output:
        json.dump(search_result, output, indent=4)


if __name__ == "__main__":
    main()
