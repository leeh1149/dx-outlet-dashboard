import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="DX OUTLET 매출 현황 대시보드",
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
    st.title("📊 DX OUTLET 매출 현황 대시보드")
    
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
    
    selected_store = st.sidebar.selectbox("매장명 선택", store_options)
    
    # 데이터 필터링
    filtered_df = df.copy()
    
    if selected_distributor != '전체':
        filtered_df = filtered_df[filtered_df['유통사'] == selected_distributor]
    
    if selected_store != '전체':
        filtered_df = filtered_df[filtered_df['매장명'] == selected_store]
    
    # 시즌 선택
    season = st.selectbox("시즌 선택", ['SS', 'FW'], key="season_selector")
    
    st.markdown("---")
    
    # 1. 아울렛 매출현황 - 디스커버리
    st.subheader("🏪 아울렛 매출현황 - 디스커버리")
    
    # 디스커버리 브랜드만 필터링
    discovery_df = filtered_df[filtered_df['브랜드'] == '디스커버리'].copy()
    
    if not discovery_df.empty:
        if season == 'SS':
            current_col = '25SS'
            previous_col = '24SS'
        else:  # FW
            current_col = '24FW'  # 25FW가 없으므로 24FW 사용
            previous_col = '23FW'
        
        # 유통사별 집계
        discovery_summary = discovery_df.groupby('유통사').agg({
            '매장명': 'count',
            current_col: 'sum',
            previous_col: 'sum'
        }).reset_index()
        
        # 매장명을 매장수로 변경
        discovery_summary = discovery_summary.rename(columns={'매장명': '매장수'})
        
        # 평균 매출 계산
        discovery_summary['현재_평균매출'] = discovery_summary[current_col] / discovery_summary['매장수']
        discovery_summary['전년_평균매출'] = discovery_summary[previous_col] / discovery_summary['매장수']
        
        # 신장률 계산 (총 매출) - 0으로 나누기 방지
        discovery_summary['총매출_신장률'] = 0.0
        mask = discovery_summary[previous_col] > 0
        discovery_summary.loc[mask, '총매출_신장률'] = ((discovery_summary.loc[mask, current_col] - discovery_summary.loc[mask, previous_col]) / discovery_summary.loc[mask, previous_col] * 100).round(1)
        
        # 신장률 계산 (평균 매출) - 0으로 나누기 방지
        discovery_summary['평균매출_신장률'] = 0.0
        mask_avg = discovery_summary['전년_평균매출'] > 0
        discovery_summary.loc[mask_avg, '평균매출_신장률'] = ((discovery_summary.loc[mask_avg, '현재_평균매출'] - discovery_summary.loc[mask_avg, '전년_평균매출']) / discovery_summary.loc[mask_avg, '전년_평균매출'] * 100).round(1)
        
        # 순위 계산 (총 매출 기준)
        discovery_summary = discovery_summary.sort_values(current_col, ascending=False).reset_index(drop=True)
        discovery_summary['순위'] = discovery_summary.index + 1
        
        # 새로운 데이터프레임 생성
        result_df = pd.DataFrame({
            '순위': discovery_summary['순위'],
            '유통사': discovery_summary['유통사'],
            '매장수': discovery_summary['매장수'],
            f'{season}시즌 총 매출': discovery_summary[current_col],
            f'전년{season}시즌 총 매출': discovery_summary[previous_col],
            '총매출 신장률': discovery_summary['총매출_신장률'],
            f'{season}시즌 평균매출': discovery_summary['현재_평균매출'],
            f'전년{season}시즌 평균매출': discovery_summary['전년_평균매출'],
            '평균매출 신장률': discovery_summary['평균매출_신장률']
        })
        
        # 신장률에 색상과 아이콘 추가
        def format_growth_rate(value):
            if value > 0:
                return f"🔵 ▲ {value}%"
            else:
                return f"🔴 ▼ {value}%"
        
        # 신장률 컬럼 포맷팅
        result_df['총매출 신장률'] = result_df['총매출 신장률'].apply(format_growth_rate)
        result_df['평균매출 신장률'] = result_df['평균매출 신장률'].apply(format_growth_rate)
        
        # 숫자 포맷팅
        result_df[f'{season}시즌 총 매출'] = result_df[f'{season}시즌 총 매출'].apply(lambda x: f"{x:,.0f}")
        result_df[f'전년{season}시즌 총 매출'] = result_df[f'전년{season}시즌 총 매출'].apply(lambda x: f"{x:,.0f}")
        result_df[f'{season}시즌 평균매출'] = result_df[f'{season}시즌 평균매출'].apply(lambda x: f"{x:,.0f}")
        result_df[f'전년{season}시즌 평균매출'] = result_df[f'전년{season}시즌 평균매출'].apply(lambda x: f"{x:,.0f}")
        
        # Streamlit 테이블 표시
        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "순위": st.column_config.NumberColumn("순위", help="총 매출 기준 순위"),
                "유통사": st.column_config.TextColumn("유통사", help="유통사명"),
                "매장수": st.column_config.NumberColumn("매장수", help="매장 개수"),
                f"{season}시즌 총 매출": st.column_config.TextColumn(f"{season}시즌 총 매출", help=f"{season}시즌 총 매출액"),
                f"전년{season}시즌 총 매출": st.column_config.TextColumn(f"전년{season}시즌 총 매출", help=f"전년 {season}시즌 총 매출액"),
                "총매출 신장률": st.column_config.TextColumn("총매출 신장률", help="총매출 증감률"),
                f"{season}시즌 평균매출": st.column_config.TextColumn(f"{season}시즌 평균매출", help=f"{season}시즌 매장당 평균 매출"),
                f"전년{season}시즌 평균매출": st.column_config.TextColumn(f"전년{season}시즌 평균매출", help=f"전년 {season}시즌 매장당 평균 매출"),
                "평균매출 신장률": st.column_config.TextColumn("평균매출 신장률", help="평균매출 증감률")
            }
        )
    else:
        st.warning("선택한 조건에 해당하는 디스커버리 브랜드 데이터가 없습니다.")
    
    st.markdown("---")
    
    # 2. 동업계 MS 현황
    st.subheader("📈 동업계 MS 현황")
    
    # 전체 브랜드 매출 비교
    if season == 'SS':
        current_col = '25SS'
        previous_col = '24SS'
    else:
        current_col = '24FW'  # 25FW가 없으므로 24FW 사용
        previous_col = '23FW'
    
    # 브랜드별 매출 비교
    brand_comparison = filtered_df.groupby('브랜드')[current_col].sum().sort_values(ascending=False).head(10)
    
    if not brand_comparison.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # 바 차트
            fig = px.bar(
                x=brand_comparison.values,
                y=brand_comparison.index,
                orientation='h',
                title=f"브랜드별 {season}시즌 매출 TOP 10",
                labels={'x': f'{season}시즌 매출 (원)', 'y': '브랜드'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 파이 차트
            fig_pie = px.pie(
                values=brand_comparison.values,
                names=brand_comparison.index,
                title=f"브랜드별 {season}시즌 매출 비중"
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("선택한 조건에 해당하는 브랜드 데이터가 없습니다.")
    
    st.markdown("---")
    
    # 3. 아울렛 매장 효율
    st.subheader("⚡ 아울렛 매장 효율")
    
    # 매장 면적 대비 매출 효율성
    efficiency_data = filtered_df[filtered_df['매장 면적'] > 0].copy()
    if not efficiency_data.empty:
        if season == 'SS':
            efficiency_data['효율성'] = efficiency_data['25SS'] / efficiency_data['매장 면적']
        else:
            efficiency_data['효율성'] = efficiency_data['24FW'] / efficiency_data['매장 면적']  # 25FW가 없으므로 24FW 사용
        
        # 매장별 효율성 TOP 10
        top_efficiency = efficiency_data.nlargest(10, '효율성')[['매장명', '유통사', '매장 면적', current_col, '효율성']]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"매장 효율성 TOP 10 ({season}시즌)")
            st.dataframe(top_efficiency, use_container_width=True)
        
        with col2:
            # 효율성 분포 히스토그램
            fig_hist = px.histogram(
                efficiency_data,
                x='효율성',
                title=f"매장 효율성 분포 ({season}시즌)",
                labels={'효율성': f'{season}시즌 매출/면적 (원/㎡)', 'count': '매장 수'}
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("매장 면적 데이터가 있는 매장이 없습니다.")
    
    st.markdown("---")
    
    # 푸터
    st.markdown("### 📝 데이터 정보")
    st.info(f"""
    - **데이터 출처**: DX OUTLET MS DB
    - **현재 시즌**: {season}시즌 ({current_col} 기준)
    - **비교 시즌**: 전년 {season}시즌 ({previous_col} 기준)
    - **선택된 유통사**: {selected_distributor}
    - **선택된 매장**: {selected_store}
    - **업데이트**: 실시간
    """)

if __name__ == "__main__":
    main()