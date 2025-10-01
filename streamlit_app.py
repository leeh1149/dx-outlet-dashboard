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

# 디스커버리 매출 분석 함수
def analyze_discovery_sales(df, season):
    """디스커버리 브랜드의 유통사별 매출을 분석합니다."""
    # 디스커버리 브랜드만 필터링
    discovery_df = df[df['브랜드'] == '디스커버리'].copy()
    
    if season == 'SS':
        current_col = '25SS'
        previous_col = '24SS'
    else:  # FW
        current_col = '25FW'
        previous_col = '24FW'
    
    # 유통사별 집계
    discovery_summary = discovery_df.groupby('유통사').agg({
        '매장명': 'count',
        current_col: 'sum',
        previous_col: 'sum'
    }).reset_index()
    
    # 매장명을 매장수로 변경
    discovery_summary = discovery_summary.rename(columns={'매장명': '매장수'})
    
    # 평균 매출 계산
    discovery_summary[f'{current_col}_평균매출'] = discovery_summary[current_col] / discovery_summary['매장수']
    discovery_summary[f'{previous_col}_평균매출'] = discovery_summary[previous_col] / discovery_summary['매장수']
    
    # 신장률 계산 (총 매출)
    discovery_summary['총매출_신장률'] = ((discovery_summary[current_col] - discovery_summary[previous_col]) / discovery_summary[previous_col] * 100).round(1)
    
    # 신장률 계산 (평균 매출)
    discovery_summary['평균매출_신장률'] = ((discovery_summary[f'{current_col}_평균매출'] - discovery_summary[f'{previous_col}_평균매출']) / discovery_summary[f'{previous_col}_평균매출'] * 100).round(1)
    
    # 순위 계산 (총 매출 기준)
    discovery_summary = discovery_summary.sort_values(current_col, ascending=False).reset_index(drop=True)
    discovery_summary['순위'] = discovery_summary.index + 1
    
    # 컬럼명 정리
    discovery_summary = discovery_summary.rename(columns={
        current_col: f'{season}시즌 총 매출',
        previous_col: f'전년{season}시즌 총 매출',
        f'{current_col}_평균매출': f'{season}시즌 평균매출',
        f'{previous_col}_평균매출': f'전년{season}시즌 평균매출',
        '총매출_신장률': '총매출 신장률',
        '평균매출_신장률': '평균매출 신장률'
    })
    
    # 컬럼 순서 정리
    result_columns = ['순위', '유통사', '매장수', f'{season}시즌 총 매출', f'전년{season}시즌 총 매출', 
                     '총매출 신장률', f'{season}시즌 평균매출', f'전년{season}시즌 평균매출', '평균매출 신장률']
    
    discovery_summary = discovery_summary[result_columns]
    
    return discovery_summary

