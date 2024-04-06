import os
import requests
from bs4 import BeautifulSoup
from Class.LoggingConfig import logging
from urllib.parse import urlparse, urljoin


class PostImageCrawler:
    def __init__(self, post_url: str):
        self.post_url = self.adjust_post_url(post_url)
        self.all_img_urls = []

        logging.info(f"Init PostImageCrawler (post_url: {self.post_url})")

        self.fetch_all_img_urls()

    def get_all_img_urls(self):
        return self.all_img_urls

    def get_all_img_urls_len(self):
        return len(self.all_img_urls)

    @staticmethod
    def adjust_post_url(self, url):
        return url.replace("blog.naver.com", "m.blog.naver.com") if "m.blog.naver.com" not in url else url

    def fetch_all_img_urls(self):
        try:
            response = requests.get(self.post_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                self.extract_img_urls(soup)
            else:
                logging.error(f"Failed to access {self.post_url}")
        except requests.RequestException as e:
            logging.error(f"Error while getting all image URLs: {e}")

    def extract_img_urls(self, soup):
        file_box = soup.find('div', id='_photo_view_property')
        if file_box:
            file_info = file_box['attachimagepathandidinfo'].strip("[]").split('},{')
            for info in file_info:
                if '"path"' in info:
                    img_url = self.extract_url_from_info(info)
                    if img_url and self.is_valid_url(img_url):
                        self.all_img_urls.append(img_url)
                    else:
                        logging.warning(f"Invalid URL skipped: {img_url}")

    @staticmethod
    def extract_url_from_info(info):
        path_start = info.find('"path":') + len('"path":')
        path_end = info.find(',', path_start) if ',' in info else len(info)
        img_path = info[path_start:path_end].strip('"')

        return urljoin("https://blogfiles.pstatic.net", img_path) if img_path else None

    @staticmethod
    def is_valid_url(url):
        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def download_all_img(self, path: str):
        for img_url in self.all_img_urls:
            try:
                self.download_img(img_url, path)
            except Exception as e:
                logging.error(f"Error downloading {img_url}: {e}")

    @staticmethod
    def download_img(img_url, path):
        file_name = os.path.basename(urlparse(img_url).path)
        full_path = os.path.join(path, file_name)
        if not os.path.exists(full_path):
            response = requests.get(img_url)
            if response.status_code == 200:
                with open(full_path, 'wb') as file:
                    file.write(response.content)
                logging.info(f"Downloaded {img_url} as {full_path}")
            else:
                logging.error(f"Failed to download {img_url} - HTTP Status Code: {response.status_code}")
        else:
            logging.debug(f"File already exists: {full_path}")
