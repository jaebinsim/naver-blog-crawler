import os
import json
import re
from datetime import date, datetime

from Class.LoggingConfig import logging
from Crawler.PostSearchCrawler import PostSearchCrawler
from Crawler.PostImageCrawler import PostImageCrawler


class Subject:
    min_image_count = 2

    def __init__(self,
                 name: str,
                 keywords: [str],
                 search_date: date,
                 output_path: str,
                 count_per_page: int,
                 order_by_sim: bool = False,
                 max_search_page: int = 1
                 ):
        self.name = name
        self.keywords = keywords
        self.search_date = search_date
        self.output_path = output_path
        self.count_per_page = count_per_page
        self.order_by_sim = order_by_sim
        self.max_search_page = max_search_page

        self.complete_posts_json_file_path = os.path.join(self.output_path, "complete_posts.json")

        logging.info("")
        logging.info(f"Init Subject "
                     f"(name: {name}, "
                     f"search_date: {search_date}, "
                     f"output_path: {output_path}, "
                     f"count_per_page: {count_per_page}, "
                     f"order_by_sim: {order_by_sim}, "
                     f"max_search_page: {max_search_page})")

    def run(self):
        logging.info("")

        if not os.path.exists(self.complete_posts_json_file_path):
            self.create()
        else:
            self.update()

    def create(self):
        logging.info(f"Start Create")

        self.make_subject_directory()

        all_posts = self.get_all_posts_from_keywords()

        for post in all_posts:
            self.post_job(post)

        self.save_complete_posts_to_json_file(all_posts, self.complete_posts_json_file_path)

    def read(self):
        pass

    def update(self):
        logging.info(f"Start Update")

        complete_posts = self.load_complete_posts_from_json_file(self.complete_posts_json_file_path)
        all_posts = self.get_all_posts_from_keywords()

        complete_post_urls = {post.get("postUrl") for post in complete_posts}
        all_post_urls = {post.get("postUrl") for post in all_posts}

        update_target_post_urls = all_post_urls - complete_post_urls

        update_target_posts = [post for post in all_posts if post.get("postUrl") in update_target_post_urls]

        logging.info(f"Updated Posts: {len(update_target_posts)}")

        if update_target_posts == 0:
            return

        for post in update_target_posts:
            self.post_job(post)

        self.save_complete_posts_to_json_file(all_posts, self.complete_posts_json_file_path)

    def delete(self):
        pass

    def save_complete_posts_to_json_file(self, posts: list, filename: str):
        if os.path.exists(filename):
            os.remove(filename)

        self.save_post_list_to_json_file(posts, filename)

    @staticmethod
    def load_complete_posts_from_json_file(filename: str) -> set:
        loaded_posts = []

        try:
            with open(filename, 'r') as json_file:
                loaded_posts = json.load(json_file)
        except FileNotFoundError:
            pass
        except json.JSONDecodeError as e:
            logging.info(f"Error decoding JSON file: {e}")
            pass

        return loaded_posts

    def make_subject_directory(self):
        logging.info(f"Subject Directory created: \"{self.output_path}\"")
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def get_psc_result_posts(self, keyword: str):
        bsc = PostSearchCrawler(
            keyword=keyword,
            search_date=self.search_date,
            count_per_page=self.count_per_page,
            order_by_sim=self.order_by_sim,
            max_search_page=self.max_search_page
        )
        return bsc.get_result_all_posts()

    def get_all_posts_from_keywords(self):
        all_posts = []

        for keyword in self.keywords:
            posts = self.get_psc_result_posts(keyword)
            for post in posts:
                if post not in all_posts:
                    all_posts.append(post)

        return all_posts

    def post_job(self, post):
        post_directory_name = self.generate_post_directory_name(post)
        post_directory_path = os.path.join(self.output_path, post_directory_name)

        logging.info("")
        logging.info(f"Post Job Start: (\"{post_directory_path}\")")

        if not os.path.exists(post_directory_path):
            logging.info(f"Make Directory")
            os.makedirs(post_directory_path)

        post_url = post['postUrl']
        bic = PostImageCrawler(post_url=post_url)

        if bic.get_all_img_urls_len() < self.min_image_count:
            logging.info(f"All Images Len is {bic.get_all_img_urls_len()} Skip")
            return

        self.save_post_list_to_json_file(post, os.path.join(post_directory_path, "post_info.json"))
        self.save_post_info_to_txt_file(post, os.path.join(post_directory_path, "post_info.txt"))

        download_all_img_path = os.path.join(post_directory_path)
        bic.download_all_img(path=download_all_img_path)

    @staticmethod
    def save_post_list_to_json_file(post: list, filename: str):
        def datetime_converter(o):
            if isinstance(o, datetime):
                return o.isoformat()

        with open(filename, "w") as json_file:
            json.dump(post, json_file, default=datetime_converter)

    def save_post_info_to_txt_file(self, post: dict, filename: str):
        keys = {
            'title': 'Title',
            'nickName': 'Nick Name',
            'blogName': 'Blog Name',
            'postUrl': 'Post URL',
            'blogUrlPC': 'Blog URL (PC)',
            'blogUrlMobile': 'Blog URL (Mobile)',
        }

        postUrl = post.get('postUrl', '')

        blog_url_pc = postUrl.rsplit('/', 1)[0]
        blog_url_mobile = blog_url_pc.replace('blog.naver.com', 'm.blog.naver.com')

        blog_id = blog_url_pc.split('/')[-1]

        blog_search_url_pc = []
        blog_search_url_mobile = []

        for keyword in self.keywords:
            search_url_pc = f"https://blog.naver.com/PostSearchList.naver?blogId={blog_id}&orderType=sim&searchText={keyword}"
            blog_search_url_pc.append((keyword, search_url_pc))

            search_url_mobile = search_url_pc.replace('blog.naver.com', 'm.blog.naver.com')
            blog_search_url_mobile.append((keyword, search_url_mobile))

        new_post = post.copy()
        new_post['blogUrlPC'] = blog_url_pc
        new_post['blogUrlMobile'] = blog_url_mobile

        extra_labels = [f"Blog Search URL (PC) ({keyword})" for keyword, _ in blog_search_url_pc]
        extra_labels += [f"Blog Search URL (Mobile) ({keyword})" for keyword, _ in blog_search_url_mobile]

        with open(filename, 'w', encoding='utf-8') as file:
            for key, label in keys.items():
                value = new_post.get(key, '')
                if not 'url' in label.lower():
                    tabs = self.get_tabs_for_windows(label)
                    file.write(f"{label}:{tabs}{value}\n")
                else:
                    file.write(f"\n{label}:\n{value}\n")

            for pc, mobile in zip(blog_search_url_pc, blog_search_url_mobile):
                pc_keyword, pc_url = pc
                mobile_keyword, mobile_url = mobile

                pc_label = f"Blog Search URL (PC) ({pc_keyword})"
                file.write(f"\n{pc_label}:\n{pc_url}\n")

                mobile_label = f"Blog Search URL (Mobile) ({mobile_keyword})"
                file.write(f"\n{mobile_label}:\n{mobile_url}\n")

    @staticmethod
    def get_tabs_for_windows(label):
        tab_len = 4
        if len(label) < 6:
            tab_len += 1
        return '\t' * tab_len

    @staticmethod
    def generate_post_directory_name(post: dict):
        addDate_str = post['addDate'].strftime('%Y-%m-%d_%H-%M-%S')

        nickName_clean = re.sub(r'[^\w\s]', '', post['nickName'])[:20].strip()
        title_clean = re.sub(r'[^\w\s]', '', post['title'])[:20].strip()

        directory_name = f"[{addDate_str}] [{nickName_clean}] [{title_clean}]"

        return directory_name
