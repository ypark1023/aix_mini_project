# admin.py
from django.contrib import admin
from .models import Place, AgeRanking


# Place 상세 페이지 안에서 연령대별 순위를 바로 확인 및 수정할 수 있게 해주는 Inline 설정
class AgeRankingInline(admin.TabularInline):
    model = AgeRanking
    extra = 0  # 기본으로 빈 줄 추가 안 함
    ordering = ['age_group', 'rank']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    """관광지 기본 정보 관리자 설정"""
    # 목록 화면에 표시할 필드들
    list_display = ('name', 'sigungu', 'category', 'region_code', 'latitude', 'longitude')
    
    # 클릭 시 상세 페이지로 이동할 필드
    list_display_links = ('name',)
    
    # 우측 필터 옵션
    list_filter = ('region_code', 'category', 'sigungu')
    
    # 검색창 검색 가능 필드
    search_fields = ('name', 'sigungu', 'place_id')
    
    # 페이지당 표시 수
    list_per_page = 20
    
    # Place 상세 보기 화면 하단에 연령대별 순위(AgeRanking) 표를 함께 표시
    inlines = [AgeRankingInline]


@admin.register(AgeRanking)
class AgeRankingAdmin(admin.ModelAdmin):
    """연령대별 순위 관리자 설정"""
    list_display = ('get_place_name', 'get_sigungu', 'age_group', 'rank', 'ratio')
    list_filter = ('age_group', 'rank', 'place__region_code', 'place__category')
    search_fields = ('place__name', 'place__sigungu')
    list_per_page = 25
    ordering = ('age_group', 'rank')

    # FK로 연결된 Place 모델의 속성을 목록에 출력하기 위한 커스텀 메서드
    @admin.display(description='관광지명', ordering='place__name')
    def get_place_name(self, obj):
        return obj.place.name

    @admin.display(description='시군구', ordering='place__sigungu')
    def get_sigungu(self, obj):
        return obj.place.sigungu