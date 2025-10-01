import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="DX OUTLET 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 로드 함수
@st.cache_data
def load_data():
    df = pd.read_csv('DX OUTLET MS DB.csv')
    return df

# 데이터 로드
df = load_data()

# 사이드바 - 필터
st.sidebar.header("📋 필터 설정")

# 유통사 선택
distributors = df['유통사'].unique().tolist()
selected_distributor = st.sidebar.selectbox(
    "유통사 선택",
    options=['전체'] + distributors,
    index=0
)

# 매장명 선택 (유통사에 따라 필터링)
if selected_distributor == '전체':
    stores = df['매장명'].unique().tolist()
else:
    stores = df[df['유통사'] == selected_distributor]['매장명'].unique().tolist()

selected_store = st.sidebar.selectbox(
    "매장명 선택",
    options=['전체'] + stores,
    index=0
)

# 데이터 필터링
filtered_df = df.copy()
if selected_distributor != '전체':
    filtered_df = filtered_df[filtered_df['유통사'] == selected_distributor]
if selected_store != '전체':
    filtered_df = filtered_df[filtered_df['매장명'] == selected_store]

# 메인 대시보드
st.title("🏪 DX OUTLET 매출 대시보드")
st.markdown("---")

# 선택된 필터 정보 표시
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("선택된 유통사", selected_distributor)
with col2:
    st.metric("선택된 매장", selected_store)
with col3:
    st.metric("데이터 건수", len(filtered_df))

st.markdown("---")

# 1. 아울렛 매출 흐름 (디스커버리 브랜드)
st.header("📈 아울렛 매출 흐름 - 디스커버리")

# 디스커버리 브랜드만 필터링
discovery_df = df[df['브랜드'] == '디스커버리']

# 유통사별 디스커버리 매출 데이터 계산
season_columns = ['23SS', '23FW', '24SS', '24FW', '25SS']
distributor_sales = []

for distributor in distributors:
    distributor_data = discovery_df[discovery_df['유통사'] == distributor]
    
    # 각 시즌별 합계 매출
    season_totals = []
    for season in season_columns:
        total_sales = distributor_data[season].sum()
        season_totals.append(total_sales)
    
    # 평균 매출 계산
    avg_sales = np.mean(season_totals)
    
    distributor_sales.append({
        '유통사': distributor,
        '총 매출': sum(season_totals),
        '평균 매출': avg_sales,
        '23SS': season_totals[0],
        '23FW': season_totals[1],
        '24SS': season_totals[2],
        '24FW': season_totals[3],
        '25SS': season_totals[4]
    })

distributor_df = pd.DataFrame(distributor_sales)

# 유통사별 총 매출과 평균 매출 차트
col1, col2 = st.columns(2)

with col1:
    # 총 매출 막대 차트
    fig_total = px.bar(
        distributor_df, 
        x='유통사', 
        y='총 매출',
        title="유통사별 디스커버리 총 매출",
        color='총 매출',
        color_continuous_scale='Blues'
    )
    fig_total.update_layout(
        xaxis_title="유통사",
        yaxis_title="총 매출 (원)",
        showlegend=False
    )
    st.plotly_chart(fig_total, use_container_width=True)

with col2:
    # 평균 매출 막대 차트
    fig_avg = px.bar(
        distributor_df, 
        x='유통사', 
        y='평균 매출',
        title="유통사별 디스커버리 평균 매출",
        color='평균 매출',
        color_continuous_scale='Greens'
    )
    fig_avg.update_layout(
        xaxis_title="유통사",
        yaxis_title="평균 매출 (원)",
        showlegend=False
    )
    st.plotly_chart(fig_avg, use_container_width=True)

# 시즌별 매출 흐름 라인 차트
st.subheader("시즌별 매출 흐름")

# 유통사별 시즌별 매출 데이터 준비
seasons = ['23SS', '23FW', '24SS', '24FW', '25SS']
season_labels = ['2023 SS', '2023 FW', '2024 SS', '2024 FW', '2025 SS']

fig_season = go.Figure()

for _, row in distributor_df.iterrows():
    fig_season.add_trace(go.Scatter(
        x=season_labels,
        y=[row[season] for season in seasons],
        mode='lines+markers',
        name=row['유통사'],
        line=dict(width=3),
        marker=dict(size=8)
    ))

fig_season.update_layout(
    title="유통사별 디스커버리 시즌별 매출 흐름",
    xaxis_title="시즌",
    yaxis_title="매출 (원)",
    hovermode='x unified',
    height=500
)

st.plotly_chart(fig_season, use_container_width=True)

