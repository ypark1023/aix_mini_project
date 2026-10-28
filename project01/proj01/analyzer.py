import json
import re
import time
import requests
import pandas as pd
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import CountVectorizer

# ==============================================================================
# 1. NAVER API HUB 인증 정보 및 공식 Endpoints
# ==============================================================================
CLIENT_ID = "uej2r8ufx1".strip()       # X-NCP-APIGW-API-KEY-ID
CLIENT_SECRET = "M4F9FilXUNPNHSrYjZSyz3p6ld9UkxHemyoI7tZa".strip() # X-NCP-APIGW-API-KEY

ENDPOINTS = {
    "blog": "https://naverapihub.apigw.ntruss.com/search/v1/blog",
    "news": "https://naverapihub.apigw.ntruss.com/search/v1/news",
    "webkr": "https://naverapihub.apigw.ntruss.com/search/v1/webkr",
    "cafearticle": "https://naverapihub.apigw.ntruss.com/search/v1/cafearticle",
    "trend": "https://naverapihub.apigw.ntruss.com/search-trend/v1/search"
}

HEADERS_GET = {
    "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
    "X-NCP-APIGW-API-KEY": CLIENT_SECRET
}

HEADERS_POST = {
    "X-NCP-APIGW-API-KEY-ID": CLIENT_ID,
    "X-NCP-APIGW-API-KEY": CLIENT_SECRET,
    "Content-Type": "application/json"
}

kiwi = Kiwi()

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text) if text else ''

# ==============================================================================
# 2. 분석 대상 20개 서울 장소 목록
# ==============================================================================
PLACES = [
    {"name": "봉은사", "district": "강남구", "category": "종교"},
    {"name": "코엑스", "district": "강남구", "category": "문화생활시설"},
    {"name": "서울식물원", "district": "강서구", "category": "관광명소"},
    {"name": "뚝섬한강공원", "district": "광진구", "category": "관광명소"},
    {"name": "어린이대공원", "district": "광진구", "category": "레저/스포츠"},
    {"name": "망원한강공원", "district": "마포구", "category": "관광명소"},
    {"name": "서울월드컵경기장", "district": "마포구", "category": "레저/스포츠"},
    {"name": "하늘공원", "district": "마포구", "category": "관광명소"},
    {"name": "반포한강공원", "district": "서초구", "category": "관광명소"},
    {"name": "예술의전당", "district": "서초구", "category": "문화생활시설"},
    {"name": "헌릉과인릉", "district": "서초구", "category": "관광명소"},
    {"name": "서울숲", "district": "성동구", "category": "관광명소"},
    {"name": "롯데월드잠실점", "district": "송파구", "category": "레저/스포츠"},
    {"name": "올림픽공원", "district": "송파구", "category": "관광명소"},
    {"name": "여의도한강공원", "district": "영등포구", "category": "관광명소"},
    {"name": "CGV용산아이파크몰", "district": "용산구", "category": "문화생활시설"},
    {"name": "국립중앙박물관", "district": "용산구", "category": "문화생활시설"},
    {"name": "노들섬", "district": "용산구", "category": "관광명소"},
    {"name": "경복궁", "district": "종로구", "category": "관광명소"},
    {"name": "팔각정북악스카이", "district": "종로구", "category": "관광명소"}
]

# ==============================================================================
# 3. 4채널 수집 및 30개 연관어 추출 함수 (자기 자신 제외)
# ==============================================================================
def get_integrated_keywords(place_name, target_year_month="202510", top_n=30):
    combined_texts = []

    # 1) 블로그
    res_blog = requests.get(ENDPOINTS["blog"], headers=HEADERS_GET, params={"query": f"{place_name} 2025년 10월", "display": 100, "sort": "date"})
    if res_blog.status_code == 200:
        for item in res_blog.json().get('items', []):
            if item.get('postdate', '').startswith(target_year_month):
                combined_texts.append(f"{clean_html(item['title'])} {clean_html(item['description'])}")

    # 2) 뉴스
    res_news = requests.get(ENDPOINTS["news"], headers=HEADERS_GET, params={"query": place_name, "display": 100, "sort": "date"})
    if res_news.status_code == 200:
        for item in res_news.json().get('items', []):
            pub_date = item.get('pubDate', '')
            if 'Oct 2025' in pub_date or '10 Oct 2025' in pub_date:
                combined_texts.append(f"{clean_html(item['title'])} {clean_html(item['description'])}")

    # 3) 웹문서
    res_web = requests.get(ENDPOINTS["webkr"], headers=HEADERS_GET, params={"query": place_name, "display": 50})
    if res_web.status_code == 200:
        for item in res_web.json().get('items', []):
            combined_texts.append(f"{clean_html(item['title'])} {clean_html(item['description'])}")

    # 4) 카페글
    res_cafe = requests.get(ENDPOINTS["cafearticle"], headers=HEADERS_GET, params={"query": f"{place_name} 2025년 10월", "display": 100, "sort": "date"})
    if res_cafe.status_code == 200:
        for item in res_cafe.json().get('items', []):
            combined_texts.append(f"{clean_html(item['title'])} {clean_html(item['description'])}")

    if not combined_texts:
        return []

    # 형태소 분석 및 불용어 제거
    full_corpus = " ".join(combined_texts)
    tokens = kiwi.tokenize(full_corpus)
    stopwords = ["2025년", "10월", "블로그", "포스팅", "뉴스", "기사", "카페", "글", "오늘", "다녀옴", "위치", "방문", "후기", "서울", "여행", "사진", "일상", "관련", "안내", place_name]
    
    nouns = [t.form for t in tokens if t.tag.startswith('N') and len(t.form) > 1 and t.form not in stopwords]

    if not nouns:
        return []

    actual_top_n = min(top_n, len(set(nouns)))
    vectorizer = CountVectorizer(max_features=actual_top_n)
    vectorizer.fit_transform([" ".join(nouns)])
    return list(vectorizer.get_feature_names_out())

