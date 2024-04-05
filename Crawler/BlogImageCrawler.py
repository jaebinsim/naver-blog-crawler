import requests
from bs4 import BeautifulSoup
import urllib.request
import os
from Class.LoggingConfig import logging


class BlogImageCrawler:
    def __init__(self, post_url: str):
        self.post_url = post_url
        self.all_img_urls = []
        logging.info(f"Init BIC (post_url: {self.post_url})")

        self.fetch_all_img_urls()

    def get_all_img_urls(self):
        return self.all_img_urls

    def get_all_img_urls_len(self):
        return len(self.all_img_urls)

    def fetch_all_img_urls(self):
        if "m.blog.naver.com" not in self.post_url:
            self.post_url = self.post_url.replace("blog.naver.com", "m.blog.naver.com")
        try:
            response = requests.get(self.post_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            file_box = soup.find('div', id='_photo_view_property')

            if file_box:
                files = (
                    file_box['attachimagepathandidinfo']
                    .strip("[]")
                    .replace('"path"', '')
                    .replace('"id"','')
                    .split('"')
                )

                for i in range(1, len(files), 2):
                    img_url = "https://blogfiles.pstatic.net" + files[i]
                    self.all_img_urls.append(img_url)

        except Exception as e:
            logging.error(f"Error while getting all image URLs: {e}")

    def download_all_img(self, path: str):
        for i, img_url in enumerate(self.all_img_urls, start=1):
            try:
                file_name = f"{os.path.basename(urllib.parse.urlparse(img_url).path)}"
                full_path = os.path.join(path, file_name)

                if not os.path.exists(full_path):
                    urllib.request.urlretrieve(img_url, full_path)
                    logging.info(f"Downloaded {img_url} as {full_path}")

                else:
                    logging.info(f"File already exists: {full_path}")

            except Exception as e:
                logging.error(f"Error downloading {img_url}: {e}")

