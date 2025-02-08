import wikipediaapi
import requests

def search(keyword):
    wiki = wikipediaapi.Wikipedia('MyProject/1.0 (your_@email.com)', 'en')
    page = wiki.page(keyword)
    
    result = page.text
    
    # 이미지 URL 가져오기
    images = get_images(keyword)
    
    return result, images

def get_images(keyword):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": keyword,
        "prop": "images",
        "imlimit": "5"  # 가져올 이미지 수 제한
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    image_urls = []
    pages = data["query"]["pages"]
    for page in pages.values():
        if "images" in page:
            for image in page["images"]:
                if image["title"].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image_url = get_image_url(image["title"])
                    if image_url:
                        image_urls.append(image_url)
    
    return image_urls

def get_image_url(image_title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": image_title,
        "prop": "imageinfo",
        "iiprop": "url"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    pages = data["query"]["pages"]
    for page in pages.values():
        if "imageinfo" in page:
            return page["imageinfo"][0]["url"]
    
    return None
