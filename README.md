# VideoStatistics
Retrieve YouTube video statistics using YouTube API

In line ```client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"``` change the json file name to your own client secret file


### Script Example
```python3 query.py "your query" --max_result MAX_RESULT```

```query``` describes the video that you want to search

```--max_result``` defines the maximum number of videos you want to display. The range is from 1 to 50, inclusive. This is limited by the YouTube API.