# ==============================================================================
# 4. 앵커(Anchor) 키워드 보정 기반 통일 스케일 가중치 분석 함수
# ==============================================================================
def analyze_scaled_trend_weights(candidate_words):
    if not candidate_words:
        return {}

    # 1차 예비 수집 (첫 5개 중 최강 앵커 키워드 선정)
    anchor_chunk = candidate_words[:5]
    keyword_groups = [{"groupName": word, "keywords": [word]} for word in anchor_chunk]
    
    body = {
        "startDate": "2025-10-01",
        "endDate": "2025-10-31",
        "timeUnit": "month",
        "keywordGroups": keyword_groups
    }
    
    res = requests.post(ENDPOINTS["trend"], headers=HEADERS_POST, data=json.dumps(body))
    if res.status_code != 200:
        return {}
        
    first_results = res.json().get('results', [])
    if not first_results:
        return {}

    # 첫 묶음 중 가장 Ratio가 높은 단어를 전체 절대 기준점(Anchor)으로 설정
    anchor_word = None
    max_ratio = -1.0
    initial_ratios = {}

    for g in first_results:
        title = g['title']
        ratio = g['data'][0]['ratio'] if g['data'] else 0.0
        initial_ratios[title] = ratio
        if ratio > max_ratio:
            max_ratio = ratio
            anchor_word = title

    # 전체 통일 스케일 결과를 담을 디렉토리
    scaled_results = {anchor_word: 100.0}

    # 나머지 29개 단어를 4개씩 나누어, 앵커 키워드(1개)와 함께 요청 (총 5개 그룹)
    remaining_words = [w for w in candidate_words if w != anchor_word]
    chunks = [remaining_words[i:i + 4] for i in range(0, len(remaining_words), 4)]

    for chunk in chunks:
        # 모든 요청에 anchor_word를 필수 포함
        current_groups = [{"groupName": anchor_word, "keywords": [anchor_word]}]
        for word in chunk:
            current_groups.append({"groupName": word, "keywords": [word]})

        req_body = {
            "startDate": "2025-10-01",
            "endDate": "2025-10-31",
            "timeUnit": "month",
            "keywordGroups": current_groups
        }

        res_chunk = requests.post(ENDPOINTS["trend"], headers=HEADERS_POST, data=json.dumps(req_body))
        
        if res_chunk.status_code == 200:
            c_results = res_chunk.json().get('results', [])
            
            # 현재 묶음 내 앵커 키워드의 Ratio 찾기
            chunk_anchor_ratio = 1.0
            for g in c_results:
                if g['title'] == anchor_word:
                    chunk_anchor_ratio = g['data'][0]['ratio'] if g['data'] else 1.0
                    break

            # 앵커 키워드(=100) 기준으로 비례 보정 계산
            for g in c_results:
                title = g['title']
                if title == anchor_word:
                    continue
                raw_ratio = g['data'][0]['ratio'] if g['data'] else 0.0
                # 보정 공식 적용
                normalized_ratio = (raw_ratio / chunk_anchor_ratio) * 100.0 if chunk_anchor_ratio > 0 else 0.0
                scaled_results[title] = round(normalized_ratio, 2)

    return scaled_results

# ==============================================================================
# 5. 메인 실행 및 CSV 저장
# ==============================================================================
if __name__ == "__main__":
    all_data_rows = []
    
    print("🚀 서울시 주요 20개 장소 2025년 10월 연관어 수집 & 절대 통일 가중치 분석 시작...\n")
    
    for idx, place in enumerate(PLACES, 1):
        p_name = place["name"]
        p_district = place["district"]
        p_category = place["category"]
        
        print(f"[{idx}/20] '{p_name}' ({p_district} | {p_category}) 분석 중...")
        
        # 1) 30개 연관어 수집
        keywords = get_integrated_keywords(p_name, target_year_month="202510", top_n=30)
        
        if not keywords:
            print(f"  ⚠️ '{p_name}' 데이터 부족으로 스킵")
            continue
            
        # 2) 앵커 보정 통일 가중치 계산
        scaled_ratios = analyze_scaled_trend_weights(keywords)
        
        # 3) 가중치 기준 내림차순 정렬
        sorted_keywords = sorted(scaled_ratios.items(), key=lambda x: x[1], reverse=True)
        
        # 4) 행 데이터 축적
        for rank, (word, ratio) in enumerate(sorted_keywords, 1):
            all_data_rows.append({
                "장소명": p_name,
                "자치구": p_district,
                "구분": p_category,
                "순위": rank,
                "연관 키워드": word,
                "통일 가중치(Ratio)": ratio
            })
            
        print(f"  └> 1위 기준(100.0) 보정 완료! 총 {len(sorted_keywords)}개 수집됨.")
        time.sleep(0.5)

    # 6. CSV 파일 저장
    if all_data_rows:
        df_result = pd.DataFrame(all_data_rows)
        file_name = "seoul_places_keywords_202510_scaled.csv"
        df_result.to_csv(file_name, index=False, encoding="utf-8-sig")
        
        print(f"\n🎉 모든 작업이 끝났습니다! 결과 파일: '{file_name}'")
        print(f"생성된 총 데이터 행 수: {len(df_result)}행")