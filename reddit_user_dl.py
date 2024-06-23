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

def get_gfycat_media_url(url):
    """Get the media URL for a Gfycat link."""
    gfycat_id = url.split('/')[-1]
    json_url = f"https://api.gfycat.com/v1/gfycats/{gfycat_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(json_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['gfyItem']['mp4Url']
    return None

def get_redgifs_media_url(url):
    """Get the media URL for a Redgifs link."""
    redgifs_id = url.split('/')[-1]
    json_url = f"https://api.redgifs.com/v1/gfycats/{redgifs_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(json_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['gfyItem']['mp4Url']
    return None

def download_user_media(username, download_directory):
    """Download all media of a Reddit user to a specified directory, excluding duplicates."""
    if username.startswith('u/'):
        username = username[2:]

    user = reddit.redditor(username)
    media_directory = os.path.join(download_directory, username)
    os.makedirs(media_directory, exist_ok=True)

    downloaded_hashes = set()
    submissions = list(user.submissions.new(limit=None))
    total = len(submissions)
    count = 0

    for submission in submissions:
        count += 1
        url = submission.url
        filename = f"{submission.id}"

        if url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4')):
            ext = url.split('.')[-1]
            filename = f"{filename}.{ext}"
            file_contents = download_media(url, media_directory, filename)
            if file_contents is not None:
                file_hash = hash_file_contents(file_contents)
                if file_hash not in downloaded_hashes:
                    downloaded_hashes.add(file_hash)
                    print(f"{count} of {total} downloaded")
                else:
                    os.remove(os.path.join(media_directory, filename))
                    print(f"{count} of {total} skipped (duplicate)")
        elif 'v.redd.it' in url:
            video_url = f"https://v.redd.it/{submission.id}/DASH_1080.mp4"
            filename = f"{filename}.mp4"
            file_contents = download_media(video_url, media_directory, filename)
            if file_contents is not None:
                file_hash = hash_file_contents(file_contents)
                if file_hash not in downloaded_hashes:
                    downloaded_hashes.add(file_hash)
                    print(f"{count} of {total} downloaded")
                else:
                    os.remove(os.path.join(media_directory, filename))
                    print(f"{count} of {total} skipped (duplicate)")
        elif 'gfycat.com' in url:
            media_url = get_gfycat_media_url(url)
            if media_url:
                filename = f"{filename}.mp4"
                file_contents = download_media(media_url, media_directory, filename)
                if file_contents is not None:
                    file_hash = hash_file_contents(file_contents)
                    if file_hash not in downloaded_hashes:
                        downloaded_hashes.add(file_hash)
                        print(f"{count} of {total} downloaded")
                    else:
                        os.remove(os.path.join(media_directory, filename))
                        print(f"{count} of {total} skipped (duplicate)")
        elif 'redgifs.com' in url:
            media_url = get_redgifs_media_url(url)
            if media_url:
                filename = f"{filename}.mp4"
                file_contents = download_media(media_url, media_directory, filename)
                if file_contents is not None:
                    file_hash = hash_file_contents(file_contents)
                    if file_hash not in downloaded_hashes:
                        downloaded_hashes.add(file_hash)
                        print(f"{count} of {total} downloaded")
                    else:
                        os.remove(os.path.join(media_directory, filename))
                        print(f"{count} of {total} skipped (duplicate)")
        elif 'redditmedia.com' in url:
            filename = f"{filename}.gif"
            file_contents = download_media(url, media_directory, filename)
            if file_contents is not None:
                file_hash = hash_file_contents(file_contents)
                if file_hash not in downloaded_hashes:
                    downloaded_hashes.add(file_hash)
                    print(f"{count} of {total} downloaded")
                else:
                    os.remove(os.path.join(media_directory, filename))
                    print(f"{count} of {total} skipped (duplicate)")

if __name__ == "__main__":
    reddit_username = input("Enter the Reddit username (u/username): ")
    download_directory = input("Enter the directory to download files to: ")
    download_user_media(reddit_username, download_directory)
