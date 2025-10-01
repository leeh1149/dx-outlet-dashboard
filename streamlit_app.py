import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="DX OUTLET 매출 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 로드 함수
@st.cache_data
def load_data():
    """CSV 파일을 로드하고 데이터를 전처리합니다."""
    try:
        df = pd.read_csv('DX OUTLET MS DB.csv')
        
        # 매출 컬럼을 숫자형으로 변환
        sales_columns = ['23SS', '23FW', '24SS', '24FW', '25SS']
        for col in sales_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 매장 면적을 숫자형으로 변환
        df['매장 면적'] = pd.to_numeric(df['매장 면적'], errors='coerce')
        
        # 결측값 처리
        df = df.fillna(0)
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return None

# 메인 함수
def main():
    # 헤더
    st.title("📊 DX OUTLET 매출 분석 대시보드")
    st.markdown("---")
    
    # 데이터 로드
    df = load_data()
    if df is None:
        st.stop()
    
    # 사이드바 필터
    st.sidebar.header("🔍 필터 옵션")
    
    # 유통사 필터
    distributors = ['전체'] + sorted(df['유통사'].unique().tolist())
    selected_distributor = st.sidebar.selectbox("유통사 선택", distributors)
    
    # 매장 필터
    if selected_distributor != '전체':
        store_options = ['전체'] + sorted(df[df['유통사'] == selected_distributor]['매장명'].unique().tolist())
    else:
        store_options = ['전체'] + sorted(df['매장명'].unique().tolist())
    
    selected_store = st.sidebar.selectbox("매장 선택", store_options)
    
    # 브랜드 필터
    brand_options = ['전체'] + sorted(df['브랜드'].unique().tolist())
    selected_brand = st.sidebar.selectbox("브랜드 선택", brand_options)
    
    # 데이터 필터링
    filtered_df = df.copy()
    
    if selected_distributor != '전체':
        filtered_df = filtered_df[filtered_df['유통사'] == selected_distributor]
    
    if selected_store != '전체':
        filtered_df = filtered_df[filtered_df['매장명'] == selected_store]
    
    if selected_brand != '전체':
        filtered_df = filtered_df[filtered_df['브랜드'] == selected_brand]
    
    # 메트릭 표시
    st.subheader("📈 주요 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_stores = len(filtered_df['매장명'].unique())
        st.metric("총 매장 수", f"{total_stores}개")
    
    with col2:
        total_brands = len(filtered_df['브랜드'].unique())
        st.metric("총 브랜드 수", f"{total_brands}개")
    
    with col3:
        total_sales_25ss = filtered_df['25SS'].sum()
        st.metric("25SS 총 매출", f"{total_sales_25ss:,.0f}원")
    
    with col4:
        avg_store_area = filtered_df['매장 면적'].mean()
        if not pd.isna(avg_store_area):
            st.metric("평균 매장 면적", f"{avg_store_area:.1f}㎡")
        else:
            st.metric("평균 매장 면적", "N/A")
    
    st.markdown("---")
    
    # 탭으로 구분된 분석
    tab1, tab2, tab3, tab4 = st.tabs(["📊 시계열 분석", "🏪 매장별 분석", "🏷️ 브랜드별 분석", "📋 데이터 테이블"])
    
    with tab1:
        st.subheader("시계열 매출 분석")
        
        # 시계열 데이터 준비
        sales_columns = ['23SS', '23FW', '24SS', '24FW', '25SS']
        sales_data = filtered_df[sales_columns].sum()
        
        # 시계열 차트
        fig = px.line(
            x=['23SS', '23FW', '24SS', '24FW', '25SS'],
            y=sales_data.values,
            title="시계열별 총 매출 추이",
            labels={'x': '시즌', 'y': '매출 (원)'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # 시즌별 매출 비교 (바 차트)
        fig_bar = px.bar(
            x=['23SS', '23FW', '24SS', '24FW', '25SS'],
            y=sales_data.values,
            title="시즌별 매출 비교",
            labels={'x': '시즌', 'y': '매출 (원)'},
            color=sales_data.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.subheader("매장별 분석")
        
        # 매장별 25SS 매출 상위 10개
        store_sales = filtered_df.groupby('매장명')['25SS'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=store_sales.values,
            y=store_sales.index,
            orientation='h',
            title="매장별 25SS 매출 TOP 10",
            labels={'x': '매출 (원)', 'y': '매장명'}
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # 매장 면적 vs 매출 산점도
        area_sales_df = filtered_df.groupby('매장명').agg({
            '매장 면적': 'first',
            '25SS': 'sum'
        }).dropna()
        
        if not area_sales_df.empty:
            fig_scatter = px.scatter(
                area_sales_df,
                x='매장 면적',
                y='25SS',
                title="매장 면적 vs 25SS 매출",
                labels={'매장 면적': '매장 면적 (㎡)', '25SS': '25SS 매출 (원)'},
                hover_data={'매장명': True}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
    
    with tab3:
        st.subheader("브랜드별 분석")
        
        # 브랜드별 25SS 매출 상위 10개
        brand_sales = filtered_df.groupby('브랜드')['25SS'].sum().sort_values(ascending=False).head(10)
        
        fig = px.pie(
            values=brand_sales.values,
            names=brand_sales.index,
            title="브랜드별 25SS 매출 비중 (TOP 10)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 브랜드별 시계열 매출 히트맵
        brand_season_data = filtered_df.groupby('브랜드')[sales_columns].sum()
        brand_season_data = brand_season_data.sort_values('25SS', ascending=False).head(15)
        
        fig_heatmap = px.imshow(
            brand_season_data.values,
            x=sales_columns,
            y=brand_season_data.index,
            title="브랜드별 시계열 매출 히트맵 (TOP 15)",
            color_continuous_scale='Blues',
            aspect='auto'
        )
        fig_heatmap.update_layout(height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab4:
        st.subheader("데이터 테이블")
        
        # 필터링된 데이터 표시
        st.write(f"총 {len(filtered_df)}개의 레코드가 표시됩니다.")
        
        # 컬럼 선택
        display_columns = st.multiselect(
            "표시할 컬럼을 선택하세요:",
            options=df.columns.tolist(),
            default=['유통사', '매장명', '브랜드', '25SS', '24FW', '24SS', '23FW', '23SS']
        )
        
        if display_columns:
            st.dataframe(
                filtered_df[display_columns],
                use_container_width=True,
                height=400
            )
            
            # CSV 다운로드 버튼
            csv = filtered_df[display_columns].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 필터링된 데이터 다운로드",
                data=csv,
                file_name=f"filtered_outlet_data_{selected_distributor}_{selected_store}_{selected_brand}.csv",
                mime="text/csv"
            )
    
    # 푸터
    st.markdown("---")
    st.markdown("### 📝 데이터 정보")
    st.info("""
    - **데이터 출처**: DX OUTLET MS DB
    - **업데이트**: 실시간
    - **포함 정보**: 아울렛 매장의 브랜드별 시즌 매출 데이터
    - **시즌 구분**: SS(Spring/Summer), FW(Fall/Winter)
    """)

if __name__ == "__main__":
    main()
