import os
import hashlib
import requests
import praw

# Reddit API credentials
CLIENT_ID = 'ID'
CLIENT_SECRET = 'SECRET'
USER_AGENT = 'AGENT'
# Initialize PRAW with credentials
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)

def hash_file_contents(file_contents):
    """Generate an MD5 hash for the given file contents."""
    hasher = hashlib.md5()
    hasher.update(file_contents)
    return hasher.hexdigest()

def download_media(url, directory, filename):
    """Download media from a URL to a directory with a given filename and return its contents."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(directory, filename)
        file_contents = bytearray()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
                file_contents.extend(chunk)
        return file_contents
    else:
        print(f"Failed to download {filename} from {url}")
        return None

def fetch_submissions(subreddit, post_type, limit, after):
    """Fetch submissions from a subreddit."""
    if post_type == 'top':
        return subreddit.top('all', limit=limit, params={'after': after})
    elif post_type == 'hot':
        return subreddit.hot(limit=limit, params={'after': after})
    elif post_type == 'new':
        return subreddit.new(limit=limit, params={'after': after})
    else:
        print("Invalid post type. Choose 'top', 'hot', or 'new'.")
        return []

def download_subreddit_media(subreddit_name, post_type, limit):
    """Download media from a subreddit to a specified directory."""
    subreddit = reddit.subreddit(subreddit_name)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    media_directory = os.path.join(script_directory, subreddit_name)
    os.makedirs(media_directory, exist_ok=True)

    downloaded_hashes = set()
    downloaded_count = 0
    after = None

    while downloaded_count < limit:
        submissions = fetch_submissions(subreddit, post_type, limit, after)
        for submission in submissions:
            if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')) or 'v.redd.it' in submission.url:
                if 'v.redd.it' in submission.url:
                    video_url = f"https://v.redd.it/{submission.id}/DASH_1080.mp4"
                    filename = f"{submission.id}.mp4"
                else:
                    video_url = submission.url
                    filename = submission.url.split("/")[-1]

                file_contents = download_media(video_url, media_directory, filename)
                if file_contents is not None:
                    file_hash = hash_file_contents(file_contents)
                    if file_hash not in downloaded_hashes:
                        downloaded_hashes.add(file_hash)
                        downloaded_count += 1
                        print(f"{downloaded_count} of {limit} downloaded")
                        if downloaded_count >= limit:
                            break
                    else:
                        os.remove(os.path.join(media_directory, filename))
                        print(f"Skipped duplicate file {filename} ({downloaded_count} of {limit} downloaded)")

            after = submission.name

        if after is None:
            break

if __name__ == "__main__":
    subreddit_name = input("Enter the subreddit name: ")
    post_type = input("Do you want 'top', 'hot', or 'new' posts? ")
    limit = int(input("Enter the number of posts to download: "))
    download_subreddit_media(subreddit_name, post_type, limit)
