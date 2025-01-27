import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from instaloader import Instaloader, Profile
from selenium.common.exceptions import NoSuchElementException

# Constants
CHROMEDRIVER_PATH = 'C:\\Users\\nalot\\Downloads\\chromedriver-win64\\chromedriver-win64'  # Update with your chromedriver path

# Initialize Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Scrape YouTube
async def scrape_youtube(url):
    print("Scraping YouTube...")
    driver = init_driver()
    driver.get(url)
    time.sleep(3)

    data = {}
    try:
        # Scrape video title
        title = driver.find_element(By.XPATH, '//*[@id="container"]/h1').text
        data["Title"] = title

        # Scrape comments (first 5 for demonstration)
        comments = []
        comment_elements = driver.find_elements(By.XPATH, '//*[@id="content-text"]')[:5]
        for comment in comment_elements:
            comments.append(comment.text)
        data["Comments"] = comments
    except NoSuchElementException:
        print("Failed to scrape YouTube data. Elements not found.")
    finally:
        driver.quit()
    return data

# Scrape TikTok
async def scrape_tiktok(url):
    print("Scraping TikTok...")
    driver = init_driver()
    driver.get(url)
    time.sleep(5)  # Wait for page to load

    data = {}
    try:
        # Scrape username
        username = driver.find_element(By.XPATH, '//h1[@data-e2e="user-title"]').text
        data["Username"] = username

        # Scrape follower count
        follower_count = driver.find_element(By.XPATH, '//strong[@data-e2e="followers-count"]').text
        data["Followers"] = follower_count
    except NoSuchElementException:
        print("Failed to scrape TikTok data. Elements not found.")
    finally:
        driver.quit()
    return data

# Scrape Instagram
async def scrape_instagram(url):
    print("Scraping Instagram...")
    L = Instaloader()
    username = url.split("/")[-2]  # Extract username from URL

    data = {}
    try:
        profile = Profile.from_username(L.context, username)

        # Scrape follower count and recent posts (first 5 for demonstration)
        data["Username"] = username
        data["Followers"] = profile.followers
        posts = []
        for post in profile.get_posts()[:5]:
            posts.append({"Caption": post.caption, "Likes": post.likes})
        data["Posts"] = posts
    except Exception as e:
        print(f"Failed to scrape Instagram data: {e}")
    return data

# Scrape Facebook
async def scrape_facebook(url):
    print("Scraping Facebook...")
    driver = init_driver()
    driver.get(url)
    time.sleep(5)  # Wait for page to load

    data = {}
    try:
        # Scrape page name
        page_name = driver.find_element(By.XPATH, '//h1').text
        data["Page Name"] = page_name

        # Scrape recent posts (first 5 for demonstration)
        posts = []
        post_elements = driver.find_elements(By.XPATH, '//div[@role="article"]')[:5]
        for post in post_elements:
            posts.append(post.text)
        data["Posts"] = posts
    except NoSuchElementException:
        print("Failed to scrape Facebook data. Elements not found.")
    finally:
        driver.quit()
    return data

# Identify platform from URL
def identify_platform(url):
    if "youtube.com" in url:
        return "youtube"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "instagram.com" in url:
        return "instagram"
    elif "facebook.com" in url:
        return "facebook"
    else:
        raise ValueError("Unsupported platform")

# Main scraping function
async def scrape_social_media(url):
    platform = identify_platform(url)
    if platform == "youtube":
        return await scrape_youtube(url)
    elif platform == "tiktok":
        return await scrape_tiktok(url)
    elif platform == "instagram":
        return await scrape_instagram(url)
    elif platform == "facebook":
        return await scrape_facebook(url)

# GUI Application
class SocialMediaScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Social Media Scraper")
        self.root.geometry("400x200")

        # URL Input
        self.label = ttk.Label(root, text="Enter URL:")
        self.label.pack(pady=10)

        self.url_entry = ttk.Entry(root, width=50)
        self.url_entry.pack(pady=10)

        # Scrape Button
        self.scrape_button = ttk.Button(root, text="Scrape", command=self.start_scraping)
        self.scrape_button.pack(pady=20)

    def start_scraping(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        # Disable the scrape button to prevent multiple clicks
        self.scrape_button.config(state=tk.DISABLED)

        # Run the scraping task in the asyncio event loop
        asyncio.create_task(self.run_scraping(url))

    async def run_scraping(self, url):
        try:
            scraped_data = await scrape_social_media(url)
            print("Scraped Data:", scraped_data)

            # Save to CSV
            if isinstance(scraped_data, dict):
                df = pd.DataFrame([scraped_data])
            else:
                df = pd.DataFrame(scraped_data)
            df.to_csv("scraped_data.csv", index=False)
            messagebox.showinfo("Success", "Data saved to 'scraped_data.csv'")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scrape data: {e}")
        finally:
            # Re-enable the scrape button
            self.scrape_button.config(state=tk.NORMAL)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = SocialMediaScraperApp(root)

    # Start the asyncio event loop
    async def run_tk():
        while True:
            root.update()
            await asyncio.sleep(0.05)

    asyncio.get_event_loop().run_until_complete(run_tk())