# 메인 함수
def main():
    # 헤더
    st.title("📊 DX OUTLET 매출 현황 대시보드")
    st.markdown("---")
    
    # 데이터 로드
    df = load_data()
    if df is None:
        st.stop()
    
    # 시즌 선택
    season = st.selectbox("시즌 선택", ['SS', 'FW'], key="season_selector")
    
    st.markdown("---")
    
    # 1. 아울렛 매출 현황 - 디스커버리
    st.subheader("🏪 아울렛 매출 현황 - 디스커버리")
    
    # 디스커버리 매출 분석
    discovery_data = analyze_discovery_sales(df, season)
    
    # 데이터 표시를 위한 HTML 생성
    def create_styled_table(data):
        html = f"""
        <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
        <thead>
            <tr style="background-color: #f0f2f6;">
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">순위</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">유통사</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">매장수</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">{season}시즌 총 매출</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">전년{season}시즌 총 매출</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">총매출 신장률</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">{season}시즌 평균매출</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">전년{season}시즌 평균매출</th>
                <th style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">평균매출 신장률</th>
            </tr>
        </thead>
        <tbody>
        """
        
        for _, row in data.iterrows():
            # 신장률에 따른 색상 결정
            total_growth_color = "color: #0066cc;" if row['총매출 신장률'] > 0 else "color: #cc0000;"
            avg_growth_color = "color: #0066cc;" if row['평균매출 신장률'] > 0 else "color: #cc0000;"
            
            # 신장률 아이콘
            total_growth_icon = "▲" if row['총매출 신장률'] > 0 else "▼"
            avg_growth_icon = "▲" if row['평균매출 신장률'] > 0 else "▼"
            
            html += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center;">{int(row['순위'])}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: bold;">{row['유통사']}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center;">{int(row['매장수'])}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{row[f'{season}시즌 총 매출']:,.0f}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{row[f'전년{season}시즌 총 매출']:,.0f}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; {total_growth_color} font-weight: bold;">{total_growth_icon} {row['총매출 신장률']}%</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{row[f'{season}시즌 평균매출']:,.0f}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{row[f'전년{season}시즌 평균매출']:,.0f}</td>
                <td style="border: 1px solid #ddd; padding: 12px; text-align: center; {avg_growth_color} font-weight: bold;">{avg_growth_icon} {row['평균매출 신장률']}%</td>
            </tr>
            """
        
        html += """
        </tbody>
        </table>
        </div>
        """
        
        return html
    
    # 스타일이 적용된 테이블 표시
    st.markdown(create_styled_table(discovery_data), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 2. 동업계 MS 현황 (플레이스홀더)
    st.subheader("📈 동업계 MS 현황")
    st.info("동업계 MS 현황 데이터가 준비되면 구현 예정입니다.")
    
    # 간단한 차트로 대체 (전체 브랜드 매출 비교)
    if season == 'SS':
        current_col = '25SS'
        previous_col = '24SS'
    else:
        current_col = '25FW'
        previous_col = '24FW'
    
    # 브랜드별 매출 비교
    brand_comparison = df.groupby('브랜드')[current_col].sum().sort_values(ascending=False).head(10)
    
    fig = px.bar(
        x=brand_comparison.values,
        y=brand_comparison.index,
        orientation='h',
        title=f"브랜드별 {season}시즌 매출 TOP 10",
        labels={'x': f'{season}시즌 매출 (원)', 'y': '브랜드'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # 3. 아울렛 매장 효율 (플레이스홀더)
    st.subheader("⚡ 아울렛 매장 효율")
    st.info("아울렛 매장 효율 분석 데이터가 준비되면 구현 예정입니다.")
    
    # 간단한 매장 효율 지표로 대체 (매장 면적 대비 매출)
    efficiency_data = df[df['매장 면적'] > 0].copy()
    if not efficiency_data.empty:
        if season == 'SS':
            efficiency_data['효율성'] = efficiency_data['25SS'] / efficiency_data['매장 면적']
        else:
            efficiency_data['효율성'] = efficiency_data['25FW'] / efficiency_data['매장 면적']
        
        # 매장별 효율성 TOP 10
        top_efficiency = efficiency_data.nlargest(10, '효율성')[['매장명', '유통사', '매장 면적', f'{season}시즌 총 매출' if season == 'SS' else '25FW', '효율성']]
        
        st.subheader(f"매장 효율성 TOP 10 ({season}시즌)")
        st.dataframe(top_efficiency, use_container_width=True)
    
    st.markdown("---")
    
    # 푸터
    st.markdown("### 📝 데이터 정보")
    st.info(f"""
    - **데이터 출처**: DX OUTLET MS DB
    - **현재 시즌**: {season}시즌 ({'25SS' if season == 'SS' else '25FW'} 기준)
    - **비교 시즌**: 전년 {season}시즌 ({'24SS' if season == 'SS' else '24FW'} 기준)
    - **업데이트**: 실시간
    """)

if __name__ == "__main__":
    main()