# 유통사별 상세 데이터 테이블
st.subheader("유통사별 디스커버리 상세 매출 데이터")
distributor_display = distributor_df.copy()
distributor_display['총 매출'] = distributor_display['총 매출'].apply(lambda x: f"{x:,}")
distributor_display['평균 매출'] = distributor_display['평균 매출'].apply(lambda x: f"{x:,.0f}")

for season in seasons:
    distributor_display[season] = distributor_display[season].apply(lambda x: f"{x:,}")

st.dataframe(distributor_display, use_container_width=True)

# 2. 동업계 MS 현황
st.markdown("---")
st.header("🏢 동업계 MS 현황")

# 전년비 비교 데이터 계산
ms_analysis_data = []

# 브랜드별로 데이터 집계
brands = df['브랜드'].unique()
for brand in brands:
    brand_data = df[df['브랜드'] == brand]
    
    # SS 시즌 비교 (25SS vs 24SS)
    ss_2025 = brand_data['25SS'].sum()
    ss_2024 = brand_data['24SS'].sum()
    ss_growth = ((ss_2025 - ss_2024) / ss_2024 * 100) if ss_2024 != 0 else 0
    
    # FW 시즌 비교 (24FW vs 23FW)
    fw_2024 = brand_data['24FW'].sum()
    fw_2023 = brand_data['23FW'].sum()
    fw_growth = ((fw_2024 - fw_2023) / fw_2023 * 100) if fw_2023 != 0 else 0
    
    ms_analysis_data.append({
        '브랜드': brand,
        '25SS_매출': ss_2025,
        '24SS_매출': ss_2024,
        'SS_전년비': ss_growth,
        '24FW_매출': fw_2024,
        '23FW_매출': fw_2023,
        'FW_전년비': fw_growth,
        '총_매출': ss_2025 + fw_2024
    })

ms_df = pd.DataFrame(ms_analysis_data)
ms_df = ms_df.sort_values('총_매출', ascending=False)

# 동업계 MS 현황 차트
col1, col2 = st.columns(2)

with col1:
    # SS 시즌 전년비 차트
    fig_ss = go.Figure()
    
    fig_ss.add_trace(go.Bar(
        name='25SS',
        x=ms_df['브랜드'],
        y=ms_df['25SS_매출'],
        marker_color='lightblue'
    ))
    
    fig_ss.add_trace(go.Bar(
        name='24SS',
        x=ms_df['브랜드'],
        y=ms_df['24SS_매출'],
        marker_color='lightcoral'
    ))
    
    fig_ss.update_layout(
        title="SS 시즌 전년비 비교 (25SS vs 24SS)",
        xaxis_title="브랜드",
        yaxis_title="매출 (원)",
        barmode='group',
        xaxis_tickangle=-45,
        height=500
    )
    
    st.plotly_chart(fig_ss, use_container_width=True)

with col2:
    # FW 시즌 전년비 차트
    fig_fw = go.Figure()
    
    fig_fw.add_trace(go.Bar(
        name='24FW',
        x=ms_df['브랜드'],
        y=ms_df['24FW_매출'],
        marker_color='lightgreen'
    ))
    
    fig_fw.add_trace(go.Bar(
        name='23FW',
        x=ms_df['브랜드'],
        y=ms_df['23FW_매출'],
        marker_color='lightpink'
    ))
    
    fig_fw.update_layout(
        title="FW 시즌 전년비 비교 (24FW vs 23FW)",
        xaxis_title="브랜드",
        yaxis_title="매출 (원)",
        barmode='group',
        xaxis_tickangle=-45,
        height=500
    )
    
    st.plotly_chart(fig_fw, use_container_width=True)

# 전년비 증감률 차트
st.subheader("브랜드별 전년비 증감률")

fig_growth = go.Figure()

fig_growth.add_trace(go.Bar(
    name='SS 전년비',
    x=ms_df['브랜드'],
    y=ms_df['SS_전년비'],
    marker_color=['green' if x > 0 else 'red' for x in ms_df['SS_전년비']],
    text=[f"{x:+.1f}%" for x in ms_df['SS_전년비']],
    textposition='auto'
))

fig_growth.add_trace(go.Bar(
    name='FW 전년비',
    x=ms_df['브랜드'],
    y=ms_df['FW_전년비'],
    marker_color=['green' if x > 0 else 'red' for x in ms_df['FW_전년비']],
    text=[f"{x:+.1f}%" for x in ms_df['FW_전년비']],
    textposition='auto'
))

fig_growth.update_layout(
    title="브랜드별 전년비 증감률 (%)",
    xaxis_title="브랜드",
    yaxis_title="증감률 (%)",
    barmode='group',
    xaxis_tickangle=-45,
    height=500
)

