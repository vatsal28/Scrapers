import os
import instaloader

def download_instagram_media(username, download_directory):
    """Download all media of an Instagram user to a specified directory."""
    # Initialize Instaloader
    loader = instaloader.Instaloader(
        dirname_pattern=os.path.join(download_directory, '{profile}'),
        download_videos=True,
        download_pictures=True,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern=""
    )
    
    # Load the profile
    profile = instaloader.Profile.from_username(loader.context, username)
    
    # Iterate through all posts of the profile
    for post in profile.get_posts():
        print(f"Downloading {post.url}")
        loader.download_post(post, target=profile.username)

if __name__ == "__main__":
    instagram_username = input("Enter the Instagram username: ")
    download_directory = input("Enter the directory to download files to: ")
    download_instagram_media(instagram_username, download_directory)
