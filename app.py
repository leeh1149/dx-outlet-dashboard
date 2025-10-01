import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

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
        margin-bottom: 1.5rem;
    }
    .growth-positive {
        color: #007bff;
        font-weight: bold;
    }
    .growth-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .table-container {
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
</style>
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

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🏪 DX OUTLET 매출 대시보드</h1>
    <p>디스커버리 브랜드 아울렛 매출 분석</p>
</div>
""", unsafe_allow_html=True)

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
    
    # 아울렛 유통사별 매출 흐름 - 디스커버리
    st.markdown('<h2 class="section-header">🏪 아울렛 유통사별 매출 흐름 - 디스커버리</h2>', unsafe_allow_html=True)
    
    # 디스커버리 데이터만 필터링
    discovery_data = filtered_df[filtered_df['브랜드'] == '디스커버리']
    
    if len(discovery_data) > 0:
        # 유통사별 분석 데이터 생성
        def create_distributor_analysis(season_current, season_previous, season_name):
            distributor_summary = []
            
            for distributor in discovery_data['유통사'].unique():
                distributor_data = discovery_data[discovery_data['유통사'] == distributor]
                store_count = len(distributor_data['매장명'].unique())
                
                # 현재 시즌과 전년 시즌 매출
                total_current = distributor_data[season_current].sum()
                total_previous = distributor_data[season_previous].sum()
                avg_current = total_current / store_count if store_count > 0 else 0
                avg_previous = total_previous / store_count if store_count > 0 else 0
                
                # 신장율 계산
                total_growth = ((total_current - total_previous) / total_previous * 100) if total_previous > 0 else 0
                avg_growth = ((avg_current - avg_previous) / avg_previous * 100) if avg_previous > 0 else 0
                
                distributor_summary.append({
                    '유통사': distributor,
                    '매장수': store_count,
                    f'{season_current}_총매출': total_current,
                    f'{season_previous}_총매출': total_previous,
                    '총매출_신장율': total_growth,
                    f'{season_current}_평균매출': avg_current,
                    f'{season_previous}_평균매출': avg_previous,
                    '평균매출_신장율': avg_growth
                })
            
            return pd.DataFrame(distributor_summary)
        
        # SS 시즌 분석 (25SS vs 24SS)
        ss_analysis = create_distributor_analysis('25SS', '24SS', 'SS')
        
        # FW 시즌 분석 (24FW vs 23FW)
        fw_analysis = create_distributor_analysis('24FW', '23FW', 'FW')
        
        # 금액을 억원 단위로 변환하는 함수
        def format_amount(amount):
            if pd.isna(amount) or amount == 0:
                return "0.00억"
            return f"{amount/100000000:.2f}억"
        
        # 신장율을 포맷하는 함수
        def format_growth(growth):
            if pd.isna(growth):
                return "0.00%"
            if growth > 0:
                return f"▲{growth:.1f}%"
            else:
                return f"▼{abs(growth):.1f}%"
        
        # SS 시즌 표
        st.markdown('<h3>📊 SS 시즌 (25SS vs 24SS)</h3>', unsafe_allow_html=True)
        
        # SS 시즌 데이터 포맷팅
        ss_display = ss_analysis.copy()
        ss_display['25SS_총매출'] = ss_display['25SS_총매출'].apply(format_amount)
        ss_display['24SS_총매출'] = ss_display['24SS_총매출'].apply(format_amount)
        ss_display['25SS_평균매출'] = ss_display['25SS_평균매출'].apply(format_amount)
        ss_display['24SS_평균매출'] = ss_display['24SS_평균매출'].apply(format_amount)
        
        # 신장율 컬럼 추가 (색상 적용을 위해)
        ss_display['총매출_신장율_표시'] = ss_display['총매출_신장율'].apply(format_growth)
        ss_display['평균매출_신장율_표시'] = ss_display['평균매출_신장율'].apply(format_growth)
        
        # 표시용 컬럼만 선택
        ss_display_columns = ['유통사', '매장수', '25SS_총매출', '24SS_총매출', '총매출_신장율_표시', 
                             '25SS_평균매출', '24SS_평균매출', '평균매출_신장율_표시']
        ss_display = ss_display[ss_display_columns]
        
        # 컬럼명 변경
        ss_display.columns = ['유통사', '매장수', '25SS 총매출', '24SS 총매출', '총매출 신장율', 
                             '25SS 평균매출', '24SS 평균매출', '평균매출 신장율']
        
        # SS 시즌 표 표시
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.dataframe(ss_display, width='stretch', hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # FW 시즌 표
        st.markdown('<h3>📊 FW 시즌 (24FW vs 23FW)</h3>', unsafe_allow_html=True)
        
        # FW 시즌 데이터 포맷팅
        fw_display = fw_analysis.copy()
        fw_display['24FW_총매출'] = fw_display['24FW_총매출'].apply(format_amount)
        fw_display['23FW_총매출'] = fw_display['23FW_총매출'].apply(format_amount)
        fw_display['24FW_평균매출'] = fw_display['24FW_평균매출'].apply(format_amount)
        fw_display['23FW_평균매출'] = fw_display['23FW_평균매출'].apply(format_amount)
        
        # 신장율 컬럼 추가 (색상 적용을 위해)
        fw_display['총매출_신장율_표시'] = fw_display['총매출_신장율'].apply(format_growth)
        fw_display['평균매출_신장율_표시'] = fw_display['평균매출_신장율'].apply(format_growth)
        
        # 표시용 컬럼만 선택
        fw_display_columns = ['유통사', '매장수', '24FW_총매출', '23FW_총매출', '총매출_신장율_표시', 
                             '24FW_평균매출', '23FW_평균매출', '평균매출_신장율_표시']
        fw_display = fw_display[fw_display_columns]
        
        # 컬럼명 변경
        fw_display.columns = ['유통사', '매장수', '24FW 총매출', '23FW 총매출', '총매출 신장율', 
                             '24FW 평균매출', '23FW 평균매출', '평균매출 신장율']
        
        # FW 시즌 표 표시
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        st.dataframe(fw_display, width='stretch', hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 요약 정보
        st.markdown('<h3>📈 요약 정보</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**SS 시즌 요약**")
            ss_total_current = ss_analysis['25SS_총매출'].sum()
            ss_total_previous = ss_analysis['24SS_총매출'].sum()
            ss_total_growth = ((ss_total_current - ss_total_previous) / ss_total_previous * 100) if ss_total_previous > 0 else 0
            
            # 평균 매출 계산
            ss_avg_current = ss_analysis['25SS_평균매출'].mean()
            ss_avg_previous = ss_analysis['24SS_평균매출'].mean()
            ss_avg_growth = ((ss_avg_current - ss_avg_previous) / ss_avg_previous * 100) if ss_avg_previous > 0 else 0
            
            st.metric(
                "총 매출",
                f"{format_amount(ss_total_current)}({format_amount(ss_total_previous)}){format_growth(ss_total_growth)}"
            )
            
            st.metric(
                "평균 매출",
                f"{format_amount(ss_avg_current)}({format_amount(ss_avg_previous)}){format_growth(ss_avg_growth)}"
            )
        
        with col2:
            st.markdown("**FW 시즌 요약**")
            fw_total_current = fw_analysis['24FW_총매출'].sum()
            fw_total_previous = fw_analysis['23FW_총매출'].sum()
            fw_total_growth = ((fw_total_current - fw_total_previous) / fw_total_previous * 100) if fw_total_previous > 0 else 0
            
            # 평균 매출 계산
            fw_avg_current = fw_analysis['24FW_평균매출'].mean()
            fw_avg_previous = fw_analysis['23FW_평균매출'].mean()
            fw_avg_growth = ((fw_avg_current - fw_avg_previous) / fw_avg_previous * 100) if fw_avg_previous > 0 else 0
            
            st.metric(
                "총 매출",
                f"{format_amount(fw_total_current)}({format_amount(fw_total_previous)}){format_growth(fw_total_growth)}"
            )
            
            st.metric(
                "평균 매출",
                f"{format_amount(fw_avg_current)}({format_amount(fw_avg_previous)}){format_growth(fw_avg_growth)}"
            )
    
    else:
        st.warning("선택된 필터 조건에 해당하는 디스커버리 데이터가 없습니다.")
    
    # 동업계 MS 현황
    st.markdown('<h2 class="section-header">📊 동업계 MS 현황</h2>', unsafe_allow_html=True)
    
    # 브랜드별 분석 데이터 생성 함수
    def create_brand_analysis(season_current, season_previous, season_name, analysis_type='total'):
        brand_summary = []
        
        for brand in filtered_df['브랜드'].unique():
            brand_data = filtered_df[filtered_df['브랜드'] == brand]
            
            if analysis_type == 'total':
                # 총 매출 분석
                current_value = brand_data[season_current].sum()
                previous_value = brand_data[season_previous].sum()
            else:
                # 평균 매출 분석 (0인 매장 제외)
                current_data = brand_data[brand_data[season_current] > 0]
                previous_data = brand_data[brand_data[season_previous] > 0]
                
                current_value = current_data[season_current].mean() if len(current_data) > 0 else 0
                previous_value = previous_data[season_previous].mean() if len(previous_data) > 0 else 0
            
            growth = ((current_value - previous_value) / previous_value * 100) if previous_value > 0 else 0
            
            brand_summary.append({
                '브랜드명': brand,
                f'{season_current}_매출': current_value,
                f'{season_previous}_매출': previous_value,
                '신장율': growth
            })
        
        # 매출 기준으로 정렬
        brand_df = pd.DataFrame(brand_summary)
        brand_df = brand_df.sort_values(f'{season_current}_매출', ascending=False).reset_index(drop=True)
        
        # 순위 추가 (전년 대비 순위 변화 계산)
        brand_df_prev = brand_df.copy()
        brand_df_prev = brand_df_prev.sort_values(f'{season_previous}_매출', ascending=False).reset_index(drop=True)
        brand_df_prev['전년순위'] = brand_df_prev.index + 1
        
        # 현재 순위와 전년 순위 매핑
        rank_mapping = dict(zip(brand_df_prev['브랜드명'], brand_df_prev['전년순위']))
        brand_df['전년순위'] = brand_df['브랜드명'].map(rank_mapping)
        brand_df['현재순위'] = brand_df.index + 1
        
        # 순위 변화 표시
        def format_rank_change(row):
            current_rank = row['현재순위']
            prev_rank = row['전년순위']
            if pd.isna(prev_rank):
                return f"{current_rank}(-)"
            change = prev_rank - current_rank
            if change > 0:
                return f"{current_rank}(▲{int(change)})"
            elif change < 0:
                return f"{current_rank}(▼{int(abs(change))})"
            else:
                return f"{current_rank}(-)"
        
        brand_df['순위'] = brand_df.apply(format_rank_change, axis=1)
        
        return brand_df
    
    # SS 시즌 MS 현황
    st.markdown('<h3>📊 SS 시즌 MS 현황</h3>', unsafe_allow_html=True)
    
    # 매출 유형 선택
    col1, col2 = st.columns(2)
    with col1:
        ss_sales_type = st.radio("SS 시즌 매출 유형 선택", ["총 매출", "평균 매출"], key="ss_sales_type")
    with col2:
        st.write("")  # 빈 공간
    
    # 분석 유형 결정
    ss_analysis_type = 'total' if ss_sales_type == "총 매출" else 'average'
    
    ss_brand_analysis = create_brand_analysis('25SS', '24SS', 'SS', ss_analysis_type)
    
    # SS 시즌 차트 생성 (최근 시즌과 전년 시즌 매출 함께 표시)
    st.markdown(f'<h4>📈 SS 시즌 브랜드별 {ss_sales_type} 차트</h4>', unsafe_allow_html=True)
    
    # 차트용 데이터 준비 - 최근 시즌과 전년 시즌을 함께 표시
    chart_data_ss = ss_brand_analysis.copy()
    
    # 데이터를 long format으로 변환
    chart_data_long = []
    for _, row in chart_data_ss.iterrows():
        chart_data_long.append({
            '브랜드명': row['브랜드명'],
            '시즌': '25SS',
            '매출': row['25SS_매출'],
            '순위': row['순위'],
            '신장율': row['신장율']
        })
        chart_data_long.append({
            '브랜드명': row['브랜드명'],
            '시즌': '24SS',
            '매출': row['24SS_매출'],
            '순위': row['순위'],
            '신장율': row['신장율']
        })
    
    chart_df_ss = pd.DataFrame(chart_data_long)
    
    # 디스커버리 브랜드 강조를 위한 색상 설정
    fig_ss = px.bar(
        chart_df_ss, 
        x='브랜드명', 
        y='매출',
        color='시즌',
        title=f'SS 시즌 브랜드별 {ss_sales_type} 비교 (25SS vs 24SS)',
        color_discrete_map={'25SS': '#FF6B6B', '24SS': '#4ECDC4'},
        text_auto=True,
        barmode='group'
    )
    
    # 디스커버리 브랜드 강조 (굵은 글씨)
    fig_ss.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        height=500,
        font=dict(size=12)
    )
    
    # 디스커버리 브랜드의 막대에 굵은 테두리 추가
    for i, trace in enumerate(fig_ss.data):
        if trace.name == '25SS':
            # 디스커버리 브랜드 찾기
            discovery_indices = [j for j, brand in enumerate(chart_df_ss[chart_df_ss['시즌'] == '25SS']['브랜드명']) if brand == '디스커버리']
            if discovery_indices:
                trace.marker.line.width = [3 if j in discovery_indices else 1 for j in range(len(trace.x))]
                trace.marker.line.color = ['#FF0000' if j in discovery_indices else '#000000' for j in range(len(trace.x))]
        elif trace.name == '24SS':
            # 디스커버리 브랜드 찾기
            discovery_indices = [j for j, brand in enumerate(chart_df_ss[chart_df_ss['시즌'] == '24SS']['브랜드명']) if brand == '디스커버리']
            if discovery_indices:
                trace.marker.line.width = [3 if j in discovery_indices else 1 for j in range(len(trace.x))]
                trace.marker.line.color = ['#FF0000' if j in discovery_indices else '#000000' for j in range(len(trace.x))]
    
    st.plotly_chart(fig_ss, width='stretch', config={'displayModeBar': False})
    
    # SS 시즌 표시용 데이터 준비 (색상 코딩 포함)
    ss_brand_display = ss_brand_analysis.copy()
    ss_brand_display['25SS_매출'] = ss_brand_display['25SS_매출'].apply(format_amount)
    ss_brand_display['24SS_매출'] = ss_brand_display['24SS_매출'].apply(format_amount)
    
    # 순위 변화에 색상 적용
    def format_rank_with_color(row):
        rank_text = row['순위']
        if '▲' in rank_text:
            return f"<span style='color: #007bff; font-weight: bold;'>{rank_text}</span>"
        elif '▼' in rank_text:
            return f"<span style='color: #dc3545; font-weight: bold;'>{rank_text}</span>"
        else:
            return f"<span style='color: #6c757d;'>{rank_text}</span>"
    
    # 신장율에 색상 적용
    def format_growth_with_color(growth):
        if pd.isna(growth):
            return "<span style='color: #6c757d;'>0.00%</span>"
        if growth > 0:
            return f"<span style='color: #007bff; font-weight: bold;'>▲{growth:.1f}%</span>"
        else:
            return f"<span style='color: #dc3545; font-weight: bold;'>▼{abs(growth):.1f}%</span>"
    
    # 브랜드명에 디스커버리 강조
    def format_brand_name(brand):
        if brand == '디스커버리':
            return f"<span style='font-weight: bold; color: #FF0000;'>{brand}</span>"
        else:
            return brand
    
    ss_brand_display['순위_색상'] = ss_brand_display.apply(format_rank_with_color, axis=1)
    ss_brand_display['신장율_색상'] = ss_brand_display['신장율'].apply(format_growth_with_color)
    ss_brand_display['브랜드명_강조'] = ss_brand_display['브랜드명'].apply(format_brand_name)
    
    # 표시용 컬럼만 선택
    ss_brand_columns = ['순위_색상', '브랜드명_강조', '25SS_매출', '24SS_매출', '신장율_색상']
    ss_brand_display = ss_brand_display[ss_brand_columns]
    
    # 컬럼명 변경
    ss_brand_display.columns = ['순위', '브랜드명', '25SS 매출', '24SS 매출', '신장율']
    
    # SS 시즌 표 표시
    st.markdown(f'<h4>📊 SS 시즌 브랜드별 {ss_sales_type} 표</h4>', unsafe_allow_html=True)
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    st.markdown(ss_brand_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # FW 시즌 MS 현황
    st.markdown('<h3>📊 FW 시즌 MS 현황</h3>', unsafe_allow_html=True)
    
    # 매출 유형 선택
    col1, col2 = st.columns(2)
    with col1:
        fw_sales_type = st.radio("FW 시즌 매출 유형 선택", ["총 매출", "평균 매출"], key="fw_sales_type")
    with col2:
        st.write("")  # 빈 공간
    
    # 분석 유형 결정
    fw_analysis_type = 'total' if fw_sales_type == "총 매출" else 'average'
    
    fw_brand_analysis = create_brand_analysis('24FW', '23FW', 'FW', fw_analysis_type)
    
    # FW 시즌 차트 생성 (최근 시즌과 전년 시즌 매출 함께 표시)
    st.markdown(f'<h4>📈 FW 시즌 브랜드별 {fw_sales_type} 차트</h4>', unsafe_allow_html=True)
    
    # 차트용 데이터 준비 - 최근 시즌과 전년 시즌을 함께 표시
    chart_data_fw = fw_brand_analysis.copy()
    
    # 데이터를 long format으로 변환
    chart_data_long_fw = []
    for _, row in chart_data_fw.iterrows():
        chart_data_long_fw.append({
            '브랜드명': row['브랜드명'],
            '시즌': '24FW',
            '매출': row['24FW_매출'],
            '순위': row['순위'],
            '신장율': row['신장율']
        })
        chart_data_long_fw.append({
            '브랜드명': row['브랜드명'],
            '시즌': '23FW',
            '매출': row['23FW_매출'],
            '순위': row['순위'],
            '신장율': row['신장율']
        })
    
    chart_df_fw = pd.DataFrame(chart_data_long_fw)
    
    # 디스커버리 브랜드 강조를 위한 색상 설정
    fig_fw = px.bar(
        chart_df_fw, 
        x='브랜드명', 
        y='매출',
        color='시즌',
        title=f'FW 시즌 브랜드별 {fw_sales_type} 비교 (24FW vs 23FW)',
        color_discrete_map={'24FW': '#FF6B6B', '23FW': '#4ECDC4'},
        text_auto=True,
        barmode='group'
    )
    
    # 디스커버리 브랜드 강조 (굵은 글씨)
    fig_fw.update_layout(
        xaxis_tickangle=-45,
        showlegend=True,
        height=500,
        font=dict(size=12)
    )
    
    # 디스커버리 브랜드의 막대에 굵은 테두리 추가
    for i, trace in enumerate(fig_fw.data):
        if trace.name == '24FW':
            # 디스커버리 브랜드 찾기
            discovery_indices = [j for j, brand in enumerate(chart_df_fw[chart_df_fw['시즌'] == '24FW']['브랜드명']) if brand == '디스커버리']
            if discovery_indices:
                trace.marker.line.width = [3 if j in discovery_indices else 1 for j in range(len(trace.x))]
                trace.marker.line.color = ['#FF0000' if j in discovery_indices else '#000000' for j in range(len(trace.x))]
        elif trace.name == '23FW':
            # 디스커버리 브랜드 찾기
            discovery_indices = [j for j, brand in enumerate(chart_df_fw[chart_df_fw['시즌'] == '23FW']['브랜드명']) if brand == '디스커버리']
            if discovery_indices:
                trace.marker.line.width = [3 if j in discovery_indices else 1 for j in range(len(trace.x))]
                trace.marker.line.color = ['#FF0000' if j in discovery_indices else '#000000' for j in range(len(trace.x))]
    
    st.plotly_chart(fig_fw, width='stretch', config={'displayModeBar': False})
    
    # FW 시즌 표시용 데이터 준비 (색상 코딩 포함)
    fw_brand_display = fw_brand_analysis.copy()
    fw_brand_display['24FW_매출'] = fw_brand_display['24FW_매출'].apply(format_amount)
    fw_brand_display['23FW_매출'] = fw_brand_display['23FW_매출'].apply(format_amount)
    
    fw_brand_display['순위_색상'] = fw_brand_display.apply(format_rank_with_color, axis=1)
    fw_brand_display['신장율_색상'] = fw_brand_display['신장율'].apply(format_growth_with_color)
    fw_brand_display['브랜드명_강조'] = fw_brand_display['브랜드명'].apply(format_brand_name)
    
    # 표시용 컬럼만 선택
    fw_brand_columns = ['순위_색상', '브랜드명_강조', '24FW_매출', '23FW_매출', '신장율_색상']
    fw_brand_display = fw_brand_display[fw_brand_columns]
    
    # 컬럼명 변경
    fw_brand_display.columns = ['순위', '브랜드명', '24FW 매출', '23FW 매출', '신장율']
    
    # FW 시즌 표 표시
    st.markdown(f'<h4>📊 FW 시즌 브랜드별 {fw_sales_type} 표</h4>', unsafe_allow_html=True)
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    st.markdown(fw_brand_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("데이터를 로드할 수 없습니다. CSV 파일을 확인해주세요.")