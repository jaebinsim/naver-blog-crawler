# Naver Blog Crawler
네이버 블로그 포스트에 포함된 원본 이미지를 저장하는 크롤러

## 지원기능
- 다중 키워드
- 특정 날짜에 업로드된 포스트만 검색
- 특정 기간동안 업로드된 포스팅만 검색
- 지정된 페이지 번호까지 정확도순으로 검색
- 지정된 페이지 번호까지 특정 날짜 또는 기간동안 업로드된 포스트만 정확도순으로 검색
- 이미 크롤링된 데이터가 있을 시, 새로 업로드된 포스트만 크롤링
- 크롤링된 포스트마다 제목, 글쓴이, 블로그명, 포스트 주소, 블로그 주소, 블로그 내 키워드 검색결과 주소 정보 제공

## Requirements
- Python 3.10+
- `pip install -r requirements.txt`

## 사용 방법
### subject_info.json 설명
```json
[
    {
        "name": 검색할 키워드의 주제명,
        "keywords": [
            검색어 키워드 1,
            검색어 키워드 2,
            검색어 키워드 3
        ]
    }
]
```
검색어 키워드 지정은 위와 같은 형식의 json 파일을 사용합니다.
실제로 검색되는 키워드는 위와 같이 n개로 지정할 수 있으며, 키워드의 주제명은 검색에 영향을 미치지 않습니다.

### 특정 날짜에 업로드된 포스트내에서 검색 (최신순 검색)
```bash
python NaverBlogCrawler.py --output <결과 저장 경로> --search_date <포스트 업로드 날짜> --subject_info_json <subject_info.json 파일 경로>
```

#### 매개변수
- `--output`: 크롤링 결과를 저장할 경로입니다.
- `--search_date`: 크롤링할 포스트가 업로드된 날짜를 `YYYY-MM-DD` 형식으로 지정합니다.
- `--subject_info_json`: `subject_info.json` 파일의 경로입니다.

#### 사용 예시
```bash
python NaverBlogCrawler.py --output ./results --search_date 2024-04-01 --subject_info_json ./subject_info.json
```

### 특정 기간동안 업로드된 포스트내에서 검색 (최신순 검색)
```bash
python NaverBlogCrawler.py --output <결과 저장 경로> --start_date <포스트 업로드 날짜 범위 시작> --end_date <포스트 업로드 날짜 범위 끝> --subject_info_json <subject_info.json 파일 경로>
```

#### 매개변수
- `--output`: 크롤링 결과를 저장할 경로입니다.
- `--start_date`: `YYYY-MM-DD` 형식으로 지정합니다.
- `--end_date`: `YYYY-MM-DD` 형식으로 지정합니다.
- `--subject_info_json`: `subject_info.json` 파일의 경로입니다.

#### 사용 예시
```bash
python NaverBlogCrawler.py --output ./results --start_date 2024-04-01 --end_date 2024-04-05 --subject_info_json ./subject_info.json
```

### 정확도순으로 검색
```bash
python NaverBlogCrawler.py --output <결과 저장 경로> --order_by_sim --max_search_page <최대 검색할 페이지 번호> --subject_info_json <subject_info.json 파일 경로>
```
정확도순으로 검색의 경우 포스트 업로드 날짜가 순차적이지 않아, 지정한 페이지 번호까지 전부 크롤링합니다

#### 매개변수
- `--output`: 크롤링 결과를 저장할 경로입니다.
- `--order_by_sim`: 정확도순으로 검색하도록 지정합니다.
- `--max_search_page`: 최대 검색할 페이지 번호를 지정합니다.
- `--search_date` (선택): `YYYY-MM-DD` 형식으로 지정합니다.
- `--start_date` (선택): `YYYY-MM-DD` 형식으로 지정합니다.
- `--end_date` (선택): `YYYY-MM-DD` 형식으로 지정합니다.
- `--subject_info_json`: `subject_info.json` 파일의 경로입니다.

#### 사용 예시
```bash
python NaverBlogCrawler.py --output ./results --order_by_sim --max_search_page 10 --subject_info_json ./subject_info.json
```

### 추가 매개변수
- `--count_per_page`: 한 페이지당 가져올 포스트의 개수를 지정합니다. (기본값: 1000)

## 크롤링 결과
### subject_info.json 예시
```json
[
    {
        "name": "일본 도쿄 여행",
        "keywords": [
            "도쿄 여행",
            "도쿄 맛집",
            "도쿄 볼거리"
        ]
    },
    {
        "name": "베트남 다낭 여행",
        "keywords": [
            "다낭 여행",
            "다낭 맛집",
            "다낭 볼거리"
        ]
    }
]
```
위와 같이 키워드 설정 시 "일본 도쿄 여행" 주제에서 검색에 사용되는 키워드는 "도쿄 여행", "도쿄 맛집", "도쿄 볼거리" 입니다.

마찬가지로 "베트남 다낭 여행" 주제의 경우 검색에 사용되는 키워드는 "다낭 여행", "다낭 맛집", "다낭 볼거리" 입니다.

### 사용 명령어
```bash
python NaverBlogCrawler.py --output ./results --start_date 2024-04-01 --end_date 2024-04-05 --subject_info_json ./subject_info.json
```

### "results" 디렉터리 내용

### "일본 도쿄 여행" 디렉터리 내용