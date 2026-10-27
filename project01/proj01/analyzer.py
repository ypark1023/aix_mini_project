import requests

# 새로 발급받은 키를 입력하세요
CLIENT_ID = ""
CLIENT_SECRET = ""

headers = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET
}

url = "https://openapi.naver.com/v1/search/blog.json?query=테스트&display=1"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ 성공! 네이버 API 인증에 성공했습니다.")
else:
    print(f"❌ 실패! 오류 코드: {response.status_code}")
    print("응답 내용:", response.text)