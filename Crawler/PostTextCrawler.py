import re

import requests
from bs4 import BeautifulSoup
from Class.LoggingConfig import logging


class PostTextCrawler:
    def __init__(self, post_url: str):
        self.post_url = self.adjust_post_url(post_url)
        self.post_text = ""
        self.post_text_lines = []

        logging.info(f"Init PostTextCrawler (post_url: {self.post_url})")
        self.fetch_post_text()
        self.split_post_text_lines()

    def split_post_text_lines(self):
        self.post_text_lines = self.post_text.split('\n')
        self.post_text_lines = [line.strip() for line in self.post_text_lines if line.strip()]

    def get_post_text(self):
        return self.post_text

    def is_include_keyword(self, keywords):
        if isinstance(keywords, str):
            keywords = [keywords]

        for keyword in keywords:
            pattern = re.compile(re.escape(''.join(keyword.split())), re.IGNORECASE)
            for line in self.post_text_lines:
                if pattern.search(line):
                    return True

        return False

    def get_include_keyword_matching_contexts(self, keywords, show_line: int = 2):
        matching_contexts = []

        if isinstance(keywords, str):
            keywords = [keywords]

        for keyword in keywords:
            pattern = re.compile(re.escape(''.join(keyword.split())), re.IGNORECASE)
            for i, line in enumerate(self.post_text_lines):
                if pattern.search(line):
                    start = max(i - show_line, 0)
                    end = min(i + show_line + 1, len(self.post_text_lines))

                    context = '\n'.join(self.post_text_lines[start:end])
                    matching_contexts.append({keyword: context})

        return matching_contexts

    @staticmethod
    def adjust_post_url(url):
        return url.replace("blog.naver.com", "m.blog.naver.com") if "m.blog.naver.com" not in url else url

    def fetch_post_text(self):
        try:
            response = requests.get(self.post_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                self.extract_post_text(soup)
            else:
                logging.error(f"Failed to access {self.post_url}")
        except requests.RequestException as e:
            logging.error(f"Error while getting post text: {e}")

    def extract_post_text(self, soup):
        post_content = soup.find('div', class_='se-main-container')
        if post_content:
            self.post_text = post_content.get_text(separator='\n')
        else:
            logging.warning("Failed to find the post content element.")

