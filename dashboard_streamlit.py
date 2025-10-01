import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
        return f"<span style='color: #0066ff; font-weight: bold;'>▲ {growth:+.1f}%</span>"
    elif growth < 0:
        return f"<span style='color: #ff0000; font-weight: bold;'>▼ {growth:+.1f}%</span>"
    else:
        return f"<span style='color: #666;'>0.0%</span>"

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
    
    # ===========================================
    # 1. 아울렛 동향 분석
    # ===========================================
    st.markdown('<h2 class="section-header">🏪 아울렛 동향 분석</h2>', unsafe_allow_html=True)
    
    # 디스커버리 데이터만 필터링
    discovery_data = filtered_df[filtered_df['브랜드'] == '디스커버리']
    
    if not discovery_data.empty:
        # 시즌 선택
        season_type = st.radio("시즌 선택", ["SS 시즌", "FW 시즌"], horizontal=True)
        
        # 데이터 타입 선택
        data_type = st.radio("데이터 타입 선택", ["총매출", "평균매출"], horizontal=True)
        
        # 유통사별 데이터 집계
        distributor_summary = []
        for distributor in discovery_data['유통사'].unique():
            dist_data = discovery_data[discovery_data['유통사'] == distributor]
            store_count = dist_data['매장명'].nunique()
            
            if season_type == "SS 시즌":
                current_sales = dist_data['25SS'].sum()
                prev_sales = dist_data['24SS'].sum()
                current_label = "25SS"
                prev_label = "24SS"
            else:  # FW 시즌
                current_sales = dist_data['24FW'].sum()
                prev_sales = dist_data['23FW'].sum()
                current_label = "24FW"
                prev_label = "23FW"
            
            # 평균 매출 계산 (매출이 0이 아닌 매장만)
            if data_type == "평균매출":
                valid_stores_current = len(dist_data[dist_data[current_label] > 0])
                valid_stores_prev = len(dist_data[dist_data[prev_label] > 0])
                current_avg = current_sales / valid_stores_current if valid_stores_current > 0 else 0
                prev_avg = prev_sales / valid_stores_prev if valid_stores_prev > 0 else 0
            else:
                current_avg = current_sales
                prev_avg = prev_sales
            
            # 성장률 계산
            growth = ((current_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
            
            distributor_summary.append({
                '유통사': distributor,
                '매장수': store_count,
                '현재매출': current_avg,
                '전년매출': prev_avg,
                '성장률': growth
            })
        
        summary_df = pd.DataFrame(distributor_summary)
        summary_df = summary_df.sort_values('현재매출', ascending=False).reset_index(drop=True)
        
        # 차트 생성
        fig = go.Figure()
        
        # 디스커버리 강조 색상
        colors = ['#FF1744' if '디스커버리' in dist else '#E3F2FD' for dist in summary_df['유통사']]
        
        fig.add_trace(go.Bar(
            name='현재 시즌',
            x=summary_df['유통사'],
            y=summary_df['현재매출'] / 100000000,
            marker_color=colors,
            text=[f"{format_growth_with_color(row['성장률'])}" for _, row in summary_df.iterrows()],
            textposition='outside',
            textfont=dict(size=10)
        ))
        
        fig.add_trace(go.Bar(
            name='전년 시즌',
            x=summary_df['유통사'],
            y=summary_df['전년매출'] / 100000000,
            marker_color=['#FF5722' if '디스커버리' in dist else '#BBDEFB' for dist in summary_df['유통사']],
            opacity=0.7
        ))
        
        fig.update_layout(
            title=f'유통사별 디스커버리 {season_type} {data_type} 비교',
            xaxis_title='유통사',
            yaxis_title=f'{data_type} (억원)',
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 요약 테이블
        st.subheader("📊 요약 테이블")
        
        display_df = summary_df.copy()
        display_df['현재매출'] = display_df['현재매출'].apply(format_to_hundred_million)
        display_df['전년매출'] = display_df['전년매출'].apply(format_to_hundred_million)
        display_df['성장률'] = display_df['성장률'].apply(format_growth_with_color)
        display_df.columns = ['유통사', '매장수', f'{current_label} {data_type}', f'{prev_label} {data_type}', '성장률']
        
        # 디스커버리 강조
        display_df['유통사'] = display_df['유통사'].apply(lambda x: f"<b>{x}</b>" if '디스커버리' in x else x)
        
        st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # ===========================================
    # 2. 동업계 MS 현황
    # ===========================================
    st.markdown('<h2 class="section-header">🏢 동업계 MS 현황</h2>', unsafe_allow_html=True)
    
    # MS 시즌 선택
    ms_season = st.radio("MS 시즌 선택", ["SS 시즌", "FW 시즌"], horizontal=True, key="ms_season")
    ms_data_type = st.radio("MS 데이터 타입 선택", ["총매출", "평균매출"], horizontal=True, key="ms_data_type")
    
    # 브랜드별 데이터 집계
    brand_summary = []
    for brand in filtered_df['브랜드'].unique():
        brand_data = filtered_df[filtered_df['브랜드'] == brand]
        
        if ms_season == "SS 시즌":
            current_sales = brand_data['25SS'].sum()
            prev_sales = brand_data['24SS'].sum()
            current_label = "25SS"
            prev_label = "24SS"
        else:  # FW 시즌
            current_sales = brand_data['24FW'].sum()
            prev_sales = brand_data['23FW'].sum()
            current_label = "24FW"
            prev_label = "23FW"
        
        # 평균 매출 계산
        if ms_data_type == "평균매출":
            valid_stores_current = len(brand_data[brand_data[current_label] > 0])
            valid_stores_prev = len(brand_data[brand_data[prev_label] > 0])
            current_avg = current_sales / valid_stores_current if valid_stores_current > 0 else 0
            prev_avg = prev_sales / valid_stores_prev if valid_stores_prev > 0 else 0
        else:
            current_avg = current_sales
            prev_avg = prev_sales
        
        # 성장률 계산
        growth = ((current_avg - prev_avg) / prev_avg * 100) if prev_avg > 0 else 0
        
        brand_summary.append({
            '브랜드': brand,
            '현재매출': current_avg,
            '전년매출': prev_avg,
            '성장률': growth
        })
    
    brand_df = pd.DataFrame(brand_summary)
    brand_df = brand_df.sort_values('현재매출', ascending=False).reset_index(drop=True)
    
    # MS 차트 생성
    fig_ms = go.Figure()
    
    # 디스커버리 강조 색상
    colors = ['#FF1744' if brand == '디스커버리' else '#E3F2FD' for brand in brand_df['브랜드']]
    
    fig_ms.add_trace(go.Bar(
        name='현재 시즌',
        x=brand_df['브랜드'],
        y=brand_df['현재매출'] / 100000000,
        marker_color=colors,
        text=[f"{format_growth_with_color(row['성장률'])}" for _, row in brand_df.iterrows()],
        textposition='outside',
        textfont=dict(size=10)
    ))
    
    fig_ms.add_trace(go.Bar(
        name='전년 시즌',
        x=brand_df['브랜드'],
        y=brand_df['전년매출'] / 100000000,
        marker_color=['#FF5722' if brand == '디스커버리' else '#BBDEFB' for brand in brand_df['브랜드']],
        opacity=0.7
    ))
    
    fig_ms.update_layout(
        title=f'브랜드별 {ms_season} {ms_data_type} 현황',
        xaxis_title='브랜드',
        yaxis_title=f'{ms_data_type} (억원)',
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig_ms, use_container_width=True)
    
    # MS 요약 테이블
    st.subheader("📊 브랜드별 매출 순위")
    
    # 순위 계산
    brand_df['순위'] = range(1, len(brand_df) + 1)
    
    # 전년 순위 계산
    prev_year_df = brand_df.copy()
    prev_year_df = prev_year_df.sort_values('전년매출', ascending=False).reset_index(drop=True)
    prev_year_df['전년순위'] = range(1, len(prev_year_df) + 1)
    
    # 순위 변화 계산
    rank_mapping = dict(zip(brand_df['브랜드'], brand_df['순위']))
    prev_rank_mapping = dict(zip(prev_year_df['브랜드'], prev_year_df['전년순위']))
    
    def format_rank_change(brand):
        current = rank_mapping[brand]
        prev = prev_rank_mapping[brand]
        change = prev - current
        
        if change > 0:
            return f"{current}<span style='color: #0066ff; font-weight: bold;'>(▲{change})</span>"
        elif change < 0:
            return f"{current}<span style='color: #ff0000; font-weight: bold;'>(▼{abs(change)})</span>"
        else:
            return f"{current}(-)"
    
    display_brand_df = brand_df.copy()
    display_brand_df['현재매출'] = display_brand_df['현재매출'].apply(format_to_hundred_million)
    display_brand_df['전년매출'] = display_brand_df['전년매출'].apply(format_to_hundred_million)
    display_brand_df['성장률'] = display_brand_df['성장률'].apply(format_growth_with_color)
    display_brand_df['순위변화'] = display_brand_df['브랜드'].apply(format_rank_change)
    
    # 컬럼명 변경
    display_brand_df.columns = ['브랜드', f'{current_label} {ms_data_type}', f'{prev_label} {ms_data_type}', '성장률', '순위', '순위변화']
    
    # 디스커버리 강조
    display_brand_df['브랜드'] = display_brand_df['브랜드'].apply(lambda x: f"<b>{x}</b>" if x == '디스커버리' else x)
    
    # 컬럼 순서 조정
    display_brand_df = display_brand_df[['순위변화', '브랜드', f'{current_label} {ms_data_type}', f'{prev_label} {ms_data_type}', '성장률']]
    
    st.markdown(display_brand_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # ===========================================
    # 3. 아울렛 매장당 효율
    # ===========================================
    st.markdown('<h2 class="section-header">🏪 아울렛 매장당 효율</h2>', unsafe_allow_html=True)
    
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
                    sales_current = store_rows['25SS'].sum()
                    sales_prev = store_rows['24SS'].sum()
                    current_label = "25SS"
                    prev_label = "24SS"
                else:  # FW시즌
                    # FW 시즌 데이터
                    sales_current = store_rows['24FW'].sum()
                    sales_prev = store_rows['23FW'].sum()
                    current_label = "24FW"
                    prev_label = "23FW"
                
                # 평당 매출 계산 (백만원 단위)
                efficiency_current = (sales_current / area_pyeong) / 1000000  # 백만원/평
                efficiency_prev = (sales_prev / area_pyeong) / 1000000  # 백만원/평
                
                # 신장율 계산
                efficiency_growth = ((efficiency_current - efficiency_prev) / efficiency_prev * 100) if efficiency_prev > 0 else 0
                sales_growth = ((sales_current - sales_prev) / sales_prev * 100) if sales_prev > 0 else 0
                
                store_efficiency_data.append({
                    '매장명': store_name,
                    '면적(평)': area_pyeong,
                    '현재_평당매출': efficiency_current,
                    '전년_평당매출': efficiency_prev,
                    '평당매출_신장율': efficiency_growth,
                    '현재_총매출': sales_current,
                    '전년_총매출': sales_prev,
                    '총매출_신장율': sales_growth
                })
        
        if store_efficiency_data:
            efficiency_df = pd.DataFrame(store_efficiency_data)
            
            # 평당 매출 기준으로 정렬
            efficiency_df = efficiency_df.sort_values('현재_평당매출', ascending=False).reset_index(drop=True)
            
            # 전년 순위 계산
            prev_year_df = efficiency_df.copy()
            prev_year_df = prev_year_df.sort_values('전년_평당매출', ascending=False).reset_index(drop=True)
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
                    return f"{current}<span style='color: #0066ff; font-weight: bold;'>(▲{change})</span>"
                elif change < 0:
                    return f"{current}<span style='color: #ff0000; font-weight: bold;'>(▼{abs(change)})</span>"
                else:
                    return f"{current}(-)"
            
            # 백만원 단위 포맷팅 함수
            def format_million(value):
                return f"{value:.1f}백만원"
            
            # 테이블 데이터 준비
            table_data = []
            for idx, row in efficiency_df.iterrows():
                table_data.append({
                    '순위': format_rank_change(row['매장명']),
                    '매장명': row['매장명'],
                    '면적(평)': f"{row['면적(평)']:.1f}평",
                    f'{current_label} 평당 매출': format_million(row['현재_평당매출']),
                    f'{prev_label} 평당 매출': format_million(row['전년_평당매출']),
                    '평당매출 신장율': format_growth_with_color(row['평당매출_신장율']),
                    f'{current_label} 총 매출': format_million(row['현재_총매출'] / 1000000),
                    f'{prev_label} 총 매출': format_million(row['전년_총매출'] / 1000000),
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

else:
    st.info("👆 사이드바에서 CSV 파일을 업로드하여 대시보드를 시작하세요.")
    
    # 사용법 안내
    st.markdown("""
    ## 📋 사용법 안내
    
    1. **파일 업로드**: 사이드바에서 'DX OUTLET MS DB.csv' 파일을 업로드하세요
    2. **필터링**: 유통사와 매장명을 선택하여 데이터를 필터링할 수 있습니다
    3. **아울렛 동향**: 디스커버리 브랜드의 시즌별 매출 흐름을 확인하세요
    4. **동업계 MS 현황**: 브랜드별 매출 순위 및 경쟁 분석을 확인하세요
    5. **아울렛 매장당 효율**: 매장별 평당 매출 효율성을 분석하세요
    
    ## 📊 분석 내용
    
    - **아울렛 동향**: 유통사별 디스커버리 매출 비교
    - **동업계 MS 현황**: 브랜드별 매출 순위 및 순위 변화
    - **아울렛 매장당 효율**: 매장별 평당 매출 효율성 분석
    """)