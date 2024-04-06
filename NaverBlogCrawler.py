import os
import argparse
import json
from datetime import date, timedelta

from Class.LoggingConfig import logging
from Class.Subject import Subject


def parse_arguments():
    def valid_date(s):
        try:
            return date.fromisoformat(s)
        except ValueError:
            raise argparse.ArgumentTypeError("잘못된 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.")

    parser = argparse.ArgumentParser(description="Naver Blog Crawler")
    parser.add_argument("--output", type=str, required=True, help="Output directory path")
    parser.add_argument("--subject_info_json", type=str, required=False, default='subject_info.json', help="Path to the JSON file containing subject info")
    parser.add_argument("--start_date", type=valid_date, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end_date", type=valid_date, help="End date in YYYY-MM-DD format")
    parser.add_argument("--search_date", type=valid_date, default=None, help="Specific date to search in YYYY-MM-DD format")
    parser.add_argument("--order_by_sim", action='store_true', default=False, help="Search Order by Similar")
    parser.add_argument("--include_content_keyword", action='store_true', default=False, help="Filters posts to include only those with the specified keyword in their content. Requires a keyword to be specified separately")
    parser.add_argument("--count_per_page", type=int, default=10, help="Count Per Page for Search")
    parser.add_argument("--max_search_page", type=int, help="Max Search Page for Search Order by Similar")
    parser.add_argument("--min_image_count", type=int, default=2, help="Min Image Count for Search")

    args = parser.parse_args()

    if args.search_date and (args.start_date or args.end_date):
        parser.error("search_date는 start_date 또는 end_date와 함께 사용할 수 없습니다.")

    if args.start_date and args.end_date and args.start_date > args.end_date:
        parser.error("시작 날짜는 종료 날짜보다 이전이어야 합니다.")

    if args.count_per_page is not None and args.count_per_page < 1:
        parser.error("count_per_page는 1 이상이어야 합니다.")

    if args.max_search_page is not None and args.max_search_page < 1:
        parser.error("max_search_page는 1 이상이어야 합니다.")

    if args.min_image_count is not None and args.min_image_count < 1:
        parser.error("min_image_count는 1 이상이어야 합니다.")

    if args.order_by_sim and (args.max_search_page is None or args.max_search_page < 1):
        parser.error("order_by_sim을 사용하려면 max_search_page가 1 이상이어야 합니다.")

    return args


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def load_subject_info(json_filepath):
    with open(json_filepath, 'r', encoding='utf-8') as file:
        return json.load(file)


if __name__ == "__main__":
    logging.info("==================== Naver Blog Crawler Start ====================")

    args = parse_arguments()
    today = date.today()
    (
        output_directory_path, subject_info_json,
        start_date, end_date, search_date,
        order_by_sim, include_content_keyword,
        count_per_page, max_search_page, min_image_count
    ) = (
        args.output, args.subject_info_json,
        args.start_date, args.end_date, args.search_date,
        args.order_by_sim, args.include_content_keyword,
        args.count_per_page, args.max_search_page, args.min_image_count
    )

    subject_info = load_subject_info(subject_info_json)

    if search_date:
        search_dates = [search_date]
    elif start_date and end_date:
        search_dates = [today] if not start_date or not end_date else list(date_range(start_date, end_date))
    else:
        search_dates = None

    if search_dates:
        date_strings = ', '.join([d.strftime('%Y-%m-%d') for d in search_dates])
        logging.info(f"검색 기준 날짜: {date_strings}")

    logging.info(f"Output Directory Path: {output_directory_path}")

    if order_by_sim:
        logging.info(f"Order by Similar Enabled (Max Search Page: {max_search_page})")

    if search_dates:
        for subject in subject_info:
            for search_date in search_dates:
                formatted_date = search_date.strftime('%Y-%m-%d')
                output_path = str(os.path.join(output_directory_path, subject["name"], formatted_date))
                subject_instance = Subject(
                    name=subject["name"],
                    keywords=subject["keywords"],
                    search_date=search_date,
                    output_path=output_path,
                    count_per_page=count_per_page,
                    include_content_keyword=include_content_keyword,
                    order_by_sim=order_by_sim,
                    max_search_page=max_search_page,
                    min_image_count=min_image_count
                )
                subject_instance.run()
    else:
        today_formatted = date.today().strftime('%Y-%m-%d')
        for subject in subject_info:
            output_path = str(os.path.join(output_directory_path, subject["name"], f"(INF) {today_formatted}"))
            subject_instance = Subject(
                name=subject["name"],
                keywords=subject["keywords"],
                search_date=None,
                output_path=output_path,
                count_per_page=count_per_page,
                include_content_keyword=include_content_keyword,
                order_by_sim=order_by_sim,
                max_search_page=max_search_page,
                min_image_count=min_image_count
            )
            subject_instance.run()
