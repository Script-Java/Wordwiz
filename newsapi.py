import requests
import pretty_errors

def get_news(key):
    url = 'https://newsapi.org/v2/top-headlines?country=us'
    # category business entertainment general healthscience sports technology
    params = {
        'apiKey': key,
        'category': 'business'
    }
    article_data = []
    counter = 0
    try:
        req = requests.get(url, params=params)
        
        if req.status_code == 200:
            res = req.json()
            articles = res['articles']
            
            for article in articles:
                author = article['author']
                title = article['title']
                description = article['description']
                url = article['url']
                article_json = {
                    'author': author,
                    'title': title,
                    'description': description,
                    'url': url
                }
                article_data.append(article_json)
                counter += 1
                if counter == 6:
                    return article_data
                
        else:
            print('Failed to retrieve articles. Status code', res.status_code)
    
    except Exception as e:
        print('Error:', str(e))



# '7d33db3af6664d2cbb3c69ffb0a29285'

