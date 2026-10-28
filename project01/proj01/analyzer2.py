import urllib.request
import urllib.parse
import json
import re
import ssl
from collections import Counter

# 1. 네이버 클라우드 플랫폼(NCP) 인증 키
CLIENT_ID = "uej2r8ufx1".strip()       # X-NCP-APIGW-API-KEY-ID
CLIENT_SECRET = "M4F9FilXUNPNHSrYjZSyz3p6ld9UkxHemyoI7tZa".strip() # X-NCP-APIGW-API-KEY

# 전체 검색 엔드포인트 정의
ENDPOINTS = {
    "블로그(Blog)": "https://naverapihub.apigw.ntruss.com/search/v1/blog",
    "뉴스(News)": "https://naverapihub.apigw.ntruss.com/search/v1/news",
    "웹문서(Web)": "https://naverapihub.apigw.ntruss.com/search/v1/webkr",
    "카페(Cafe)": "https://naverapihub.apigw.ntruss.com/search/v1/cafearticle"
}

def search_ncp_all_channels(query, display_per_channel=50):
    """
    4개 채널(블로그, 뉴스, 웹문서, 카페) 데이터를 통합 수집
    """
    all_documents = []
    channel_counts = {}
    context = ssl._create_unverified_context()
    
    for ch_name, endpoint in ENDPOINTS.items():
        params = urllib.parse.urlencode({
            'query': query,
            'display': display_per_channel,
            'sort': 'sim'
        })
        url = f"{endpoint}?{params}"
        
        request = urllib.request.Request(url)
        request.add_header("X-NCP-APIGW-API-KEY-ID", CLIENT_ID)
        request.add_header("X-NCP-APIGW-API-KEY", CLIENT_SECRET)
        
        try:
            response = urllib.request.urlopen(request, context=context)
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                docs = []
                for item in data.get('items', []):
                    clean_title = re.sub(r'<[^>]+>|&[a-zA-Z]+;', ' ', item.get('title', ''))
                    clean_description = re.sub(r'<[^>]+>|&[a-zA-Z]+;', ' ', item.get('description', ''))
                    docs.append(f"{clean_title} {clean_description}")
                
                all_documents.extend(docs)
                channel_counts[ch_name] = len(docs)
        except Exception as e:
            print(f"⚠️ [{ch_name}] 수집 중 예외 발생: {e}")
            
    return all_documents, channel_counts

# 2. '봉은사' 멀티 채널 원문 수집 실행
target_place = "봉은사"
print(f"🔍 '{target_place}' 키워드로 4개 채널(블로그, 뉴스, 웹문서, 카페) 원문을 수집합니다...")
docs, counts = search_ncp_all_channels(target_place, display_per_channel=50)

print("\n📊 채널별 수집 건수:")
for ch, count in counts.items():
    print(f"   - {ch}: {count}건")
print(f"✅ 총 {len(docs)}개 통합 데이터 수집 완료!\n")

# 3. 보완된 역추적 분석 함수 (부분 일치 'in' 적용)
def analyze_cooccurrence_improved(documents, target_word, top_n=5):
    co_words = []
    ngram_pairs = []
    
    stopwords = {'봉은사', '등', '및', '수', '것', '이', '가', '은', '는', '에', '와', '과', '으로', '로', '에서', '하여', '있는', '입니다', '하고'}
    
    for doc in documents:
        # 문장/문단에 타겟 키워드가 포함된 경우 탐색
        if target_word in doc:
            words = [w for w in re.findall(r'\b[가-힣]{2,}\b', doc) if w not in stopwords]
            
            # 1) 동시 출현어 (부분 일치 제외 처리)
            for w in words:
                if target_word not in w:
                    co_words.append(w)
            
            # 2) Target Word 전후 어휘 조합 (부분 일치 적용)
            for i, w in enumerate(words):
                if target_word in w: # Exact Match 대신 부분 일치 적용!
                    if i > 0:
                        ngram_pairs.append((words[i-1], w))
                    if i < len(words) - 1:
                        ngram_pairs.append((w, words[i+1]))

    return Counter(co_words).most_common(top_n), Counter(ngram_pairs).most_common(top_n)

# 4. 봉은사 주요 연관어 멀티 채널 역추적 분석 실행
target_keywords = ['성종', '선릉', '시간', '역사', '넷째']

if docs:
    for kw in target_keywords:
        print(f"==========================================")
        print(f"🔎 타겟 연관 키워드: [{kw}] 멀티 채널 역추적 결과")
        print(f"==========================================")
        
        top_co, top_ngram = analyze_cooccurrence_improved(docs, kw, top_n=5)
        
        print(f"📌 [{kw}] 동시 출현어 Top 5:")
        if top_co:
            for word, count in top_co:
                print(f"   - {word}: {count}회")
        else:
            print("   - 출현 데이터 없음")
            
        print(f"\n📌 [{kw}] 주변 N-gram 문맥 조합 Top 5:")
        if top_ngram:
            for pair, count in top_ngram:
                print(f"   - {' + '.join(pair)}: {count}회")
        else:
            print("   - 문맥 조합 없음")
        print("\n")
else:
    print("⚠️ 수집된 데이터가 없습니다. NCP Client Key를 확인해 주세요.")