import os
import time
import subprocess

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = r"C:\Users\PLATINUM\.gemini\antigravity\scratch\critical_save_studio\docs\qa\critical_noir\iteration_3_0\after"
os.makedirs(out_dir, exist_ok=True)

targets = [
    # Desktop Full & Hero views
    ("home_ru_desktop_1440.png", "http://127.0.0.1:5000/ru", 1440, 3200),
    ("home_en_desktop_1440.png", "http://127.0.0.1:5000/en", 1440, 3200),
    ("home_ru_mobile_390.png", "http://127.0.0.1:5000/ru", 390, 3800),
    ("games_ru_desktop_1440.png", "http://127.0.0.1:5000/ru/games", 1440, 2600),
    ("games_en_desktop_1440.png", "http://127.0.0.1:5000/en/games", 1440, 2600),
    ("games_ru_mobile_390.png", "http://127.0.0.1:5000/ru/games", 390, 3200),
    ("fwr_ru_desktop_1440.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 1440, 3600),
    ("fwr_en_desktop_1440.png", "http://127.0.0.1:5000/en/products/financial-war-room", 1440, 3600),
    ("fwr_ru_tablet_768.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 768, 3800),
    ("fwr_ru_mobile_390.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 390, 4200),
    ("about_ru_desktop_1440.png", "http://127.0.0.1:5000/ru/about", 1440, 2200),
    ("software_ru_desktop_1440.png", "http://127.0.0.1:5000/ru/software", 1440, 2400),
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
    print(f"Capturing {filename} ({width}x{height})...")
    try:
        subprocess.run(cmd, check=True, timeout=15)
    except Exception as e:
        print(f"Failed {filename}: {e}")
    time.sleep(0.3)

print("Iteration 3.0 AFTER screenshots captured.")
