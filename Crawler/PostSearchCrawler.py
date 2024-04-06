import requests
import json
from datetime import date, datetime, timedelta
from Class.LoggingConfig import logging


class PostSearchCrawler:
    def __init__(self,
                 keyword: str,
                 search_date: date,
                 count_per_page: int = 1000,
                 order_by_sim: bool = False,
                 max_search_page: int = 1
                 ):
        self.keyword = keyword
        self.search_date = search_date
        self.count_per_page = count_per_page
        self.order_by_sim = order_by_sim
        self.max_search_page = max_search_page
        self.result_all_posts = []

        logging.info("")
        logging.info(f"Init BSC (keyword: {self.keyword}, search_date: {self.search_date})")

        if not order_by_sim and search_date:
            self.fetch_posts_by_date(search_date=self.search_date)
        elif order_by_sim:
            self.fetch_posts_by_date_sim(search_date=self.search_date, max_search_page=self.max_search_page)

    def get_result_all_posts(self):
        return self.result_all_posts

    def fetch_posts_by_date(self, search_date):
        page = 1

        while True:
            logging.info(f"Get Response (keyword: {self.keyword}, page: {page}, count_per_page: {self.count_per_page})")
            response = self.get_response(keyword=self.keyword, order_by='recentdate', page=page,
                                         count_per_page=self.count_per_page)
            response_json = self.convert_response_to_json(response=response)
            response_list = self.convert_json_to_list(response_json=response_json)

            if not response_list:
                break

            for post in response_list:
                addDate = post.get('addDate')
                if addDate:
                    addDate = addDate.date()
                    if addDate == search_date and post not in self.result_all_posts:
                        self.result_all_posts.append(post)
                    elif addDate < search_date:
                        return

            page += 1

    def fetch_posts_by_date_sim(self, search_date, max_search_page):
        page = 1

        while page <= max_search_page:
            logging.info(f"Get Response (keyword: {self.keyword}, page: {page}, count_per_page: {self.count_per_page})")
            response = self.get_response(keyword=self.keyword, order_by="sim", page=page,
                                         count_per_page=self.count_per_page)
            response_json = self.convert_response_to_json(response=response)
            response_list = self.convert_json_to_list(response_json=response_json)

            for post in response_list:
                addDate = post.get('addDate')
                if addDate:
                    addDate = addDate.date()

                    if search_date is not None and addDate == search_date and post not in self.result_all_posts:
                        self.result_all_posts.append(post)

                    elif search_date is None and post not in self.result_all_posts:
                        self.result_all_posts.append(post)

            if page == max_search_page:
                break

            page += 1

    @staticmethod
    def get_response(keyword, order_by='recentdate', page=1, count_per_page=7):
        base_url = "https://section.blog.naver.com/ajax/SearchList.naver"
        params = {
            'countPerPage': count_per_page,
            'currentPage': page,
            'endDate': '',
            'keyword': keyword,
            'orderBy': order_by,
            'startDate': '',
            'type': 'post'
        }
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9',
            'Referer': 'https://section.blog.naver.com/Search/Post.naver',
            'Sec-Ch-Ua': '"Chromium";v="122", "Google Chrome";v="122", ";Not A Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

        response = requests.get(base_url, headers=headers, params=params)

        return response

    @staticmethod
    def convert_response_to_json(response):
        response_text = response.text
        response_json = None

        json_start_pos = response_text.find('{')

        try:
            if json_start_pos != -1:
                response_json = json.loads(response_text[json_start_pos:])
            else:
                logging.error("JSON 시작 부분을 찾을 수 없습니다.")

        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding failed: {e}")

        return response_json

    @staticmethod
    def convert_json_to_list(response_json):
        result = []

        for item in response_json['result']['searchList']:
            addDate = datetime.utcfromtimestamp(item['addDate'] / 1000) + timedelta(hours=9)
            thumbnails_urls = [thumb['url'] for thumb in item['thumbnails']]
            item_dict = {
                'postUrl': item['postUrl'],
                'title': item['title'],
                'contents': item['contents'],
                'nickName': item.get('nickName', ''),
                'blogName': item.get('blogName', ''),
                'addDate': addDate,
                'thumbnails': thumbnails_urls,
                'product': item.get('product', None),
                'hasThumbnail': item.get('hasThumbnail', False),
                'marketPost': item.get('marketPost', False)
            }

            result.append(item_dict)

        return result