st.plotly_chart(fig_growth, use_container_width=True)

# 동업계 MS 현황 표
st.subheader("동업계 MS 현황 상세 데이터")

# 표시용 데이터 준비
ms_display = ms_df.copy()
ms_display['25SS_매출'] = ms_display['25SS_매출'].apply(lambda x: f"{x:,}")
ms_display['24SS_매출'] = ms_display['24SS_매출'].apply(lambda x: f"{x:,}")
ms_display['24FW_매출'] = ms_display['24FW_매출'].apply(lambda x: f"{x:,}")
ms_display['23FW_매출'] = ms_display['23FW_매출'].apply(lambda x: f"{x:,}")
ms_display['SS_전년비'] = ms_display['SS_전년비'].apply(lambda x: f"{x:+.1f}%")
ms_display['FW_전년비'] = ms_display['FW_전년비'].apply(lambda x: f"{x:+.1f}%")
ms_display['총_매출'] = ms_display['총_매출'].apply(lambda x: f"{x:,}")

# 컬럼명 한글로 변경
ms_display.columns = ['브랜드', '25SS 매출', '24SS 매출', 'SS 전년비', '24FW 매출', '23FW 매출', 'FW 전년비', '총 매출']

st.dataframe(ms_display, use_container_width=True)

# 3. 시즌별 매출 흐름
st.markdown("---")
st.header("📅 시즌별 매출 흐름")

# 시즌별 매출 흐름 데이터 계산
seasonal_flow_data = []

# 브랜드별로 데이터 집계
for brand in brands:
    brand_data = df[df['브랜드'] == brand]
    
    # SS 시즌 비교 (25SS vs 24SS)
    ss_2025 = brand_data['25SS'].sum()
    ss_2024 = brand_data['24SS'].sum()
    ss_growth = ((ss_2025 - ss_2024) / ss_2024 * 100) if ss_2024 != 0 else 0
    
    # FW 시즌 비교 (24FW vs 23FW)
    fw_2024 = brand_data['24FW'].sum()
    fw_2023 = brand_data['23FW'].sum()
    fw_growth = ((fw_2024 - fw_2023) / fw_2023 * 100) if fw_2023 != 0 else 0
    
    seasonal_flow_data.append({
        '브랜드': brand,
        '25SS_매출': ss_2025,
        '24SS_매출': ss_2024,
        'SS_전년비': ss_growth,
        '24FW_매출': fw_2024,
        '23FW_매출': fw_2023,
        'FW_전년비': fw_growth,
        'SS_총매출': ss_2025 + ss_2024,
        'FW_총매출': fw_2024 + fw_2023
    })

seasonal_df = pd.DataFrame(seasonal_flow_data)
seasonal_df = seasonal_df.sort_values('SS_총매출', ascending=False)

# 시즌별 매출 흐름 차트
col1, col2 = st.columns(2)

with col1:
    # SS 시즌 흐름 차트
    fig_ss_flow = go.Figure()
    
    fig_ss_flow.add_trace(go.Bar(
        name='25SS',
        x=seasonal_df['브랜드'],
        y=seasonal_df['25SS_매출'],
        marker_color='skyblue',
        text=[f"{x:,}" for x in seasonal_df['25SS_매출']],
        textposition='auto'
    ))
    
    fig_ss_flow.add_trace(go.Bar(
        name='24SS',
        x=seasonal_df['브랜드'],
        y=seasonal_df['24SS_매출'],
        marker_color='lightcoral',
        text=[f"{x:,}" for x in seasonal_df['24SS_매출']],
        textposition='auto'
    ))
    
    fig_ss_flow.update_layout(
        title="SS 시즌 매출 흐름 (25SS vs 24SS)",
        xaxis_title="브랜드",
        yaxis_title="매출 (원)",
        barmode='group',
        xaxis_tickangle=-45,
        height=500
    )
    
    st.plotly_chart(fig_ss_flow, use_container_width=True)

with col2:
    # FW 시즌 흐름 차트
    fig_fw_flow = go.Figure()
    
    fig_fw_flow.add_trace(go.Bar(
        name='24FW',
        x=seasonal_df['브랜드'],
        y=seasonal_df['24FW_매출'],
        marker_color='lightgreen',
        text=[f"{x:,}" for x in seasonal_df['24FW_매출']],
        textposition='auto'
    ))
    
    fig_fw_flow.add_trace(go.Bar(
        name='23FW',
        x=seasonal_df['브랜드'],
        y=seasonal_df['23FW_매출'],
        marker_color='lightpink',
        text=[f"{x:,}" for x in seasonal_df['23FW_매출']],
        textposition='auto'
    ))
    
    fig_fw_flow.update_layout(
        title="FW 시즌 매출 흐름 (24FW vs 23FW)",
        xaxis_title="브랜드",
        yaxis_title="매출 (원)",
        barmode='group',
        xaxis_tickangle=-45,
        height=500
    )
    
    st.plotly_chart(fig_fw_flow, use_container_width=True)

