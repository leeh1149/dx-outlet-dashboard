import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import requests
import json

# 페이지 설정
st.set_page_config(
    page_title="DX OUTLET 매출 대시보드",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #667eea;
    }
    .section-header {
        color: #333;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🏪 DX OUTLET 매출 대시보드</h1>
    <p>실시간 데이터 분석 및 시각화</p>
</div>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    """CSV 파일을 자동으로 로드하고 전처리합니다."""
    try:
        # CSV 파일을 직접 로드
        df = pd.read_csv('DX OUTLET MS DB.csv')
        return df
    except FileNotFoundError:
        st.error("DX OUTLET MS DB.csv 파일을 찾을 수 없습니다. 파일이 같은 폴더에 있는지 확인해주세요.")
        return None
    except Exception as e:
        st.error(f"파일 로드 중 오류가 발생했습니다: {e}")
        return None

def format_to_hundred_million(value):
    """억원 단위로 변환합니다."""
    return f"{value / 100000000:.1f}억원"

def format_growth_with_color(growth):
    """전년비를 색상과 함께 표시합니다."""
    if growth > 0:
        return f"<span style='color: #0066cc; font-weight: bold;'>▲ {growth:+.1f}%</span>"
    elif growth < 0:
        return f"<span style='color: #cc0000; font-weight: bold;'>▼ {growth:+.1f}%</span>"
    else:
        return f"<span style='color: #666;'>0.0%</span>"

def format_efficiency_to_hundred_million(value):
    """평당 매출을 억원 단위로 변환합니다."""
    return f"{value / 100000000:.1f}억원/평"

def format_efficiency_to_million(value):
    """평당 매출을 백만원 단위로 변환합니다."""
    return f"{value / 1000000:.2f}백만원/평"

# AI 분석 함수들
def call_jemini_api(api_key, prompt):
    """재미나이 2.5 Flash API를 호출하는 함수"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "API 응답에서 내용을 찾을 수 없습니다."
        else:
            return f"API 호출 실패: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"API 호출 중 오류 발생: {str(e)}"

def analyze_outlet_trends(discovery_data, efficiency_data):
    """아울렛 동향 분석"""
    if discovery_data.empty:
        return "디스커버리 데이터가 없습니다."
    
    # 유통사별 매출 분석
    distributor_analysis = discovery_data.groupby('유통사').agg({
        '25SS': 'sum',
        '24SS': 'sum',
        '24FW': 'sum',
        '23FW': 'sum'
    }).reset_index()
    
    # 효율성 데이터 분석
    efficiency_analysis = ""
    if not efficiency_data.empty:
        top_efficiency = efficiency_data.head(3)
        efficiency_analysis = f"""
        **🏆 효율성 TOP 3 매장:**
        - {top_efficiency.iloc[0]['매장명']}: {top_efficiency.iloc[0]['평균효율성']:.1f}억원/평
        - {top_efficiency.iloc[1]['매장명']}: {top_efficiency.iloc[1]['평균효율성']:.1f}억원/평
        - {top_efficiency.iloc[2]['매장명']}: {top_efficiency.iloc[2]['평균효율성']:.1f}억원/평
        """
    
    analysis_text = f"""
    **📊 디스커버리 아울렛 동향 분석 데이터:**
    
    **유통사별 매출 현황:**
    {distributor_analysis.to_string(index=False)}
    
    {efficiency_analysis}
    
    **분석 요청사항:**
    1. 어떤 유통망에서 디스커버리가 매출이 잘 나오고 효율이 좋은지 분석해주세요
    2. 시즌별 매출 패턴과 유통사별 성과 차이를 설명해주세요
    3. 효율성이 높은 매장들의 공통점을 찾아주세요
    4. 개선 방안과 전략적 제안을 해주세요
    """
    
    return analysis_text

def analyze_peer_ms_status(brand_df):
    """동업계 MS 현황 분석"""
    if brand_df.empty:
        return "브랜드 데이터가 없습니다."
    
    # 디스커버리 성과 분석
    discovery_data = brand_df[brand_df['브랜드'] == '디스커버리']
    if discovery_data.empty:
        return "디스커버리 브랜드 데이터가 없습니다."
    
    # 상위 브랜드 분석
    top_brands = brand_df.head(5)
    
    analysis_text = f"""
    **🏢 동업계 MS 현황 분석 데이터:**
    
    **전체 브랜드 순위 (상위 5개):**
    {top_brands[['브랜드', '25SS', '24SS', 'SS_전년비']].to_string(index=False)}
    
    **디스커버리 성과:**
    - 25SS 매출: {discovery_data.iloc[0]['25SS']/100000000:.1f}억원
    - 24SS 매출: {discovery_data.iloc[0]['24SS']/100000000:.1f}억원
    - SS 전년비: {discovery_data.iloc[0]['SS_전년비']:+.1f}%
    
    **분석 요청사항:**
    1. 전년 대비 디스커버리 매출 추이를 분석해주세요
    2. 어떤 브랜드가 잘 나가고 있는지 경쟁사 분석을 해주세요
    3. 디스커버리의 시장 포지션과 경쟁력을 평가해주세요
    4. 시장 기회와 위협 요소를 분석해주세요
    5. 디스커버리 브랜드 강화 전략을 제안해주세요
    """
    
    return analysis_text

def calculate_efficiency_data(df):
    """디스커버리 브랜드의 효율성 데이터를 계산합니다."""
    # 디스커버리 브랜드만 필터링
    discovery_df = df[df['브랜드'] == '디스커버리'].copy()
    
    if discovery_df.empty:
        return pd.DataFrame()
    
    # 매장별 데이터 집계
    store_data = []
    for store_name in discovery_df['매장명'].unique():
        store_rows = discovery_df[discovery_df['매장명'] == store_name]
        
        # 매장 정보
        distributor = store_rows['유통사'].iloc[0]
        area_pyeong = store_rows['매장 면적'].iloc[0] if '매장 면적' in store_rows.columns else 0
        area = area_pyeong * 3.3058 if area_pyeong > 0 else 0  # 평을 평방미터로 변환
        
        # 디버깅 정보 (롯데아울렛이천 확인용)
        if '롯데아울렛이천' in store_name:
            st.write(f"🔍 디버깅: {store_name} - 매장면적: {area_pyeong}평, 평방미터: {area:.1f}㎡")
        
        # 시즌별 매출액 계산
        seasons = ['23SS', '23FW', '24SS', '24FW', '25SS']
        season_sales = {}
        season_efficiency = {}
        
        for season in seasons:
            sales = store_rows[season].sum() if season in store_rows.columns else 0
            season_sales[season] = sales
            season_efficiency[season] = sales / area_pyeong if area_pyeong > 0 else 0
        
        # 평균 효율성 계산
        valid_efficiencies = [eff for eff in season_efficiency.values() if eff > 0]
        avg_efficiency = np.mean(valid_efficiencies) if valid_efficiencies else 0
        
        store_data.append({
            '매장명': store_name,
            '유통사': distributor,
            '매장면적': area,  # 평방미터
            '매장면적_평': area_pyeong,  # 평 (원본 데이터)
            '평균효율성': avg_efficiency,
            **{f'{season}_매출액': season_sales[season] for season in seasons},
            **{f'{season}_효율성': season_efficiency[season] for season in seasons}
        })
    
    # DataFrame으로 변환하고 평균 효율성 기준으로 정렬
    efficiency_df = pd.DataFrame(store_data)
    efficiency_df = efficiency_df.sort_values('평균효율성', ascending=False).reset_index(drop=True)
    
    return efficiency_df

# 사이드바 - 데이터 상태
st.sidebar.header("📁 데이터 상태")

# 데이터 자동 로드
with st.spinner('데이터를 로드하는 중...'):
    df = load_data()

# 메인 컨텐츠
if df is not None:
    # 데이터 정보 표시
    st.sidebar.success(f"✅ 데이터 로드 완료: {len(df)}개 행")
    
    # 필터링 옵션
    st.sidebar.header("🔍 필터 옵션")
    
    # 유통사 필터
    distributors = ['전체'] + sorted(df['유통사'].unique().tolist())
    selected_distributor = st.sidebar.selectbox("유통사 선택", distributors)
    
    # 매장명 필터
    if selected_distributor != '전체':
        stores = ['전체'] + sorted(df[df['유통사'] == selected_distributor]['매장명'].unique().tolist())
    else:
        stores = ['전체'] + sorted(df['매장명'].unique().tolist())
    
    selected_store = st.sidebar.selectbox("매장명 선택", stores)
    
    # AI 분석 섹션
    st.sidebar.header("🤖 AI 분석")
    api_key = st.sidebar.text_input(
        "재미나이 API 키",
        type="password",
        help="Google AI Studio에서 발급받은 API 키를 입력하세요"
    )
    
    # AI 분석 버튼
    if api_key:
        analyze_outlet = st.sidebar.button("📊 아울렛 동향 AI 분석", key="analyze_outlet")
        analyze_peer = st.sidebar.button("🏢 동업계 MS 현황 AI 분석", key="analyze_peer")
    else:
        st.sidebar.info("🔑 API 키를 입력하면 AI 분석을 사용할 수 있습니다")
        analyze_outlet = False
        analyze_peer = False
    
    # 필터링된 데이터
    filtered_df = df.copy()
    if selected_distributor != '전체':
        filtered_df = filtered_df[filtered_df['유통사'] == selected_distributor]
    if selected_store != '전체':
        filtered_df = filtered_df[filtered_df['매장명'] == selected_store]
    
    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("선택된 유통사", selected_distributor)
    with col2:
        st.metric("선택된 매장", selected_store)
    with col3:
        st.metric("데이터 건수", len(filtered_df))
    with col4:
        discovery_count = len(filtered_df[filtered_df['브랜드'] == '디스커버리'])
        st.metric("디스커버리 건수", discovery_count)
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["🏪 아울렛 동향", "📊 매장 효율", "🤖 AI 분석"])
    
    with tab1:
            st.markdown('<h2 class="section-header">🏪 아울렛 동향</h2>', unsafe_allow_html=True)
            
            # 아울렛 매출 흐름 - 디스커버리
            st.subheader("📈 아울렛 매출 흐름 - 디스커버리")
            
            # 디스커버리 데이터만 필터링
            discovery_data = filtered_df[filtered_df['브랜드'] == '디스커버리']
            
            if not discovery_data.empty:
                # 유통사별 데이터 집계
                distributor_summary = []
                for distributor in discovery_data['유통사'].unique():
                    dist_data = discovery_data[discovery_data['유통사'] == distributor]
                    store_count = dist_data['매장명'].nunique()
                    
                    # 시즌별 매출 계산
                    seasons = ['23SS', '23FW', '24SS', '24FW', '25SS']
                    season_totals = {}
                    season_valid_stores = {}
                    
                    for season in seasons:
                        season_totals[season] = dist_data[season].sum()
                        # 0이 아닌 매장 수 계산 (평균 매출용)
                        season_valid_stores[season] = len(dist_data[dist_data[season] > 0])
                    
                    # SS 시즌 데이터
                    ss_2025 = season_totals['25SS']
                    ss_2024 = season_totals['24SS']
                    ss_growth = ((ss_2025 - ss_2024) / ss_2024 * 100) if ss_2024 > 0 else 0
                    
                    # FW 시즌 데이터
                    fw_2024 = season_totals['24FW']
                    fw_2023 = season_totals['23FW']
                    fw_growth = ((fw_2024 - fw_2023) / fw_2023 * 100) if fw_2023 > 0 else 0
                    
                    distributor_summary.append({
                        '유통사': distributor,
                        '매장수': store_count,
                        '25SS_총매출': ss_2025,
                        '24SS_총매출': ss_2024,
                        'SS_전년비': ss_growth,
                        '24FW_총매출': fw_2024,
                        '23FW_총매출': fw_2023,
                        'FW_전년비': fw_growth,
                        '25SS_평균매출': ss_2025 / season_valid_stores['25SS'] if season_valid_stores['25SS'] > 0 else 0,
                        '24SS_평균매출': ss_2024 / season_valid_stores['24SS'] if season_valid_stores['24SS'] > 0 else 0,
                        '24FW_평균매출': fw_2024 / season_valid_stores['24FW'] if season_valid_stores['24FW'] > 0 else 0,
                        '23FW_평균매출': fw_2023 / season_valid_stores['23FW'] if season_valid_stores['23FW'] > 0 else 0
                    })
                
                summary_df = pd.DataFrame(distributor_summary)
                
                # 시즌 선택
                season_type = st.radio("시즌 선택", ["SS 시즌", "FW 시즌"], horizontal=True)
                
                # 데이터 타입 선택 (총매출/평균매출)
                data_type = st.radio("데이터 타입 선택", ["총매출", "평균매출"], horizontal=True)
                
                if season_type == "SS 시즌":
                    # SS 시즌 차트
                    fig_ss = go.Figure()
                    
                    if data_type == "총매출":
                        fig_ss.add_trace(go.Bar(
                            name='25SS',
                            x=summary_df['유통사'],
                            y=summary_df['25SS_총매출'] / 100000000,
                            marker_color='#1f77b4'
                        ))
                        
                        fig_ss.add_trace(go.Bar(
                            name='24SS',
                            x=summary_df['유통사'],
                            y=summary_df['24SS_총매출'] / 100000000,
                            marker_color='#ff7f0e'
                        ))
                        
                        y_title = '총 매출 (억원)'
                        chart_title = '유통사별 디스커버리 SS 시즌 총 매출 비교'
                    else:  # 평균매출
                        fig_ss.add_trace(go.Bar(
                            name='25SS 평균',
                            x=summary_df['유통사'],
                            y=summary_df['25SS_평균매출'] / 100000000,
                            marker_color='#1f77b4'
                        ))
                        
                        fig_ss.add_trace(go.Bar(
                            name='24SS 평균',
                            x=summary_df['유통사'],
                            y=summary_df['24SS_평균매출'] / 100000000,
                            marker_color='#ff7f0e'
                        ))
                        
                        y_title = '평균 매출 (억원)'
                        chart_title = '유통사별 디스커버리 SS 시즌 평균 매출 비교'
                    
                    fig_ss.update_layout(
                        title=chart_title,
                        xaxis_title='유통사',
                        yaxis_title=y_title,
                        barmode='group',
                        height=500
                    )
                    
                    st.plotly_chart(fig_ss, use_container_width=True)
                    
                    # SS 시즌 요약 테이블
                    st.subheader("SS 시즌 요약")
                    
                    if data_type == "총매출":
                        ss_summary = summary_df[['유통사', '매장수', '25SS_총매출', '24SS_총매출', 'SS_전년비']].copy()
                        ss_summary['25SS_총매출'] = ss_summary['25SS_총매출'].apply(format_to_hundred_million)
                        ss_summary['24SS_총매출'] = ss_summary['24SS_총매출'].apply(format_to_hundred_million)
                        ss_summary.columns = ['유통사', '매장수', '25SS 총매출', '24SS 총매출', 'SS 전년비']
                    else:  # 평균매출
                        ss_summary = summary_df[['유통사', '매장수', '25SS_평균매출', '24SS_평균매출', 'SS_전년비']].copy()
                        ss_summary['25SS_평균매출'] = ss_summary['25SS_평균매출'].apply(format_to_hundred_million)
                        ss_summary['24SS_평균매출'] = ss_summary['24SS_평균매출'].apply(format_to_hundred_million)
                        ss_summary.columns = ['유통사', '매장수', '25SS 평균매출', '24SS 평균매출', 'SS 전년비']
                    
                    # 전년비 색상 표시를 위한 스타일링
                    def format_growth_with_color(growth):
                        if growth > 0:
                            return f"<span style='color: #0066cc; font-weight: bold;'>▲ {growth:+.1f}%</span>"
                        elif growth < 0:
                            return f"<span style='color: #cc0000; font-weight: bold;'>▼ {growth:+.1f}%</span>"
                        else:
                            return f"<span style='color: #666;'>0.0%</span>"
                    
                    # 전년비 컬럼에 색상 적용
                    ss_summary['SS 전년비'] = ss_summary['SS 전년비'].apply(format_growth_with_color)
                    
                    # 디스커버리 브랜드 굵은 글씨로 강조
                    ss_summary['유통사'] = ss_summary['유통사'].apply(lambda x: f"<b>{x}</b>" if '디스커버리' in x else x)
                    
                    # HTML로 표시하여 색상이 적용되도록 함
                    st.markdown(ss_summary.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                else:
                    # FW 시즌 차트
                    fig_fw = go.Figure()
                    
                    if data_type == "총매출":
                        fig_fw.add_trace(go.Bar(
                            name='24FW',
                            x=summary_df['유통사'],
                            y=summary_df['24FW_총매출'] / 100000000,
                            marker_color='#2ca02c'
                        ))
                        
                        fig_fw.add_trace(go.Bar(
                            name='23FW',
                            x=summary_df['유통사'],
                            y=summary_df['23FW_총매출'] / 100000000,
                            marker_color='#d62728'
                        ))
                        
                        y_title = '총 매출 (억원)'
                        chart_title = '유통사별 디스커버리 FW 시즌 총 매출 비교'
                    else:  # 평균매출
                        fig_fw.add_trace(go.Bar(
                            name='24FW 평균',
                            x=summary_df['유통사'],
                            y=summary_df['24FW_평균매출'] / 100000000,
                            marker_color='#2ca02c'
                        ))
                        
                        fig_fw.add_trace(go.Bar(
                            name='23FW 평균',
                            x=summary_df['유통사'],
                            y=summary_df['23FW_평균매출'] / 100000000,
                            marker_color='#d62728'
                        ))
                        
                        y_title = '평균 매출 (억원)'
                        chart_title = '유통사별 디스커버리 FW 시즌 평균 매출 비교'
                    
                    fig_fw.update_layout(
                        title=chart_title,
                        xaxis_title='유통사',
                        yaxis_title=y_title,
                        barmode='group',
                        height=500
                    )
                    
                    st.plotly_chart(fig_fw, use_container_width=True)
                    
                    # FW 시즌 요약 테이블
                    st.subheader("FW 시즌 요약")
                    
                    if data_type == "총매출":
                        fw_summary = summary_df[['유통사', '매장수', '24FW_총매출', '23FW_총매출', 'FW_전년비']].copy()
                        fw_summary['24FW_총매출'] = fw_summary['24FW_총매출'].apply(format_to_hundred_million)
                        fw_summary['23FW_총매출'] = fw_summary['23FW_총매출'].apply(format_to_hundred_million)
                        fw_summary.columns = ['유통사', '매장수', '24FW 총매출', '23FW 총매출', 'FW 전년비']
                    else:  # 평균매출
                        fw_summary = summary_df[['유통사', '매장수', '24FW_평균매출', '23FW_평균매출', 'FW_전년비']].copy()
                        fw_summary['24FW_평균매출'] = fw_summary['24FW_평균매출'].apply(format_to_hundred_million)
                        fw_summary['23FW_평균매출'] = fw_summary['23FW_평균매출'].apply(format_to_hundred_million)
                        fw_summary.columns = ['유통사', '매장수', '24FW 평균매출', '23FW 평균매출', 'FW 전년비']
                    
                    # 전년비 색상 표시를 위한 스타일링
                    def format_growth_with_color(growth):
                        if growth > 0:
                            return f"<span style='color: #0066cc; font-weight: bold;'>▲ {growth:+.1f}%</span>"
                        elif growth < 0:
                            return f"<span style='color: #cc0000; font-weight: bold;'>▼ {growth:+.1f}%</span>"
                        else:
                            return f"<span style='color: #666;'>0.0%</span>"
                    
                    # 전년비 컬럼에 색상 적용
                    fw_summary['FW 전년비'] = fw_summary['FW 전년비'].apply(format_growth_with_color)
                    
                    # 디스커버리 브랜드 굵은 글씨로 강조
                    fw_summary['유통사'] = fw_summary['유통사'].apply(lambda x: f"<b>{x}</b>" if '디스커버리' in x else x)
                    
                    # HTML로 표시하여 색상이 적용되도록 함
                    st.markdown(fw_summary.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # 동업계 MS 현황
            st.subheader("🏢 동업계 MS 현황")
            
            # MS 유통사 선택
            ms_distributors = ['전체'] + sorted(filtered_df['유통사'].unique().tolist())
            ms_distributor = st.selectbox("MS 유통사 선택", ms_distributors, key="ms_distributor")
            
            # 선택된 유통사에 따라 데이터 필터링
            if ms_distributor == '전체':
                ms_filtered_df = filtered_df
            else:
                ms_filtered_df = filtered_df[filtered_df['유통사'] == ms_distributor]
            
            # 브랜드별 데이터 집계
            brand_summary = []
            for brand in ms_filtered_df['브랜드'].unique():
                brand_data = ms_filtered_df[ms_filtered_df['브랜드'] == brand]
                
                seasons = ['23SS', '23FW', '24SS', '24FW', '25SS']
                season_totals = {}
                season_valid_stores = {}
                
                for season in seasons:
                    season_totals[season] = brand_data[season].sum()
                    # 0이 아닌 매장 수 계산 (평균 매출용)
                    season_valid_stores[season] = len(brand_data[brand_data[season] > 0])
                
                # SS 시즌 성장률
                ss_growth = ((season_totals['25SS'] - season_totals['24SS']) / season_totals['24SS'] * 100) if season_totals['24SS'] > 0 else 0
                
                # FW 시즌 성장률
                fw_growth = ((season_totals['24FW'] - season_totals['23FW']) / season_totals['23FW'] * 100) if season_totals['23FW'] > 0 else 0
                
                brand_summary.append({
                    '브랜드': brand,
                    '25SS': season_totals['25SS'],
                    '24SS': season_totals['24SS'],
                    'SS_전년비': ss_growth,
                    '24FW': season_totals['24FW'],
                    '23FW': season_totals['23FW'],
                    'FW_전년비': fw_growth
                })
            
            brand_df = pd.DataFrame(brand_summary)
            # 기본적으로는 총매출 기준으로 정렬 (나중에 데이터 타입에 따라 재정렬)
            brand_df = brand_df.sort_values('25SS', ascending=False).reset_index(drop=True)
            
            # MS 현황 차트
            ms_season = st.radio("MS 시즌 선택", ["SS 시즌", "FW 시즌"], horizontal=True, key="ms_season")
            ms_data_type = st.radio("MS 데이터 타입 선택", ["총매출", "평균매출"], horizontal=True, key="ms_data_type")
            
            if ms_season == "SS 시즌":
                fig_ms = go.Figure()
                
                # 디스커버리 강조 색상 (더욱 눈에 띄는 색상과 스타일)
                colors = ['#FF1744' if brand == '디스커버리' else '#E3F2FD' for brand in brand_df['브랜드']]
                edge_colors = ['#D32F2F' if brand == '디스커버리' else '#1976D2' for brand in brand_df['브랜드']]
                edge_widths = [3 if brand == '디스커버리' else 1 for brand in brand_df['브랜드']]
                
                if ms_data_type == "총매출":
                    fig_ms.add_trace(go.Bar(
                        name='25SS',
                        x=brand_df['브랜드'],
                        y=brand_df['25SS'] / 100000000,
                        marker=dict(
                            color=colors,
                            line=dict(color=edge_colors, width=edge_widths)
                        ),
                        text=[f"{format_growth_with_color(brand_df.iloc[i]['SS_전년비'])}" for i in range(len(brand_df))],
                        textposition='outside',
                        textfont=dict(size=10, color='#000000')
                    ))
                    
                    fig_ms.add_trace(go.Bar(
                        name='24SS',
                        x=brand_df['브랜드'],
                        y=brand_df['24SS'] / 100000000,
                        marker=dict(
                            color=['#FF5722' if brand == '디스커버리' else '#BBDEFB' for brand in brand_df['브랜드']],
                            line=dict(color=['#D32F2F' if brand == '디스커버리' else '#1976D2' for brand in brand_df['브랜드']], width=edge_widths)
                        )
                    ))
                    
                    y_title = '매출 (억원)'
                    chart_title = 'SS 시즌 총 매출 현황 (높은 매출 순) - 🔥 디스커버리 강조'
                else:  # 평균매출
                    # 평균매출 계산을 위해 매출이 0이 아닌 매장 수 계산
                    brand_valid_store_counts = {}
                    for brand in brand_df['브랜드']:
                        brand_data = ms_filtered_df[ms_filtered_df['브랜드'] == brand]
                        # 25SS와 24SS 모두 0이 아닌 매장만 카운트
                        valid_stores_25SS = brand_data[brand_data['25SS'] > 0]['매장명'].nunique()
                        valid_stores_24SS = brand_data[brand_data['24SS'] > 0]['매장명'].nunique()
                        brand_valid_store_counts[brand] = {
                            '25SS': valid_stores_25SS,
                            '24SS': valid_stores_24SS
                        }
                    
                    # 평균매출 계산 (매출이 0인 매장 제외)
                    brand_df['25SS_평균'] = brand_df.apply(
                        lambda row: row['25SS'] / brand_valid_store_counts[row['브랜드']]['25SS'] 
                        if brand_valid_store_counts[row['브랜드']]['25SS'] > 0 else 0, axis=1
                    )
                    brand_df['24SS_평균'] = brand_df.apply(
                        lambda row: row['24SS'] / brand_valid_store_counts[row['브랜드']]['24SS'] 
                        if brand_valid_store_counts[row['브랜드']]['24SS'] > 0 else 0, axis=1
                    )
                    
                    # 평균매출 기준 전년비 재계산
                    brand_df['SS_전년비'] = brand_df.apply(
                        lambda row: ((row['25SS_평균'] - row['24SS_평균']) / row['24SS_평균'] * 100) 
                        if row['24SS_평균'] > 0 else 0, axis=1
                    )
                    
                    # 평균매출 기준으로 재정렬
                    brand_df = brand_df.sort_values('25SS_평균', ascending=False).reset_index(drop=True)
                    
                    # 재정렬 후 색상 배열 다시 계산
                    colors = ['#FF1744' if brand == '디스커버리' else '#E3F2FD' for brand in brand_df['브랜드']]
                    edge_colors = ['#D32F2F' if brand == '디스커버리' else '#1976D2' for brand in brand_df['브랜드']]
                    edge_widths = [3 if brand == '디스커버리' else 1 for brand in brand_df['브랜드']]
                    
                    fig_ms.add_trace(go.Bar(
                        name='25SS 평균',
                        x=brand_df['브랜드'],
                        y=brand_df['25SS_평균'] / 100000000,
                        marker=dict(
                            color=colors,
                            line=dict(color=edge_colors, width=edge_widths)
                        ),
                        text=[f"{format_growth_with_color(brand_df.iloc[i]['SS_전년비'])}" for i in range(len(brand_df))],
                        textposition='outside',
                        textfont=dict(size=10, color='#000000')
                    ))
                    
                    fig_ms.add_trace(go.Bar(
                        name='24SS 평균',
                        x=brand_df['브랜드'],
                        y=brand_df['24SS_평균'] / 100000000,
                        marker=dict(
                            color=['#FF5722' if brand == '디스커버리' else '#BBDEFB' for brand in brand_df['브랜드']],
                            line=dict(color=['#D32F2F' if brand == '디스커버리' else '#1976D2' for brand in brand_df['브랜드']], width=edge_widths)
                        )
                    ))
                    
                    y_title = '평균 매출 (억원)'
                    chart_title = 'SS 시즌 평균 매출 현황 (높은 매출 순) - 🔥 디스커버리 강조'
                
                # 디스커버리 브랜드 텍스트 굵게 표시
                brand_labels = [f"<b>{brand}</b>" if brand == '디스커버리' else brand for brand in brand_df['브랜드']]
                
                fig_ms.update_layout(
                    title=chart_title,
                    xaxis_title='브랜드',
                    yaxis_title=y_title,
                    barmode='group',
                    height=500,
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(brand_df))),
                        ticktext=brand_labels
                    )
                )
                
                st.plotly_chart(fig_ms, use_container_width=True)
                
                # MS 테이블
                st.subheader("브랜드별 매출 순위")
                
                # 전년 순위 계산 (24SS 기준으로 정렬)
                prev_year_df = brand_df.copy()
                prev_year_df = prev_year_df.sort_values('24SS', ascending=False).reset_index(drop=True)
                prev_year_df['prev_rank'] = range(1, len(prev_year_df) + 1)
                
                # 현재 순위와 전년 순위 매핑
                current_rank = range(1, len(brand_df) + 1)
                rank_mapping = dict(zip(brand_df['브랜드'], current_rank))
                prev_rank_mapping = dict(zip(prev_year_df['브랜드'], prev_year_df['prev_rank']))
                
                # 순위 증감 계산 (SS 시즌)
                def format_rank_change(brand):
                    current = rank_mapping[brand]
                    prev = prev_rank_mapping[brand]
                    change = prev - current
                    
                    if change > 0:
                        return f"{current}<span style='color: #0066cc; font-weight: bold;'>(▲{change})</span>"
                    elif change < 0:
                        return f"{current}<span style='color: #cc0000; font-weight: bold;'>(▼{abs(change)})</span>"
                    else:
                        return f"{current}(-)"
                
                if ms_data_type == "총매출":
                    ms_table = brand_df[['브랜드', '25SS', '24SS', 'SS_전년비']].copy()
                    ms_table['25SS'] = ms_table['25SS'].apply(format_to_hundred_million)
                    ms_table['24SS'] = ms_table['24SS'].apply(format_to_hundred_million)
                    ms_table.columns = ['브랜드', '25SS', '24SS', 'SS 전년비']
                else:  # 평균매출
                    ms_table = brand_df[['브랜드', '25SS_평균', '24SS_평균', 'SS_전년비']].copy()
                    ms_table['25SS_평균'] = ms_table['25SS_평균'].apply(format_to_hundred_million)
                    ms_table['24SS_평균'] = ms_table['24SS_평균'].apply(format_to_hundred_million)
                    ms_table.columns = ['브랜드', '25SS 평균', '24SS 평균', 'SS 전년비']
                
                # 순위 증감 추가
                ms_table['순위'] = ms_table['브랜드'].apply(format_rank_change)
                
                # 전년비 색상 표시
                def format_growth_with_color(growth):
                    if growth > 0:
                        return f"<span style='color: #0066cc; font-weight: bold;'>▲ {growth:+.1f}%</span>"
                    elif growth < 0:
                        return f"<span style='color: #cc0000; font-weight: bold;'>▼ {growth:+.1f}%</span>"
                    else:
                        return f"<span style='color: #666;'>0.0%</span>"
                
                ms_table['SS 전년비'] = ms_table['SS 전년비'].apply(format_growth_with_color)
                
                # 디스커버리 브랜드 굵은 글씨로 표시
                ms_table['브랜드'] = ms_table['브랜드'].apply(lambda x: f"<b>{x}</b>" if x == '디스커버리' else x)
                
                # 컬럼 순서 조정
                ms_table = ms_table[['순위', '브랜드'] + [col for col in ms_table.columns if col not in ['순위', '브랜드']]]
                
                # HTML로 표시하여 색상이 적용되도록 함
                st.markdown(ms_table.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            else:
                fig_ms = go.Figure()
                
                # 디스커버리 강조 색상 (더욱 눈에 띄는 색상과 스타일)
                colors = ['#FF1744' if brand == '디스커버리' else '#E8F5E8' for brand in brand_df['브랜드']]
                edge_colors = ['#D32F2F' if brand == '디스커버리' else '#388E3C' for brand in brand_df['브랜드']]
                edge_widths = [3 if brand == '디스커버리' else 1 for brand in brand_df['브랜드']]
                
                if ms_data_type == "총매출":
                    fig_ms.add_trace(go.Bar(
                        name='24FW',
                        x=brand_df['브랜드'],
                        y=brand_df['24FW'] / 100000000,
                        marker=dict(
                            color=colors,
                            line=dict(color=edge_colors, width=edge_widths)
                        ),
                        text=[f"{format_growth_with_color(brand_df.iloc[i]['FW_전년비'])}" for i in range(len(brand_df))],
                        textposition='outside',
                        textfont=dict(size=10, color='#000000')
                    ))
                    
                    fig_ms.add_trace(go.Bar(
                        name='23FW',
                        x=brand_df['브랜드'],
                        y=brand_df['23FW'] / 100000000,
                        marker=dict(
                            color=['#FF5722' if brand == '디스커버리' else '#C8E6C9' for brand in brand_df['브랜드']],
                            line=dict(color=['#D32F2F' if brand == '디스커버리' else '#388E3C' for brand in brand_df['브랜드']], width=edge_widths)
                        )
                    ))
                    
                    y_title = '매출 (억원)'
                    chart_title = 'FW 시즌 총 매출 현황 (높은 매출 순) - 🔥 디스커버리 강조'
                else:  # 평균매출
                    # 평균매출 계산을 위해 매출이 0이 아닌 매장 수 계산
                    brand_valid_store_counts = {}
                    for brand in brand_df['브랜드']:
                        brand_data = ms_filtered_df[ms_filtered_df['브랜드'] == brand]
                        # 24FW와 23FW 모두 0이 아닌 매장만 카운트
                        valid_stores_24FW = brand_data[brand_data['24FW'] > 0]['매장명'].nunique()
                        valid_stores_23FW = brand_data[brand_data['23FW'] > 0]['매장명'].nunique()
                        brand_valid_store_counts[brand] = {
                            '24FW': valid_stores_24FW,
                            '23FW': valid_stores_23FW
                        }
                    
                    # 평균매출 계산 (매출이 0인 매장 제외)
                    brand_df['24FW_평균'] = brand_df.apply(
                        lambda row: row['24FW'] / brand_valid_store_counts[row['브랜드']]['24FW'] 
                        if brand_valid_store_counts[row['브랜드']]['24FW'] > 0 else 0, axis=1
                    )
                    brand_df['23FW_평균'] = brand_df.apply(
                        lambda row: row['23FW'] / brand_valid_store_counts[row['브랜드']]['23FW'] 
                        if brand_valid_store_counts[row['브랜드']]['23FW'] > 0 else 0, axis=1
                    )
                    
                    # 평균매출 기준 전년비 재계산
                    brand_df['FW_전년비'] = brand_df.apply(
                        lambda row: ((row['24FW_평균'] - row['23FW_평균']) / row['23FW_평균'] * 100) 
                        if row['23FW_평균'] > 0 else 0, axis=1
                    )
                    
                    # 평균매출 기준으로 재정렬
                    brand_df = brand_df.sort_values('24FW_평균', ascending=False).reset_index(drop=True)
                    
                    # 재정렬 후 색상 배열 다시 계산
                    colors = ['#FF1744' if brand == '디스커버리' else '#E8F5E8' for brand in brand_df['브랜드']]
                    edge_colors = ['#D32F2F' if brand == '디스커버리' else '#388E3C' for brand in brand_df['브랜드']]
                    edge_widths = [3 if brand == '디스커버리' else 1 for brand in brand_df['브랜드']]
                    
                    fig_ms.add_trace(go.Bar(
                        name='24FW 평균',
                        x=brand_df['브랜드'],
                        y=brand_df['24FW_평균'] / 100000000,
                        marker=dict(
                            color=colors,
                            line=dict(color=edge_colors, width=edge_widths)
                        ),
                        text=[f"{format_growth_with_color(brand_df.iloc[i]['FW_전년비'])}" for i in range(len(brand_df))],
                        textposition='outside',
                        textfont=dict(size=10, color='#000000')
                    ))
                    
                    fig_ms.add_trace(go.Bar(
                        name='23FW 평균',
                        x=brand_df['브랜드'],
                        y=brand_df['23FW_평균'] / 100000000,
                        marker=dict(
                            color=['#FF5722' if brand == '디스커버리' else '#C8E6C9' for brand in brand_df['브랜드']],
                            line=dict(color=['#D32F2F' if brand == '디스커버리' else '#388E3C' for brand in brand_df['브랜드']], width=edge_widths)
                        )
                    ))
                    
                    y_title = '평균 매출 (억원)'
                    chart_title = 'FW 시즌 평균 매출 현황 (높은 매출 순) - 🔥 디스커버리 강조'
                
                # 디스커버리 브랜드 텍스트 굵게 표시
                brand_labels = [f"<b>{brand}</b>" if brand == '디스커버리' else brand for brand in brand_df['브랜드']]
                
                fig_ms.update_layout(
                    title=chart_title,
                    xaxis_title='브랜드',
                    yaxis_title=y_title,
                    barmode='group',
                    height=500,
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(len(brand_df))),
                        ticktext=brand_labels
                    )
                )
                
                st.plotly_chart(fig_ms, use_container_width=True)
                
                # MS 테이블
                st.subheader("브랜드별 매출 순위")
                
                # 전년 순위 계산 (23FW 기준으로 정렬)
                prev_year_df = brand_df.copy()
                prev_year_df = prev_year_df.sort_values('23FW', ascending=False).reset_index(drop=True)
                prev_year_df['prev_rank'] = range(1, len(prev_year_df) + 1)
                
                # 현재 순위와 전년 순위 매핑
                current_rank = range(1, len(brand_df) + 1)
                rank_mapping = dict(zip(brand_df['브랜드'], current_rank))
                prev_rank_mapping = dict(zip(prev_year_df['브랜드'], prev_year_df['prev_rank']))
                
                # 순위 증감 계산 (FW 시즌)
                def format_rank_change(brand):
                    current = rank_mapping[brand]
                    prev = prev_rank_mapping[brand]
                    change = prev - current
                    
                    if change > 0:
                        return f"{current}<span style='color: #0066cc; font-weight: bold;'>(▲{change})</span>"
                    elif change < 0:
                        return f"{current}<span style='color: #cc0000; font-weight: bold;'>(▼{abs(change)})</span>"
                    else:
                        return f"{current}(-)"
                
                if ms_data_type == "총매출":
                    ms_table = brand_df[['브랜드', '24FW', '23FW', 'FW_전년비']].copy()
                    ms_table['24FW'] = ms_table['24FW'].apply(format_to_hundred_million)
                    ms_table['23FW'] = ms_table['23FW'].apply(format_to_hundred_million)
                    ms_table.columns = ['브랜드', '24FW', '23FW', 'FW 전년비']
                else:  # 평균매출
                    ms_table = brand_df[['브랜드', '24FW_평균', '23FW_평균', 'FW_전년비']].copy()
                    ms_table['24FW_평균'] = ms_table['24FW_평균'].apply(format_to_hundred_million)
                    ms_table['23FW_평균'] = ms_table['23FW_평균'].apply(format_to_hundred_million)
                    ms_table.columns = ['브랜드', '24FW 평균', '23FW 평균', 'FW 전년비']
                
                # 순위 증감 추가
                ms_table['순위'] = ms_table['브랜드'].apply(format_rank_change)
                
                # 전년비 색상 표시
                def format_growth_with_color(growth):
                    if growth > 0:
                        return f"<span style='color: #0066cc; font-weight: bold;'>▲ {growth:+.1f}%</span>"
                    elif growth < 0:
                        return f"<span style='color: #cc0000; font-weight: bold;'>▼ {growth:+.1f}%</span>"
                    else:
                        return f"<span style='color: #666;'>0.0%</span>"
                
                ms_table['FW 전년비'] = ms_table['FW 전년비'].apply(format_growth_with_color)
                
                # 디스커버리 브랜드 굵은 글씨로 표시
                ms_table['브랜드'] = ms_table['브랜드'].apply(lambda x: f"<b>{x}</b>" if x == '디스커버리' else x)
                
                # 컬럼 순서 조정
                ms_table = ms_table[['순위', '브랜드'] + [col for col in ms_table.columns if col not in ['순위', '브랜드']]]
                
                # HTML로 표시하여 색상이 적용되도록 함
                st.markdown(ms_table.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # 아울렛 매장당 효율 분석
            st.subheader("🏪 아울렛 매장당 효율")
            
            # 디스커버리 브랜드만 필터링
            discovery_outlet_data = filtered_df[filtered_df['브랜드'] == '디스커버리'].copy()
            
            if not discovery_outlet_data.empty:
                # 시즌 선택
                efficiency_season = st.radio("효율 분석 시즌 선택", ["SS시즌", "FW시즌"], horizontal=True, key="efficiency_season")
                
                # 매장별 효율 데이터 계산
                store_efficiency_data = []
                for store_name in discovery_outlet_data['매장명'].unique():
                    store_rows = discovery_outlet_data[discovery_outlet_data['매장명'] == store_name]
                    
                    # 매장 정보
                    area_pyeong = store_rows['매장 면적'].iloc[0] if '매장 면적' in store_rows.columns else 0
                    
                    if area_pyeong > 0:  # 면적이 있는 매장만 분석
                        if efficiency_season == "SS시즌":
                            # SS 시즌 데이터
                            sales_25ss = store_rows['25SS'].sum()
                            sales_24ss = store_rows['24SS'].sum()
                            
                            # 평당 매출 계산 (백만원 단위)
                            efficiency_25ss = (sales_25ss / area_pyeong) / 1000000  # 백만원/평
                            efficiency_24ss = (sales_24ss / area_pyeong) / 1000000  # 백만원/평
                            
                            # 신장율 계산
                            efficiency_growth = ((efficiency_25ss - efficiency_24ss) / efficiency_24ss * 100) if efficiency_24ss > 0 else 0
                            sales_growth = ((sales_25ss - sales_24ss) / sales_24ss * 100) if sales_24ss > 0 else 0
                            
                            store_efficiency_data.append({
                                '매장명': store_name,
                                '면적(평)': area_pyeong,
                                '25SS_평당매출': efficiency_25ss,
                                '24SS_평당매출': efficiency_24ss,
                                '평당매출_신장율': efficiency_growth,
                                '25SS_총매출': sales_25ss,
                                '24SS_총매출': sales_24ss,
                                '총매출_신장율': sales_growth
                            })
                        else:  # FW시즌
                            # FW 시즌 데이터
                            sales_24fw = store_rows['24FW'].sum()
                            sales_23fw = store_rows['23FW'].sum()
                            
                            # 평당 매출 계산 (백만원 단위)
                            efficiency_24fw = (sales_24fw / area_pyeong) / 1000000  # 백만원/평
                            efficiency_23fw = (sales_23fw / area_pyeong) / 1000000  # 백만원/평
                            
                            # 신장율 계산
                            efficiency_growth = ((efficiency_24fw - efficiency_23fw) / efficiency_23fw * 100) if efficiency_23fw > 0 else 0
                            sales_growth = ((sales_24fw - sales_23fw) / sales_23fw * 100) if sales_23fw > 0 else 0
                            
                            store_efficiency_data.append({
                                '매장명': store_name,
                                '면적(평)': area_pyeong,
                                '24FW_평당매출': efficiency_24fw,
                                '23FW_평당매출': efficiency_23fw,
                                '평당매출_신장율': efficiency_growth,
                                '24FW_총매출': sales_24fw,
                                '23FW_총매출': sales_23fw,
                                '총매출_신장율': sales_growth
                            })
                
                if store_efficiency_data:
                    efficiency_df = pd.DataFrame(store_efficiency_data)
                    
                    # 평당 매출 기준으로 정렬
                    if efficiency_season == "SS시즌":
                        efficiency_df = efficiency_df.sort_values('25SS_평당매출', ascending=False).reset_index(drop=True)
                    else:
                        efficiency_df = efficiency_df.sort_values('24FW_평당매출', ascending=False).reset_index(drop=True)
                    
                    # 전년 순위 계산
                    prev_year_df = efficiency_df.copy()
                    if efficiency_season == "SS시즌":
                        prev_year_df = prev_year_df.sort_values('24SS_평당매출', ascending=False).reset_index(drop=True)
                    else:
                        prev_year_df = prev_year_df.sort_values('23FW_평당매출', ascending=False).reset_index(drop=True)
                    prev_year_df['prev_rank'] = range(1, len(prev_year_df) + 1)
                    
                    # 현재 순위와 전년 순위 매핑
                    current_rank = range(1, len(efficiency_df) + 1)
                    rank_mapping = dict(zip(efficiency_df['매장명'], current_rank))
                    prev_rank_mapping = dict(zip(prev_year_df['매장명'], prev_year_df['prev_rank']))
                    
                    # 순위 증감 계산
                    def format_rank_change(store_name):
                        current = rank_mapping[store_name]
                        prev = prev_rank_mapping[store_name]
                        change = prev - current
                        
                        if change > 0:
                            return f"{current}<span style='color: #0066cc; font-weight: bold;'>(▲{change})</span>"
                        elif change < 0:
                            return f"{current}<span style='color: #cc0000; font-weight: bold;'>(▼{abs(change)})</span>"
                        else:
                            return f"{current}(-)"
                    
                    # 신장율 색상 표시 함수
                    def format_growth_with_color(growth):
                        if growth > 0:
                            return f"<span style='color: #0066cc; font-weight: bold;'>▲ {growth:+.1f}%</span>"
                        elif growth < 0:
                            return f"<span style='color: #cc0000; font-weight: bold;'>▼ {growth:+.1f}%</span>"
                        else:
                            return f"<span style='color: #666;'>0.0%</span>"
                    
                    # 백만원 단위 포맷팅 함수
                    def format_million(value):
                        return f"{value:.1f}백만원"
                    
                    # 테이블 데이터 준비
                    if efficiency_season == "SS시즌":
                        table_data = []
                        for idx, row in efficiency_df.iterrows():
                            table_data.append({
                                '순위': format_rank_change(row['매장명']),
                                '매장명': row['매장명'],
                                '면적(평)': f"{row['면적(평)']:.1f}평",
                                '25SS 시즌 평당 매출': format_million(row['25SS_평당매출']),
                                '24SS시즌 평당 매출': format_million(row['24SS_평당매출']),
                                '평당매출 신장율': format_growth_with_color(row['평당매출_신장율']),
                                '25SS시즌 총 매출': format_million(row['25SS_총매출'] / 1000000),
                                '24SS시즌 총 매출': format_million(row['24SS_총매출'] / 1000000),
                                '총매출 신장율': format_growth_with_color(row['총매출_신장율'])
                            })
                    else:  # FW시즌
                        table_data = []
                        for idx, row in efficiency_df.iterrows():
                            table_data.append({
                                '순위': format_rank_change(row['매장명']),
                                '매장명': row['매장명'],
                                '면적(평)': f"{row['면적(평)']:.1f}평",
                                '24FW 시즌 평당 매출': format_million(row['24FW_평당매출']),
                                '23FW시즌 평당 매출': format_million(row['23FW_평당매출']),
                                '평당매출 신장율': format_growth_with_color(row['평당매출_신장율']),
                                '24FW시즌 총 매출': format_million(row['24FW_총매출'] / 1000000),
                                '23FW시즌 총 매출': format_million(row['23FW_총매출'] / 1000000),
                                '총매출 신장율': format_growth_with_color(row['총매출_신장율'])
                            })
                    
                    # DataFrame으로 변환
                    result_df = pd.DataFrame(table_data)
                    
                    # HTML로 표시하여 색상이 적용되도록 함
                    st.markdown(result_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.warning("면적 정보가 있는 디스커버리 매장이 없습니다.")
            else:
                st.warning("디스커버리 브랜드 데이터가 없습니다.")
    
    with tab2:
        st.markdown('<h2 class="section-header">📊 매장 효율</h2>', unsafe_allow_html=True)
        
        # 매장 효율 분석
        st.subheader("🚀 디스커버리 매장 효율 분석")
        
        # 효율성 데이터 계산
        efficiency_df = calculate_efficiency_data(df)
        
        if not efficiency_df.empty:
            # 시즌 선택
            season_type = st.radio("시즌 선택", ["SS", "FW"], horizontal=True)
            
            # 매출기준 선택
            sales_criteria = st.radio("매출기준 선택", ["매출순", "평당매출순"], horizontal=True)
            
            if season_type == "SS":
                current_season = "25SS"
                prev_season = "24SS"
                season_label = "SS"
            else:
                current_season = "24FW"
                prev_season = "23FW"
                season_label = "FW"
            
            # 시즌별 데이터 준비
            season_df = efficiency_df.copy()
            season_df['현재시즌_매출'] = season_df[f'{current_season}_매출액']
            season_df['현재시즌_효율성'] = season_df[f'{current_season}_효율성']
            season_df['전년시즌_매출'] = season_df[f'{prev_season}_매출액']
            season_df['전년시즌_효율성'] = season_df[f'{prev_season}_효율성']
            
            # 전년비 계산
            season_df['매출_전년비'] = season_df.apply(
                lambda row: ((row['현재시즌_매출'] - row['전년시즌_매출']) / row['전년시즌_매출'] * 100) 
                if row['전년시즌_매출'] > 0 else 0, axis=1
            )
            season_df['효율성_전년비'] = season_df.apply(
                lambda row: ((row['현재시즌_효율성'] - row['전년시즌_효율성']) / row['전년시즌_효율성'] * 100) 
                if row['전년시즌_효율성'] > 0 else 0, axis=1
            )
            
            # 매장명에 면적 표시 추가
            season_df['매장명_면적'] = season_df.apply(
                lambda row: f"{row['매장명']} ({row['매장면적_평']:.1f}평)", axis=1
            )
            
            # 매출기준에 따라 정렬
            if sales_criteria == "매출순":
                season_df = season_df.sort_values('현재시즌_매출', ascending=False).reset_index(drop=True)
            else:  # 평당매출순
                season_df = season_df.sort_values('현재시즌_효율성', ascending=False).reset_index(drop=True)
            
            # 전년 순위 계산 (매출기준에 따라)
            prev_year_df = season_df.copy()
            if sales_criteria == "매출순":
                prev_year_df = prev_year_df.sort_values('전년시즌_매출', ascending=False).reset_index(drop=True)
            else:  # 평당매출순
                prev_year_df = prev_year_df.sort_values('전년시즌_효율성', ascending=False).reset_index(drop=True)
            prev_year_df['prev_rank'] = range(1, len(prev_year_df) + 1)
            
            # 현재 순위와 전년 순위 매핑
            current_rank = range(1, len(season_df) + 1)
            rank_mapping = dict(zip(season_df['매장명'], current_rank))
            prev_rank_mapping = dict(zip(prev_year_df['매장명'], prev_year_df['prev_rank']))
            
            # 순위 증감 계산
            def format_rank_change(store_name):
                current = rank_mapping[store_name]
                prev = prev_rank_mapping[store_name]
                change = prev - current
                
                if change > 0:
                    return f"{current}<span style='color: #0066cc; font-weight: bold;'>(▲{change})</span>"
                elif change < 0:
                    return f"{current}<span style='color: #cc0000; font-weight: bold;'>(▼{abs(change)})</span>"
                else:
                    return f"{current}(-)"
            
            # BEST 5, WORST 5 표시
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 BEST 5")
                best_5 = season_df.head(5)
                best_data = []
                for idx, row in best_5.iterrows():
                    best_data.append({
                        '순위': f"{idx + 1}위",
                        '매장명': row['매장명_면적'],
                        '유통사': row['유통사'],
                        f'{current_season} 매출': format_to_hundred_million(row['현재시즌_매출']),
                        '평당매출': format_efficiency_to_million(row['현재시즌_효율성'])
                    })
                best_df = pd.DataFrame(best_data)
                st.dataframe(best_df, use_container_width=True)
            
            with col2:
                st.subheader("📉 WORST 5")
                worst_5 = season_df.tail(5)
                worst_data = []
                for i, (idx, row) in enumerate(worst_5.iterrows()):
                    worst_data.append({
                        '순위': f"{len(season_df) - 4 + i}위",
                        '매장명': row['매장명_면적'],
                        '유통사': row['유통사'],
                        f'{current_season} 매출': format_to_hundred_million(row['현재시즌_매출']),
                        '평당매출': format_efficiency_to_million(row['현재시즌_효율성'])
                    })
                worst_df = pd.DataFrame(worst_data)
                st.dataframe(worst_df, use_container_width=True)
            
            # 전년비 요약
            st.subheader(f"📊 {season_label} 시즌 전년비 요약")
            
            summary_data = []
            for idx, row in season_df.iterrows():
                summary_data.append({
                    '순위': format_rank_change(row['매장명']),
                    '매장명': row['매장명_면적'],
                    '유통사': row['유통사'],
                    f'{current_season} 매출': format_to_hundred_million(row['현재시즌_매출']),
                    f'{prev_season} 매출': format_to_hundred_million(row['전년시즌_매출']),
                    '매출 전년비': format_growth_with_color(row['매출_전년비']),
                    f'{current_season} 평당매출': format_efficiency_to_million(row['현재시즌_효율성']),
                    f'{prev_season} 평당매출': format_efficiency_to_million(row['전년시즌_효율성']),
                    '평당매출 전년비': format_growth_with_color(row['효율성_전년비'])
                })
            
            summary_df = pd.DataFrame(summary_data)
            # HTML로 표시하여 색상이 적용되도록 함
            st.markdown(summary_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
        else:
            st.warning("디스커버리 브랜드 데이터가 없습니다.")
    
    with tab3:
        st.markdown('<h2 class="section-header">🤖 AI 분석</h2>', unsafe_allow_html=True)
        
        if api_key:
            # AI 분석 결과 표시
            if analyze_outlet:
                st.markdown("### 📊 아울렛 동향 AI 분석")
                
                # 디스커버리 데이터 준비
                discovery_data = filtered_df[filtered_df['브랜드'] == '디스커버리']
                efficiency_data = calculate_efficiency_data(filtered_df)
                
                if not discovery_data.empty:
                    with st.spinner("AI가 아울렛 동향을 분석하고 있습니다..."):
                        analysis_prompt = analyze_outlet_trends(discovery_data, efficiency_data)
                        ai_response = call_jemini_api(api_key, analysis_prompt)
                    
                    # 분석 결과 표시 박스
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        color: white;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    ">
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**🤖 AI 분석 결과**")
                    st.markdown(ai_response)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("디스커버리 데이터가 없어 분석할 수 없습니다.")
            
            elif analyze_peer:
                st.markdown("### 🏢 동업계 MS 현황 AI 분석")
                
                # 브랜드별 데이터 준비
                brand_df = filtered_df.groupby('브랜드').agg({
                    '25SS': 'sum',
                    '24SS': 'sum',
                    '24FW': 'sum',
                    '23FW': 'sum'
                }).reset_index()
                
                # 전년비 계산
                brand_df['SS_전년비'] = ((brand_df['25SS'] - brand_df['24SS']) / brand_df['24SS'] * 100).round(1)
                brand_df['FW_전년비'] = ((brand_df['24FW'] - brand_df['23FW']) / brand_df['23FW'] * 100).round(1)
                
                # SS 시즌 기준으로 정렬
                brand_df = brand_df.sort_values('25SS', ascending=False).reset_index(drop=True)
                
                if not brand_df.empty:
                    with st.spinner("AI가 동업계 MS 현황을 분석하고 있습니다..."):
                        analysis_prompt = analyze_peer_ms_status(brand_df)
                        ai_response = call_jemini_api(api_key, analysis_prompt)
                    
                    # 분석 결과 표시 박스
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        color: white;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    ">
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**🤖 AI 분석 결과**")
                    st.markdown(ai_response)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("브랜드 데이터가 없어 분석할 수 없습니다.")
            
            else:
                st.info("👆 사이드바에서 '아울렛 동향 AI 분석' 또는 '동업계 MS 현황 AI 분석' 버튼을 클릭하세요.")
                
                # 분석 안내
                st.markdown("""
                ### 📋 AI 분석 기능 안내
                
                **📊 아울렛 동향 AI 분석**
                - 어떤 유통망에서 디스커버리가 매출이 잘 나오고 효율이 좋은지 분석
                - 시즌별 매출 패턴과 유통사별 성과 차이 분석
                - 효율성이 높은 매장들의 공통점 분석
                - 개선 방안과 전략적 제안 제공
                
                **🏢 동업계 MS 현황 AI 분석**
                - 전년 대비 디스커버리 매출 추이 분석
                - 경쟁사 분석 및 잘 나가는 브랜드 파악
                - 디스커버리의 시장 포지션과 경쟁력 평가
                - 시장 기회와 위협 요소 분석
                - 디스커버리 브랜드 강화 전략 제안
                """)
        else:
            st.warning("🔑 재미나이 API 키를 입력하면 AI 분석을 사용할 수 있습니다.")
            
            st.markdown("""
            ### 🔑 API 키 설정 방법
                
                1. [Google AI Studio](https://makersuite.google.com/app/apikey)에 접속
                2. Google 계정으로 로그인
                3. "Create API Key" 버튼 클릭
                4. 생성된 API 키를 사이드바에 입력
                
                ### 🤖 AI 분석 기능
                
                **재미나이 2.5 Flash**를 사용하여 다음과 같은 분석을 제공합니다:
                - 데이터 기반 인사이트 도출
                - 시장 트렌드 분석
                - 경쟁사 분석
                - 전략적 제안
                """)

else:
    st.info("👆 사이드바에서 CSV 파일을 업로드하여 대시보드를 시작하세요.")
    
    # 사용법 안내
    st.markdown("""
    ## 📋 사용법 안내
    
    1. **파일 업로드**: 사이드바에서 'DX OUTLET MS DB.csv' 파일을 업로드하세요
    2. **필터링**: 유통사와 매장명을 선택하여 데이터를 필터링할 수 있습니다
    3. **아울렛 동향**: 디스커버리 브랜드의 시즌별 매출 흐름과 동업계 MS 현황을 확인하세요
    4. **매장 효율**: 디스커버리 매장들의 평당 매출액 기준 효율성을 분석하세요
    
    ## 📊 분석 내용
    
    - **아울렛 동향**: 유통사별 디스커버리 매출 비교, 브랜드별 MS 현황
    - **매장 효율**: 평당 매출액 기준 매장 효율성 순위, 시즌별 효율성 히트맵, 매장면적 vs 효율성 관계
    """)
