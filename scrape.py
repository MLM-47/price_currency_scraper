import requests 

URL= "https://books.toscrape.com/"

headers = {
    "user-agent": "book-scraper/1.0"
}
        
Feedback=requests.get(URL, headers=headers,timeout=5)

print(Feedback.status_code)