# 시즌별 전년비 증감률 차트
st.subheader("시즌별 전년비 증감률")

fig_seasonal_growth = go.Figure()

fig_seasonal_growth.add_trace(go.Bar(
    name='SS 전년비',
    x=seasonal_df['브랜드'],
    y=seasonal_df['SS_전년비'],
    marker_color=['green' if x > 0 else 'red' for x in seasonal_df['SS_전년비']],
    text=[f"{x:+.1f}%" for x in seasonal_df['SS_전년비']],
    textposition='auto'
))

fig_seasonal_growth.add_trace(go.Bar(
    name='FW 전년비',
    x=seasonal_df['브랜드'],
    y=seasonal_df['FW_전년비'],
    marker_color=['green' if x > 0 else 'red' for x in seasonal_df['FW_전년비']],
    text=[f"{x:+.1f}%" for x in seasonal_df['FW_전년비']],
    textposition='auto'
))

fig_seasonal_growth.update_layout(
    title="시즌별 전년비 증감률 (%)",
    xaxis_title="브랜드",
    yaxis_title="증감률 (%)",
    barmode='group',
    xaxis_tickangle=-45,
    height=500
)

st.plotly_chart(fig_seasonal_growth, use_container_width=True)

# 시즌별 매출 흐름 표
st.subheader("시즌별 매출 흐름 상세 데이터")

# 표시용 데이터 준비
seasonal_display = seasonal_df.copy()
seasonal_display['25SS_매출'] = seasonal_display['25SS_매출'].apply(lambda x: f"{x:,}")
seasonal_display['24SS_매출'] = seasonal_display['24SS_매출'].apply(lambda x: f"{x:,}")
seasonal_display['24FW_매출'] = seasonal_display['24FW_매출'].apply(lambda x: f"{x:,}")
seasonal_display['23FW_매출'] = seasonal_display['23FW_매출'].apply(lambda x: f"{x:,}")
seasonal_display['SS_전년비'] = seasonal_display['SS_전년비'].apply(lambda x: f"{x:+.1f}%")
seasonal_display['FW_전년비'] = seasonal_display['FW_전년비'].apply(lambda x: f"{x:+.1f}%")
seasonal_display['SS_총매출'] = seasonal_display['SS_총매출'].apply(lambda x: f"{x:,}")
seasonal_display['FW_총매출'] = seasonal_display['FW_총매출'].apply(lambda x: f"{x:,}")

# 컬럼명 한글로 변경
seasonal_display.columns = ['브랜드', '25SS 매출', '24SS 매출', 'SS 전년비', '24FW 매출', '23FW 매출', 'FW 전년비', 'SS 총매출', 'FW 총매출']

st.dataframe(seasonal_display, use_container_width=True)

# 선택된 필터에 따른 상세 정보
if selected_distributor != '전체' or selected_store != '전체':
    st.markdown("---")
    st.header("🔍 선택된 필터 상세 정보")
    
    if selected_store != '전체':
        # 특정 매장의 브랜드별 매출
        store_brand_sales = filtered_df.groupby('브랜드')[season_columns].sum()
        store_brand_sales['총 매출'] = store_brand_sales.sum(axis=1)
        store_brand_sales = store_brand_sales.sort_values('총 매출', ascending=False)
        
        st.subheader(f"{selected_store} 브랜드별 매출")
        
        fig_brand = px.bar(
            store_brand_sales.reset_index(),
            x='브랜드',
            y='총 매출',
            title=f"{selected_store} 브랜드별 총 매출",
            color='총 매출',
            color_continuous_scale='Viridis'
        )
        fig_brand.update_layout(
            xaxis_title="브랜드",
            yaxis_title="총 매출 (원)",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_brand, use_container_width=True)
        
        # 브랜드별 상세 데이터
        st.subheader("브랜드별 상세 매출 데이터")
        brand_display = store_brand_sales.copy()
        brand_display['총 매출'] = brand_display['총 매출'].apply(lambda x: f"{x:,}")
        for season in seasons:
            brand_display[season] = brand_display[season].apply(lambda x: f"{x:,}")
        
        st.dataframe(brand_display, use_container_width=True)

# 푸터
st.markdown("---")
st.markdown("📊 **DX OUTLET 매출 대시보드** - 실시간 데이터 분석")
