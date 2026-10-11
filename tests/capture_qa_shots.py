import os
import time
import subprocess

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = r"C:\Users\PLATINUM\.gemini\antigravity\scratch\critical_save_studio\docs\qa\critical_noir"
os.makedirs(out_dir, exist_ok=True)

targets = [
    ("home_ru_dark_1440.png", "http://127.0.0.1:5000/ru", 1440, 1080),
    ("home_ru_mobile_390.png", "http://127.0.0.1:5000/ru", 390, 844),
    ("fwr_ru_dark_1440.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 1440, 1200),
    ("fwr_en_dark_1440.png", "http://127.0.0.1:5000/en/products/financial-war-room", 1440, 1200),
    ("fwr_ru_mobile_390.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 390, 844),
    ("download_ru_dark_1440.png", "http://127.0.0.1:5000/ru/products/financial-war-room#download-center", 1440, 1100),
    ("download_ru_tablet_768.png", "http://127.0.0.1:5000/ru/products/financial-war-room#download-center", 768, 1024),
    ("download_ru_mobile_390.png", "http://127.0.0.1:5000/ru/products/financial-war-room#download-center", 390, 844),
    ("catalog_ru_dark_1440.png", "http://127.0.0.1:5000/ru/games", 1440, 1080),
    ("software_ru_dark_1440.png", "http://127.0.0.1:5000/ru/software", 1440, 1080),
    ("software_ru_mobile_390.png", "http://127.0.0.1:5000/ru/software", 390, 844),
]

for filename, url, width, height in targets:
    out_file = os.path.join(out_dir, filename)
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={out_file}",
        url
    ]
    print(f"Capturing {filename}...")
    subprocess.run(cmd, check=True)
    time.sleep(0.5)

print("All visual QA screenshots captured successfully.")
