import time
import random
import requests
import ssl
import threading
import sys
import tkinter as tk
from tkinter import simpledialog

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

stop_flag = False

def stop_execution():
    global stop_flag
    input("Press ENTER to stop the script...")
    stop_flag = True
    print("Stopping script...")

threading.Thread(target=stop_execution, daemon=True).start()

def get_proxy_from_api():
    api_endpoint = "http://pubproxy.com/api/proxy?limit=1&format=txt&type=http"
    try:
        response = requests.get(api_endpoint, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error getting proxy from API: {e}")
        return None

# Create a GUI window for user input
root = tk.Tk()
root.withdraw()  # Hide the root window

url = simpledialog.askstring("Input", "Enter the YouTube video URL:")
duration = simpledialog.askinteger("Input", "Enter the duration to watch the video (in seconds):")
views = simpledialog.askinteger("Input", "Enter the number of views to simulate:")
view_interval = simpledialog.askinteger("Input", "Enter the time interval between views (in seconds):")

def detect_video_type(driver):
    try:
        # Check for LIVE badge
        live_badge = driver.find_elements(By.XPATH, "//span[contains(text(), 'LIVE')]")
        return "live" if live_badge else "uploaded"
    except Exception as e:
        print(f"Error detecting video type: {e}")
        return "unknown"

def random_scroll(driver):
    for _ in range(random.randint(5, 10)):
        scroll_distance = random.randint(200, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        time.sleep(random.uniform(1, 3))
        driver.execute_script(f"window.scrollBy(0, {-scroll_distance});")
        time.sleep(random.uniform(1, 3))

def simulate_user_interactions(url):
    global stop_flag
    if stop_flag:
        print("Script stopped before starting interaction.")
        return

    proxy = get_proxy_from_api()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--mute-audio")
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "video")))
        time.sleep(5)

        # Detect if the video is live or uploaded
        video_type = detect_video_type(driver)
        print(f"Detected: This is a {video_type} video.")
        
        play_button = driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button.ytp-button")
        if "paused" in play_button.get_attribute("class"):
            play_button.click()
        
        for _ in range(duration):
            if stop_flag:
                print("Stopping script...")
                driver.quit()
                return
            if random.random() < 0.3:  # 30% chance to scroll while watching
                random_scroll(driver)
            time.sleep(1)
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        
    except Exception as e:
        print(f"Error during interaction: {e}")
    finally:
        if driver:
            driver.quit()

for i in range(views):
    if stop_flag:
        print("Stopping script...")
        break
    start_time = time.time()
    simulate_user_interactions(url)
    print(f"View {i+1} successful")
    
    while time.time() - start_time < view_interval:
        if stop_flag:
            print("Stopping script...")
            break
        time.sleep(1)

print("Script execution completed.")
