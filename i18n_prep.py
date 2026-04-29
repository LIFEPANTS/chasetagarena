import os
import json
from bs4 import BeautifulSoup
import re

html_files = ["index.html", "guide.html", "privacy.html", "terms.html"]
all_strings = {}

def process_file(filename):
    if not os.path.exists(filename):
        return
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # We want to add data-i18n to tags that contain direct text
    # Or just wrap text nodes in <span data-i18n="..."></span>
    
    # For simplicity, we just extract all visible text nodes that have word characters
    count = len(all_strings)
    
    for text_node in soup.find_all(string=True):
        parent = text_node.parent
        if parent.name in ['script', 'style', 'head', 'title', 'meta', '[document]', 'nav']:
            continue
        text = text_node.strip()
        if re.search(r'[a-zA-Z]', text) and len(text) > 1:
            # find if it already exists
            key = None
            for k, v in all_strings.items():
                if v == text:
                    key = k
                    break
            if not key:
                key = f"t_{len(all_strings)}"
                all_strings[key] = text
            
            # Wrap or tag
            if parent.name in ['h1', 'h2', 'h3', 'p', 'a', 'span', 'strong', 'em', 'button', 'li']:
                if len(parent.contents) == 1:
                    parent['data-i18n'] = key
                else:
                    # Replace text node with a span
                    new_tag = soup.new_tag("span")
                    new_tag['data-i18n'] = key
                    new_tag.string = text_node
                    text_node.replace_with(new_tag)
            else:
                new_tag = soup.new_tag("span")
                new_tag['data-i18n'] = key
                new_tag.string = text_node
                text_node.replace_with(new_tag)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(soup))

for f in html_files:
    process_file(f)

with open('en_strings.json', 'w', encoding='utf-8') as f:
    json.dump(all_strings, f, indent=4)
