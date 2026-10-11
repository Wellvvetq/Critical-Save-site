import os
import time
import subprocess

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_dir = r"C:\Users\PLATINUM\.gemini\antigravity\scratch\critical_save_studio\docs\qa\critical_noir\iteration_3_1\after"
os.makedirs(out_dir, exist_ok=True)

targets = [
    # Desktop 1440px
    ("home_ru_1440.png", "http://127.0.0.1:5000/ru", 1440, 3200),
    ("home_en_1440.png", "http://127.0.0.1:5000/en", 1440, 3200),
    ("games_ru_1440.png", "http://127.0.0.1:5000/ru/games", 1440, 2600),
    ("games_en_1440.png", "http://127.0.0.1:5000/en/games", 1440, 2600),
    ("games_filtered_ru_1440.png", "http://127.0.0.1:5000/ru/games?genre=%D0%98%D1%81%D1%81%D0%BB%D0%B5%D0%B4%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5", 1440, 2000),
    ("fwr_ru_1440.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 1440, 3600),
    ("fwr_en_1440.png", "http://127.0.0.1:5000/en/products/financial-war-room", 1440, 3600),
    ("about_ru_1440.png", "http://127.0.0.1:5000/ru/about", 1440, 2200),
    ("software_ru_1440.png", "http://127.0.0.1:5000/ru/software", 1440, 2400),

    # Tablet 768px
    ("home_ru_768.png", "http://127.0.0.1:5000/ru", 768, 3600),
    ("games_ru_768.png", "http://127.0.0.1:5000/ru/games", 768, 2800),
    ("fwr_ru_768.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 768, 3800),

    # Mobile 390px
    ("home_ru_390.png", "http://127.0.0.1:5000/ru", 390, 3800),
    ("games_ru_390.png", "http://127.0.0.1:5000/ru/games", 390, 3200),
    ("fwr_ru_390.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 390, 4200),

    # Mobile min 320px
    ("home_ru_320.png", "http://127.0.0.1:5000/ru", 320, 3900),
    ("games_ru_320.png", "http://127.0.0.1:5000/ru/games", 320, 3300),
    ("fwr_ru_320.png", "http://127.0.0.1:5000/ru/products/financial-war-room", 320, 4300),
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

print(f"Iteration 3.1 AFTER screenshots captured successfully to {out_dir}.")
