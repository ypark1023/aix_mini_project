# import_data.py
import glob
import os
import django
import pandas as pd

# 1. Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj01.settings")
django.setup()

from tour.models import AgeRanking, Place

def run_import():
    # 현재 script 파일이 있는 폴더 위치를 절대 경로로 취득 (터미널 위치 상관없이 동작!)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_pattern = os.path.join(base_dir, "total_*_corrected.csv")
    
    file_list = sorted(glob.glob(file_pattern))
    print(f"🔍 탐색된 CSV 파일 ({len(file_list)}개): {file_list}")

    if not file_list:
        print("❌ CSV 파일을 찾지 못했습니다. 파일 이름을 확인하세요.")
        return

    place_count = 0
    ranking_count = 0

    for file_path in file_list:
        print(f"📖 읽는 중: {os.path.basename(file_path)}...")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')

        for _, row in df.iterrows():
            # NumPy 타입을 Python 기본 타입(str, float, int)으로 변환
            p_id = str(row["관광지ID"]).strip()
            r_code = str(row["지역코드"]).strip()
            sigungu_val = str(row["시군구"]).strip()
            name_val = str(row["관심지점명"]).strip()
            cat_val = str(row["구분"]).strip()
            lat_val = float(row["위도"])
            lng_val = float(row["경도"])
            
            age_val = int(row["연령대"])
            rank_val = int(row["순위"])
            ratio_val = float(row["비율"])

            # Place 생성 또는 가져오기
            place, created = Place.objects.get_or_create(
                place_id=p_id,
                defaults={
                    "region_code": r_code,
                    "sigungu": sigungu_val,
                    "name": name_val,
                    "category": cat_val,
                    "latitude": lat_val,
                    "longitude": lng_val,
                }
            )
            if created:
                place_count += 1

            # AgeRanking 생성 또는 업데이트
            _, r_created = AgeRanking.objects.update_or_create(
                place=place,
                age_group=age_val,
                defaults={"rank": rank_val, "ratio": ratio_val}
            )
            if r_created:
                ranking_count += 1

    print("\n==========================================")
    print(f"🎉 DB 입고 완료!")
    print(f" - 새로 등록된 Place: {place_count}개 (전체: {Place.objects.count()}개)")
    print(f" - 새로 등록된 AgeRanking: {ranking_count}개 (전체: {AgeRanking.objects.count()}개)")
    print("==========================================")

if __name__ == "__main__":
    run_import()