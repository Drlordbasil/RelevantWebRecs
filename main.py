import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class WebPage:
    def __init__(self, url, text):
        self.url = url
        self.text = text
        self.content = []

    def scrape_content(self):
        soup = BeautifulSoup(self.text, 'html.parser')
        articles = soup.find_all('article')
        for article in articles:
            headline_element = article.find('h2')
            if headline_element:
                headline = headline_element.text.strip()
            else:
                headline = ''
            summary_element = article.find('p')
            if summary_element:
                summary = summary_element.text.strip()
            else:
                summary = ''

            keyword_elements = article.find_all('span', class_='keyword')
            keywords = [tag.text for tag in keyword_elements]

            url_element = article.find('a')
            if url_element and 'href' in url_element.attrs:
                url = url_element['href']
                self.content.append({'headline': headline, 'summary': summary, 'keywords': keywords, 'url': url})


class WebContentAggregator:
    def __init__(self):
        self.search_queries = []
        self.webpages = []

    def add_search_query(self, query):
        self.search_queries.append(query)

    def fetch_webpages(self):
        for query in self.search_queries:
            url = f"https://www.example.com/search?q={query}"
            response = requests.get(url)
            if response.status_code == 200:
                self.webpages.append(WebPage(url, response.text))
            else:
                print(f"Failed to fetch webpage for query: {query}")

    def scrape_content(self):
        for webpage in self.webpages:
            webpage.scrape_content()

    def deduplicate_content(self):
        unique_content = {}
        for webpage in self.webpages:
            for content in webpage.content:
                url = content['url']
                if url not in unique_content:
                    unique_content[url] = content
        self.webpages = [WebPage(url, '') for url, content in unique_content.items()]

    def recommend_content(self, user_preferences):
        vectorizer = CountVectorizer(stop_words=stopwords.words('english'))
        documents = []
        for webpage in self.webpages:
            for content in webpage.content:
                documents.append(content['summary'])

        document_vectors = vectorizer.fit_transform(documents).toarray()
        query_vector = vectorizer.transform([user_preferences]).toarray()

        similarities = cosine_similarity(document_vectors, query_vector)
        indices = np.argsort(similarities, axis=0)[::-1]

        recommendations = []
        for index in indices:
            for webpage in self.webpages:
                for content in webpage.content:
                    if content['url'] == index:
                        recommendations.append(content)
        return recommendations

    def run(self):
        self.fetch_webpages()
        self.scrape_content()
        self.deduplicate_content()
        user_preferences = input("Enter your interests: ")
        recommendations = self.recommend_content(user_preferences)
        for recommendation in recommendations:
            print(recommendation['headline'])
            print(recommendation['summary'])
            print(recommendation['url'])
            print('---')


web_aggregator = WebContentAggregator()
web_aggregator.add_search_query("Python programming")
web_aggregator.add_search_query("Data analysis")
web_aggregator.run()