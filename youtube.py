from googleapiclient.discovery import build
import os

api_key = os.getenv('youtube_key')
youtube = build('youtube', 'v3', developerKey=api_key)

def search_videos(query, max_results=5):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results
    )
    return request.execute()

def get_video_details(video_id):
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    )
    return request.execute()

# search_response = search_videos("Python programming",1)

# for item in search_response['items']:
#     video_id = item['id']['videoId']
#     video_details = get_video_details(video_id)
#     video = video_details['items'][0]
#     print(f"Title: {video['snippet']['title']}")
#     print(f"Description: {video['snippet']['description']}")
#     print(f"Views: {video['statistics']['viewCount']}")
#     print(f"Likes: {video['statistics']['likeCount']}")
#     # print(f"Dislikes: {video['statistics']['dislikeCount']}")
#     print(f"URL: https://www.youtube.com/watch?v={video_id}")
#     print("-" * 50)

def youtube_search(query,num = 1):
    search_res = search_videos(query,num)
    # res_url_list = []
    # for item in search_res['items']:
    #     video_id = item['id']['videoId']
    #     res_url =  f"https://www.youtube.com/watch?v={video_id}"
    #     res_url_list.append(res_url)
    # return res_url_list[num-1]
    video_id = search_res['items'][num-1]['id']['videoId']
    res_url =  f"https://www.youtube.com/watch?v={video_id}"
    return res_url

if __name__ == '__main__':
    query = input('搜尋:')
    num = int(input('第幾筆:'))
    print(youtube_search(query,num))