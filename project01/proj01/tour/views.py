from django.shortcuts import render
from django.http import JsonResponse
from .models import Place, AgeRanking
import json

def gw_list10(request):
    # 1. 강원도(gw)의 모든 관광지 정보 가져오기
    gw_places = Place.objects.filter(region_code='gw')
    
    # JavaScript에서 바로 사용할 placeData 객체 구성
    place_data_dict = {}
    for place in gw_places:
        # 관광지 이미지 파일명 예시: 관광지명.jpg (없으면 default.jpg 사용)
        # 로컬 폴더: static/images/allimg/강원도/
        image_url = f"/static/images/gw/{place.name}.jpg"
        
        place_data_dict[place.place_id] = {
            "id": place.place_id,
            "name": place.name,
            "sigungu": place.sigungu,
            "category": place.category,
            "lat": place.latitude,
            "lng": place.longitude,
            "img": image_url,
            "location": f"강원특별자치도 {place.sigungu} {place.name}",
            "desc": f"{place.name}은(는) 강원특별자치도 {place.sigungu}에 위치한 인기 {place.category}입니다.",
            "kmap": f"https://map.kakao.com/link/search/{place.name}",
            "nmap": f"https://map.naver.com/v5/search/{place.name}",
            "yt": "https://www.youtube.com/embed/2X_2Idri090?autoplay=1",  # 기본 영상
            "tags": [f"#{place.sigungu}여행", f"#{place.name}", f"#{place.category}"],
            "tip": "시즌별 운영 시간과 주차 가능 여부를 방문 전 체크해보세요!"
        }

    # 2. 연령대별 TOP 10 데이터 쿼리
    age_groups = [20, 30, 40, 50, 60]
    age_filter_datasets = {
        "all": [],
        "20s": [],
        "30s": [],
        "40s": [],
        "50s": [],
        "60s": []
    }

    # 전체(all): 20대 기준 1~10위 우선 할당 또는 전체 순위
    all_rankings = AgeRanking.objects.filter(place__region_code='gw', age_group=20).order_by('rank')[:10]
    for r in all_rankings:
        age_filter_datasets["all"].append({
            "id": r.place.place_id,
            "name": r.place.name,
            "category": r.place.category,
            "location": f"강원 {r.place.sigungu}",
            "count": f"{r.rank}위 ({r.ratio}%)",
            "rank": r.rank
        })

    # 각 연령대별 TOP 10
    key_map = {20: '20s', 30: '30s', 40: '40s', 50: '50s', 60: '60s'}
    for age in age_groups:
        rankings = AgeRanking.objects.filter(place__region_code='gw', age_group=age).order_by('rank')[:10]
        key = key_map[age]
        for r in rankings:
            age_filter_datasets[key].append({
                "id": r.place.place_id,
                "name": r.place.name,
                "category": r.place.category,
                "location": f"강원 {r.place.sigungu}",
                "count": f"{r.ratio}%",
                "rank": r.rank
            })

    context = {
        'place_data_json': json.dumps(place_data_dict, ensure_ascii=False),
        'age_datasets_json': json.dumps(age_filter_datasets, ensure_ascii=False),
    }
    return render(request, 'gw_list10.html', context)