import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import numpy as np

# -----------------------------------------------------------
# 1. 한글 폰트 설정 (사용자 환경에 맞게 수정 필요)
# -----------------------------------------------------------
# Windows: 'Malgun Gothic', Mac: 'AppleGothic'
plt.rcParams['font.family'] = 'Malgun Gothic' 
plt.rcParams['axes.unicode_minus'] = False

# -----------------------------------------------------------
# 2. 데이터 로드 및 전처리
# -----------------------------------------------------------
# (1) 업로드된 최근 데이터 로드
file_path = "고용노동부_산업재해 중대산업사고 발생 사업장_20241219.csv"
try:
    df_recent = pd.read_csv(file_path, encoding='cp949')
except:
    df_recent = pd.read_csv(file_path, encoding='utf-8')

# 사고 유형 분류 함수
def classify_accident(text):
    if '화재' in text: return '화재 (Fire)'
    elif '폭발' in text: return '폭발 (Explosion)'
    elif '누출' in text or '비산' in text: return '누출 (Leakage)'
    elif '질식' in text or '중독' in text: return '질식/중독'
    else: return '기타'

df_recent['유형'] = df_recent['사고 내용'].apply(classify_accident)
df_recent['지역'] = df_recent['사업장 소재지'].apply(lambda x: x.split()[0])

# (2) 역사적 데이터 (구미 사고 이후 추이 - 환경부 통계 재구성)
data_history = {
    '연도': [2012, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
    '사고건수': [13, 105, 113, 78, 87, 66, 57, 51],
    '비고': ['구미사고', '신고의무화', '법시행', '감소세', '감소세', '감소세', '감소세', '안정화']
}
df_history = pd.DataFrame(data_history)

# -----------------------------------------------------------
# 3. 종합 대시보드 시각화
# -----------------------------------------------------------
fig = plt.figure(figsize=(18, 10))
gs = fig.add_gridspec(2, 2)

# [Chart 1] 정책 효과 분석 (Line Chart)
ax1 = fig.add_subplot(gs[0, :]) # Top full width
sns.lineplot(data=df_history, x='연도', y='사고건수', marker='o', linewidth=3, color='#1f77b4', ax=ax1)
ax1.axvline(x=2015, color='red', linestyle='--', label='화관법/화평법 시행 (2015)')
ax1.text(2012.2, 20, '구미 불산사고(2012)', color='red', fontweight='bold')
ax1.set_title('📢 [History] 구미 사고 이후 법령 강화에 따른 화학사고 감소 추이 (2012~2020)', fontsize=15, fontweight='bold')
ax1.set_ylabel('연간 사고 건수')
ax1.legend()
ax1.grid(True, alpha=0.3)

# [Chart 2] 최근 3년(2021-2023) 사고 유형 (Pie Chart)
ax2 = fig.add_subplot(gs[1, 0])
type_counts = df_recent['유형'].value_counts()
colors = sns.color_palette('pastel')[0:len(type_counts)]
explode = [0.05 if i == 0 else 0 for i in range(len(type_counts))] # 1위 강조
ax2.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=140, colors=colors, explode=explode)
ax2.set_title('🔍 [Current Risk] 최근 3년 중대산업사고 유형 분석', fontsize=13, fontweight='bold')

# [Chart 3] 지역별 사고 발생 현황 (Bar Chart)
ax3 = fig.add_subplot(gs[1, 1])
region_counts = df_recent['지역'].value_counts()
sns.barplot(x=region_counts.index, y=region_counts.values, palette='Reds_r', ax=ax3)
ax3.set_title('📍 [Location] 사고 집중 발생 지역 (산단 중심)', fontsize=13, fontweight='bold')
ax3.set_ylabel('발생 건수')

plt.tight_layout()
plt.savefig('Safety_Analysis_Dashboard.png', dpi=300)
print("✅ 시각화 대시보드 저장 완료: Safety_Analysis_Dashboard.png")

# -----------------------------------------------------------
# 4. 브리핑 자료 자동 생성
# -----------------------------------------------------------
total_accidents = len(df_recent)
top_type = type_counts.idxmax()
top_type_pct = (type_counts.max() / total_accidents) * 100
top_region = region_counts.idxmax()

briefing_text = f"""
[ 📄 산업안전 데이터 분석 브리핑 ]
------------------------------------------------------------
1. 분석 개요
   - 대상: 고용노동부 중대산업사고 데이터 및 화학사고 추이
   - 목적: 구미 사고 이후 개선 효과 확인 및 현존 리스크 진단

2. 주요 성과 (Past ~ Now)
   - 2012년 구미 불산 누출 사고 이후 '화관법' 등 규제 강화로 
     화학사고 발생 건수는 2015년 대비 약 50% 수준으로 감소하며 안정화 추세임.

3. 현존 리스크 진단 (2021~2023 데이터 기준)
   - (유형) 현재 가장 위협적인 요소는 '{top_type}'로 전체의 {top_type_pct:.1f}%를 차지함.
   - (지역) '{top_region}' 등 주요 석유화학 산단이 위치한 지역에서 사고가 지속 발생 중.

4. 전문가 제언
   - 하드웨어적 설비 개선은 상당 부분 이루어졌으나, '{top_type}' 예방을 위한 
     지능형 감지 시스템(AI 센서 등) 도입이 시급함.
   - '{top_region}' 지역 산단에 대한 노후 설비 디지털 트윈 구축 권장.
------------------------------------------------------------
"""

print(briefing_text)

# 텍스트 파일로 저장
with open("Safety_Briefing.txt", "w", encoding='utf-8') as f:
    f.write(briefing_text)
print("✅ 브리핑 자료 저장 완료: Safety_Briefing.txt")