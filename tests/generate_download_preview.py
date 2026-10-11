import urllib.request
import re

html = urllib.request.urlopen('http://127.0.0.1:5000/ru/products/financial-war-room').read().decode('utf-8')
match = re.search(r'<section id="download-center".*?</section>', html, re.DOTALL)
if match:
    section_html = match.group(0)
    head_match = re.search(r'<head>.*?</head>', html, re.DOTALL)
    head_content = head_match.group(0) if head_match else ''
    
    # Replace relative static urls with localhost urls
    head_content = head_content.replace('href="/static/', 'href="http://127.0.0.1:5000/static/')
    section_html = section_html.replace('href="/static/', 'href="http://127.0.0.1:5000/static/')

    full_preview = f"""<!DOCTYPE html>
<html lang="ru" data-theme="dark">
{head_content}
<body style="background: #050811; padding: 40px 0; min-height: 100vh;">
{section_html}
<script src="http://127.0.0.1:5000/static/js/main.js"></script>
</body>
</html>"""
    with open('tests/download_preview.html', 'w', encoding='utf-8') as f:
        f.write(full_preview)
    print("Created tests/download_preview.html successfully")
else:
    print("Could not find download-center section")
