# models.py
from django.db import models

class Place(models.Model):
    """관광지 기본 정보 테이블"""
    place_id = models.CharField(max_length=64, primary_key=True, verbose_name="관광지ID")
    region_code = models.CharField(max_length=20, verbose_name="지역코드")
    sigungu = models.CharField(max_length=50, verbose_name="시군구")
    name = models.CharField(max_length=100, verbose_name="관심지점명")
    category = models.CharField(max_length=50, verbose_name="구분")
    latitude = models.FloatField(verbose_name="위도")
    longitude = models.FloatField(verbose_name="경도")

    class Meta:
        verbose_name = "관광지"
        verbose_name_plural = "관광지 목록"

    def __str__(self):
        return f"[{self.sigungu}] {self.name}"


class AgeRanking(models.Model):
    """연령대별 순위 및 비율 정보 테이블"""
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="rankings", verbose_name="관광지")
    age_group = models.IntegerField(verbose_name="연령대")  # 20, 30, 40, 50, 60
    rank = models.IntegerField(verbose_name="순위")
    ratio = models.FloatField(verbose_name="비율")

    class Meta:
        verbose_name = "연령대별 순위"
        verbose_name_plural = "연령대별 순위 목록"
        unique_together = ('place', 'age_group')  # 특정 관광지-연령대 조합 중복 방지
        ordering = ['age_group', 'rank']

    def __str__(self):
        return f"{self.age_group}대 {self.rank}위 - {self.place.name} ({self.ratio}%)"