import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform

# -----------------------------------------------------------
# 1. 페이지 및 폰트 설정
# -----------------------------------------------------------
st.set_page_config(page_title="산업안전 데이터 분석", layout="wide")

# 한글 폰트 설정 (OS별 자동 대응)
system_name = platform.system()
if system_name == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif system_name == 'Darwin':  # Mac
    plt.rc('font', family='AppleGothic')
else:
    # 리눅스/코랩 등 (나눔고딕 설치 필요할 수 있음)
    plt.rc('font', family='NanumGothic')

plt.rcParams['axes.unicode_minus'] = False

# -----------------------------------------------------------
# 2. 데이터 로드 (캐싱 적용으로 속도 향상)
# -----------------------------------------------------------
@st.cache_data
def load_data():
    # 실제 파일 경로에 맞게 수정해주세요. 같은 폴더에 파일이 있어야 합니다.
    file_path = "고용노동부_산업재해 중대산업사고 발생 사업장_20241219.csv"
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except:
        df = pd.read_csv(file_path, encoding='utf-8')
    
    # 전처리
    def classify_accident(text):
        if '화재' in text: return '화재 (Fire)'
        elif '폭발' in text: return '폭발 (Explosion)'
        elif '누출' in text or '비산' in text: return '누출 (Leakage)'
        elif '질식' in text or '중독' in text: return '질식/중독'
        else: return '기타'

    df['유형'] = df['사고 내용'].apply(classify_accident)
    df['지역'] = df['사업장 소재지'].apply(lambda x: x.split()[0])
    return df

@st.cache_data
def load_history_data():
    data_history = {
        '연도': [2012, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
        '사고건수': [13, 105, 113, 78, 87, 66, 57, 51],
        '비고': ['구미사고', '신고의무화', '법시행', '감소세', '감소세', '감소세', '감소세', '안정화']
    }
    return pd.DataFrame(data_history)

# -----------------------------------------------------------
# 3. 메인 대시보드 UI
# -----------------------------------------------------------
st.title("📊 대한민국 산업안전 데이터 분석 대시보드")
st.markdown("---")

# 데이터 로드 시도
try:
    df_recent = load_data()
    df_history = load_history_data()
except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. 같은 폴더에 '고용노동부_산업재해...' 파일을 넣어주세요.")
    st.stop()

# 탭 구성 (분석 리포트 / 시각화 / 원본 데이터)
tab1, tab2, tab3 = st.tabs(["📈 분석 리포트 & 요약", "📊 상세 차트", "강원 데이터 원본"])

with tab1:
    st.header("1. 구미 불산사고 이후 개선 효과 분석")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 정책 효과 그래프
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df_history, x='연도', y='사고건수', marker='o', linewidth=3, color='#1f77b4', ax=ax1)
        ax1.axvline(x=2015, color='red', linestyle='--', label='화관법 시행(2015)')
        ax1.text(2012.2, 20, '구미사고(2012)', color='red', fontweight='bold')
        ax1.set_title('연도별 화학사고 발생 추이 (2012~2020)')
        ax1.grid(True, alpha=0.3)
        st.pyplot(fig1) # plt.show() 대신 사용

    with col2:
        st.info("""
        **💡 핵심 인사이트**
        
        * **개선 효과**: 2015년 화관법 시행 이후 사고 건수가 **50% 이상 감소**하며 안정화 추세.
        * **현재 상황**: 제도적 정착은 완료되었으나, 노후 산단 중심으로 새로운 리스크 발생 중.
        """)

    st.markdown("---")
    
    st.header("2. 최근 3년(2021~2023) 주요 리스크 진단")
    # 브리핑 텍스트 생성 로직
    top_type = df_recent['유형'].value_counts().idxmax()
    top_type_pct = (df_recent['유형'].value_counts().max() / len(df_recent)) * 100
    top_region = df_recent['지역'].value_counts().idxmax()

    st.success(f"""
    **🔍 데이터 분석 브리핑**
    
    1. **최대 위험 요인**: 최근 3년간 가장 빈번한 사고는 **'{top_type}'**로 전체의 **{top_type_pct:.1f}%**를 차지합니다.
    2. **집중 발생 지역**: **'{top_region}'** 등 석유화학 단지 밀집 지역에서 사고가 집중되고 있습니다.
    3. **제언**: 누출보다 '화재' 비중이 높아짐에 따라, **지능형 화재 감지 센서** 도입이 시급합니다.
    """)

with tab2:
    st.subheader("최근 사고 상세 분석 시각화")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**📌 사고 유형별 분포**")
        fig2, ax2 = plt.subplots()
        type_counts = df_recent['유형'].value_counts()
        colors = sns.color_palette('pastel')[0:len(type_counts)]
        ax2.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
        st.pyplot(fig2)
        
    with col_b:
        st.markdown("**📌 지역별 사고 발생 건수**")
        fig3, ax3 = plt.subplots()
        region_counts = df_recent['지역'].value_counts()
        sns.barplot(x=region_counts.index, y=region_counts.values, palette='Reds_r', ax=ax3)
        ax3.set_ylabel("발생 건수")
        st.pyplot(fig3)

with tab3:
    st.subheader("📂 분석에 사용된 원본 데이터")
    st.dataframe(df_recent)