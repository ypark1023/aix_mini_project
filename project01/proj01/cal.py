import pandas as pd
import json

def process_dashboard_data():
    # 1. 기존 연령대별 비율 데이터 추출 함수
    def get_age_averages(filepath):
        df = pd.read_excel(filepath, header=3)
        region_col = df.columns[0]
        avg_cols = [col for col in df.columns if isinstance(col, str) and '전체 평균' in col]
        
        result = {}
        for _, row in df.iterrows():
            region = str(row[region_col]).strip()
            if pd.isna(region) or region in ['nan', '시군구', '전체 평균', 'None']:
                continue
                
            region_data = {}
            for col in avg_cols:
                age_group = col.split('\n')[0].strip()
                val = row[col]
                if pd.notna(val):
                    try:
                        region_data[age_group] = round(float(val), 1)
                    except ValueError:
                        pass
            if region_data:
                result[region] = region_data
        return result

    # 3개 지역 비율 데이터 불러오기
    all_data = {
        "서울": get_age_averages('서울시_연령별_월별배치_방문자_통합본.xlsx'),
        "경기": get_age_averages('경기_연령별_월별배치_12개월_통합본.xlsx'),
        "강원": get_age_averages('강원_연령별_월별배치_12개월_통합본.xlsx')
    }

    # 2. 전국 방문자 수 파일에서 데이터 읽기 (3번째 줄이 헤더)
    df_vis = pd.read_excel('전국_월별_기초지자체_방문자수_12개월_통합본.xlsx', header=2)
    
    # 엑셀의 광역지자체명을 우리가 설정한 키값으로 매핑
    sido_map = {
        '서울특별시': '서울',
        '경기도': '경기',
        '강원특별자치도': '강원'
    }
    
    # 3. 데이터 병합 (비율 데이터 객체 안에 '총방문자수' 추가)
    for _, row in df_vis.iterrows():
        sido = str(row['광역지자체명']).strip()
        sigungu = str(row['기초지자체명']).strip()
        
        # 서울, 경기, 강원 데이터만 처리
        if sido in sido_map:
            key_sido = sido_map[sido]
            
            # 12개월(인덱스 3~14) 방문자 수 합산
            monthly_vals = pd.to_numeric(row.iloc[3:15], errors='coerce').fillna(0)
            total_visitors = int(monthly_vals.sum())
            
            # 해당 시군구가 all_data에 존재하면 총방문자수 항목 추가
            if key_sido in all_data and sigungu in all_data[key_sido]:
                all_data[key_sido][sigungu]['총방문자수'] = total_visitors

    return all_data

# 실행 및 JSON 저장
final_data = process_dashboard_data()

with open('dashboard_final_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("데이터 병합 완료! dashboard_final_data.json 파일을 확인하세요.")