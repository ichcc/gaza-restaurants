import json
import sys
import requests
import os
from urllib.parse import urlparse


def get_restaurant_info(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            handle = f"@{path_parts[0]}"
            if "instagram.com" in parsed_url.netloc:
                return {
                    "name": path_parts[0].replace("_", " ").replace(".", " ").title(),
                    "platform": "Instagram",
                    "handle": handle,
                    "url": url,
                    "description": ""
                }
            elif "tiktok.com" in parsed_url.netloc:
                return {
                    "name": path_parts[0].replace("_", " ").replace(".", " ").title(),
                    "platform": "TikTok",
                    "handle": handle,
                    "url": url,
                    "description": ""
                }
    except requests.RequestException as e:
        print(f"Error checking url {url}: {e}")
    return None

def update_restaurants_file(new_restaurants):
    with open('restaurants.json', 'r+') as f:
        data = json.load(f)
        existing_urls = {r['url'] for r in data}
        for restaurant in new_restaurants:
            if restaurant['url'] not in existing_urls:
                data.append(restaurant)
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def regenerate_markdown_table():
    with open('restaurants.json', 'r') as f:
        restaurants = json.load(f)
    with open('gaza_restaurants_table.md', 'w') as f:
        f.write("# Active Restaurants in Gaza - Social Media Links\n\n")
        f.write("| Restaurant/Business Name | Platform | Handle/Username | Description |\n")
        f.write("|-------------------------|----------|-----------------|-------------|\n")
        for r in restaurants:
            f.write(f"| {r['name']} | {r['platform']} | [{r['handle']}]({r['url']}) | {r['description']} |\n")

def commit_changes():
    os.system("git add restaurants.json gaza_restaurants_table.md")
    os.system("git commit -m 'Update restaurant list'")

if __name__ == "__main__":
    if "--regenerate" in sys.argv:
        regenerate_markdown_table()
        print("Markdown table regenerated.")
        sys.exit(0)

    urls = sys.argv[1:]
    if not urls:
        print("Usage: python update.py <url1> <url2> ...")
        print("Or: python update.py --regenerate")
        sys.exit(1)

    new_restaurants = []
    for url in urls:
        restaurant_info = get_restaurant_info(url)
        if restaurant_info:
            new_restaurants.append(restaurant_info)

    if new_restaurants:
        update_restaurants_file(new_restaurants)
        regenerate_markdown_table()
        commit_changes()
        print(f"Added {len(new_restaurants)} new restaurants.")
    else:
        print("No new restaurants added.")
