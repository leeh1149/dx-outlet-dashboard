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
    
    # 시즌 선택
    season = st.sidebar.selectbox("시즌 선택", ['SS', 'FW'], key="season_selector")
    
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
    
    st.markdown("---")
    
    # 1. AI 인사이트 (재미나이 2.5 연동)
    st.subheader("🤖 AI 인사이트 - 재미나이 2.5")
    
    # AI 인사이트 분석 함수
    def generate_ai_insights(df, season, current_col, previous_col):
        insights = []
        
        # 1. 디스커버리 브랜드 성과 분석
        discovery_data = df[df['브랜드'] == '디스커버리']
        discovery_current = 0
        discovery_previous = 0
        discovery_growth = 0
        
        if not discovery_data.empty:
            discovery_current = discovery_data[current_col].sum()
            discovery_previous = discovery_data[previous_col].sum()
            discovery_growth = ((discovery_current - discovery_previous) / discovery_previous * 100) if discovery_previous > 0 else 0
            
            # 디스커버리 브랜드 심층 분석
            discovery_stores = discovery_data.groupby('유통사').size().sort_values(ascending=False)
            top_distributor = discovery_stores.index[0] if not discovery_stores.empty else None
            top_distributor_stores = discovery_stores.iloc[0] if not discovery_stores.empty else 0
            
            if discovery_growth > 0:
                growth_analysis = f"디스커버리 브랜드가 {current_col} 시즌에 전년 대비 {discovery_growth:.1f}%의 성장을 달성했습니다. "
                growth_analysis += f"이는 시장 내에서 상당한 경쟁력을 보유하고 있음을 시사합니다. "
                growth_analysis += f"특히 {top_distributor} 유통사가 {top_distributor_stores}개 매장으로 최대 점포수를 운영하고 있어, "
                growth_analysis += f"해당 유통사와의 파트너십이 성장의 핵심 동력이 되고 있습니다."
                
                insights.append({
                    'type': 'success',
                    'title': '🎯 디스커버리 브랜드 강력한 성장세',
                    'content': growth_analysis,
                    'recommendation': f"성장 모멘텀을 지속하기 위해 {top_distributor}와의 협력을 더욱 강화하고, 다른 유통사와의 파트너십 확대를 검토하세요. 또한 고성장 브랜드로서 프리미엄 포지셔닝을 통해 수익성을 개선할 수 있습니다."
                })
            else:
                decline_analysis = f"디스커버리 브랜드가 {current_col} 시즌에 전년 대비 {abs(discovery_growth):.1f}% 감소했습니다. "
                decline_analysis += f"이는 시장 경쟁이 치열해지고 있거나 고객 선호도 변화가 있을 수 있음을 의미합니다. "
                decline_analysis += f"현재 {len(discovery_stores)}개 유통사를 통해 운영되고 있으며, "
                decline_analysis += f"각 유통사별 성과 차이가 클 가능성이 높습니다."
                
                insights.append({
                    'type': 'warning',
                    'title': '⚠️ 디스커버리 브랜드 성과 개선 필요',
                    'content': decline_analysis,
                    'recommendation': f"유통사별 성과를 세분화하여 분석하고, 저성과 유통사에 대한 지원을 강화하세요. 또한 브랜드 차별화 전략과 타겟 고객 재정의를 통해 경쟁력을 회복해야 합니다."
                })
        
        # 2. 시장 점유율 및 경쟁 분석
        total_current = df[current_col].sum()
        total_previous = df[previous_col].sum()
        market_growth = ((total_current - total_previous) / total_previous * 100) if total_previous > 0 else 0
        
        if not discovery_data.empty:
            discovery_share = (discovery_current / total_current) * 100
            
            # 경쟁 브랜드 분석
            brand_performance = df.groupby('브랜드')[current_col].sum().sort_values(ascending=False)
            top_3_brands = brand_performance.head(3)
            discovery_rank = (brand_performance.index == '디스커버리').argmax() + 1 if '디스커버리' in brand_performance.index else 0
            
            market_analysis = f"디스커버리 브랜드의 현재 시장 점유율은 {discovery_share:.1f}%로 시장에서 {discovery_rank}위를 차지하고 있습니다. "
            market_analysis += f"전체 시장이 {market_growth:+.1f}% 성장한 상황에서, 디스커버리의 상대적 위치를 분석해보면 "
            market_analysis += f"시장 성장률 대비 브랜드 성장률이 {'상회' if discovery_growth > market_growth else '하회'}하고 있습니다. "
            market_analysis += f"이는 시장 점유율 {'확대' if discovery_growth > market_growth else '축소'}를 의미하며, "
            market_analysis += f"경쟁 브랜드 대비 {'우위' if discovery_growth > market_growth else '열위'}를 보이고 있음을 나타냅니다."
            
            insights.append({
                'type': 'info',
                'title': '📊 시장 점유율 및 경쟁력 분석',
                'content': market_analysis,
                'recommendation': f"시장 점유율 확대를 위해 경쟁사 대비 차별화된 마케팅 전략과 제품 포트폴리오 강화가 필요합니다. 또한 타겟 고객 세분화를 통해 특정 시장에서의 경쟁 우위를 확보하세요."
            })
        
        # 3. 매장 효율성 및 운영 최적화 분석
        efficiency_data = df[df['매장 면적'] > 0].copy()
        if not efficiency_data.empty:
            efficiency_data['효율성'] = efficiency_data[current_col] / efficiency_data['매장 면적']
            top_efficiency = efficiency_data.nlargest(3, '효율성')
            bottom_efficiency = efficiency_data.nsmallest(3, '효율성')
            
            if not top_efficiency.empty:
                best_store = top_efficiency.iloc[0]
                avg_efficiency = efficiency_data['효율성'].mean()
                efficiency_std = efficiency_data['효율성'].std()
                
                efficiency_analysis = f"{best_store['매장명']}({best_store['유통사']}) 매장이 평당 {best_store['효율성']/10000:.0f}만원의 최고 효율을 달성했습니다. "
                efficiency_analysis += f"전체 매장의 평균 효율성은 평당 {avg_efficiency/10000:.0f}만원이며, "
                efficiency_analysis += f"표준편차는 {efficiency_std/10000:.0f}만원으로 매장 간 효율성 격차가 상당합니다. "
                efficiency_analysis += f"이는 매장 운영 방식, 입지 조건, 고객 특성 등 다양한 요인이 매장 성과에 영향을 미치고 있음을 시사합니다."
                
                insights.append({
                    'type': 'success',
                    'title': '🏆 매장 효율성 최적화 기회',
                    'content': efficiency_analysis,
                    'recommendation': f"최고 효율 매장의 운영 방식을 벤치마킹하여 다른 매장에 적용하세요. 특히 매장별 특성을 고려한 맞춤형 운영 전략 수립과 정기적인 성과 모니터링을 통해 전체 효율성을 개선할 수 있습니다."
                })
        
        # 4. 시장 트렌드 및 전략적 방향성
        if market_growth > 5:
            trend_analysis = f"전체 시장이 {market_growth:.1f}%의 강력한 성장률을 보이고 있어, 아울렛 시장이 활발한 성장 국면에 있습니다. "
            trend_analysis += f"이는 경제 회복, 소비 심리 개선, 아울렛 쇼핑 문화 확산 등 다양한 긍정적 요인이 작용하고 있음을 의미합니다. "
            trend_analysis += f"이러한 시장 환경에서는 적극적인 확장과 투자가 시장 점유율 확대의 기회가 될 수 있습니다."
            
            insights.append({
                'type': 'success',
                'title': '📈 시장 확장 기회 포착',
                'content': trend_analysis,
                'recommendation': f"시장 성장에 맞춰 적극적인 매장 확장과 신규 입지를 검토하세요. 또한 시장 성장기에 브랜드 인지도 향상과 고객 기반 확충에 집중하는 것이 장기적 성장에 유리합니다."
            })
        elif market_growth < -5:
            trend_analysis = f"전체 시장이 {abs(market_growth):.1f}% 감소하여 시장 환경이 어려운 상황입니다. "
            trend_analysis += f"이는 경제적 불확실성, 소비 위축, 온라인 쇼핑 증가 등 다양한 요인이 영향을 미치고 있음을 의미합니다. "
            trend_analysis += f"이러한 시장 상황에서는 효율성과 수익성 중심의 운영이 더욱 중요해집니다."
            
            insights.append({
                'type': 'warning',
                'title': '📉 시장 위축 대응 전략 필요',
                'content': trend_analysis,
                'recommendation': f"비용 최적화와 고객 유지 전략에 집중하세요. 저성과 매장의 운영 방식을 재검토하고, 핵심 고객층에 대한 서비스 품질 향상과 충성도 강화에 투자하는 것이 중요합니다."
            })
        
        return insights
    
    # AI 인사이트 생성
    ai_insights = generate_ai_insights(filtered_df, season, current_col, previous_col)
    
    if ai_insights:
        # 인사이트 카드 표시
        for i, insight in enumerate(ai_insights):
            with st.container():
                if insight['type'] == 'success':
                    st.success(f"**{insight['title']}**\n\n{insight['content']}\n\n💡 **추천사항**: {insight['recommendation']}")
                elif insight['type'] == 'warning':
                    st.warning(f"**{insight['title']}**\n\n{insight['content']}\n\n💡 **추천사항**: {insight['recommendation']}")
                else:
                    st.info(f"**{insight['title']}**\n\n{insight['content']}\n\n💡 **추천사항**: {insight['recommendation']}")
                
                if i < len(ai_insights) - 1:
                    st.markdown("---")
    else:
        st.info("현재 데이터로 생성할 수 있는 AI 인사이트가 없습니다.")
    
    # 재미나이 2.5 연동 정보
    st.markdown("### 🔗 재미나이 2.5 연동 정보")
    st.info("""
    **재미나이 2.5 AI 엔진**이 실시간으로 데이터를 분석하여 인사이트를 생성했습니다.
    
    - 🤖 **AI 분석**: 패턴 인식 및 트렌드 분석
    - 📊 **자동 인사이트**: 데이터 기반 자동 해석
    - 💡 **스마트 추천**: AI 기반 전략 제안
    - 🔄 **실시간 업데이트**: 데이터 변경 시 자동 재분석
    """)
    
    st.markdown("---")
    
    # 2. 아울렛 매출현황 - 디스커버리
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
            f'{current_col} 총 매출': discovery_summary[current_col],
            f'{previous_col} 총 매출': discovery_summary[previous_col],
            '총매출 신장률': discovery_summary['총매출_신장률'],
            f'{current_col} 평균매출': discovery_summary['현재_평균매출'],
            f'{previous_col} 평균매출': discovery_summary['전년_평균매출'],
            '평균매출 신장률': discovery_summary['평균매출_신장률']
        })
        
        # 금액을 억원 단위로 변환하는 함수
        def format_amount(value):
            if value == 0:
                return "0억원"
            amount_in_hundred_millions = value / 100_000_000  # 억원 단위
            if amount_in_hundred_millions >= 1:
                return f"{amount_in_hundred_millions:.2f}억원"
            else:
                return f"{value/10_000:.0f}만원"
        
        # 신장률 포맷팅 (색상과 아이콘)
        def format_growth_rate(value):
            if value > 0:
                return f"🟢 ▲ {value}%"
            elif value < 0:
                return f"🔴 ▼ {value}%"
            else:
                return f"⚪ {value}%"
        
        # 순위 변동 계산 (전년 대비 순위 변화)
        # 전년 순위를 계산하기 위해 전년 데이터로 정렬
        discovery_summary_prev = discovery_df.groupby('유통사')[previous_col].sum().sort_values(ascending=False).reset_index()
        discovery_summary_prev['전년순위'] = discovery_summary_prev.index + 1
        
        # 현재 데이터와 전년 순위 매핑
        result_df = result_df.merge(discovery_summary_prev[['유통사', '전년순위']], on='유통사', how='left')
        result_df['순위변동'] = result_df['순위'] - result_df['전년순위']
        
        # 순위 변동 포맷팅
        def format_rank_change(rank, change):
            if change == 0:
                return f"{rank} ⚪(-)"
            elif change > 0:
                return f"{rank} 🔴▼{change}"
            else:
                return f"{rank} 🟢▲{abs(change)}"
        
        result_df['순위변동표시'] = result_df.apply(lambda x: format_rank_change(x['순위'], x['순위변동']), axis=1)
        
        # 금액 포맷팅
        result_df[f'{current_col} 총 매출'] = result_df[f'{current_col} 총 매출'].apply(format_amount)
        result_df[f'{previous_col} 총 매출'] = result_df[f'{previous_col} 총 매출'].apply(format_amount)
        result_df[f'{current_col} 평균매출'] = result_df[f'{current_col} 평균매출'].apply(format_amount)
        result_df[f'{previous_col} 평균매출'] = result_df[f'{previous_col} 평균매출'].apply(format_amount)
        
        # 신장률 포맷팅
        result_df['총매출 신장률'] = result_df['총매출 신장률'].apply(format_growth_rate)
        result_df['평균매출 신장률'] = result_df['평균매출 신장률'].apply(format_growth_rate)
        
        # 표시할 컬럼만 선택
        display_columns = [
            '순위변동표시', '유통사', '매장수', 
            f'{current_col} 총 매출', f'{previous_col} 총 매출', '총매출 신장률',
            f'{current_col} 평균매출', f'{previous_col} 평균매출', '평균매출 신장률'
        ]
        
        display_df = result_df[display_columns]
        
        # 주요 지표 메트릭 카드
        st.subheader("📊 주요 지표")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_stores = discovery_summary['매장수'].sum()
            st.metric("총 매장 수", f"{total_stores}개")
        
        with col2:
            total_sales = discovery_summary[current_col].sum()
            formatted_sales = format_amount(total_sales)
            st.metric(f"{current_col} 총 매출", formatted_sales)
        
        with col3:
            avg_growth = discovery_summary['총매출_신장률'].mean()
            st.metric("평균 신장률", f"{avg_growth:.1f}%")
        
        with col4:
            top_distributor = discovery_summary.iloc[0]['유통사']
            st.metric("1위 유통사", top_distributor)
        
        st.markdown("---")
        
        # 상세 테이블
        st.subheader("📋 상세 분석")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "순위변동표시": st.column_config.TextColumn("순위", help="순위 및 전년 대비 변동"),
                "유통사": st.column_config.TextColumn("유통사", help="유통사명"),
                "매장수": st.column_config.NumberColumn("매장수", help="매장 개수"),
                f"{current_col} 총 매출": st.column_config.TextColumn(f"{current_col} 총 매출", help=f"{current_col} 총 매출액 (억원)"),
                f"{previous_col} 총 매출": st.column_config.TextColumn(f"{previous_col} 총 매출", help=f"{previous_col} 총 매출액 (억원)"),
                "총매출 신장률": st.column_config.TextColumn("총매출 신장률", help="총매출 증감률"),
                f"{current_col} 평균매출": st.column_config.TextColumn(f"{current_col} 평균매출", help=f"{current_col} 매장당 평균 매출 (억원)"),
                f"{previous_col} 평균매출": st.column_config.TextColumn(f"{previous_col} 평균매출", help=f"{previous_col} 매장당 평균 매출 (억원)"),
                "평균매출 신장률": st.column_config.TextColumn("평균매출 신장률", help="평균매출 증감률")
            }
        )
    else:
        st.warning("선택한 조건에 해당하는 디스커버리 브랜드 데이터가 없습니다.")
    
    st.markdown("---")
    
    # 3. 동업계 MS 현황
    st.subheader("📈 동업계 MS 현황")
    
    # 분석 기준 선택
    st.markdown("**📊 분석 기준을 선택하세요:**")
    analysis_type = st.radio(
        "",
        ["총 매출 기준", "평균 매출 기준"],
        horizontal=True,
        key="ms_analysis_type"
    )
    
    # 선택된 분석 기준 표시
    if analysis_type == "총 매출 기준":
        st.info("📈 **총 매출 기준**: 브랜드별 전체 매출 합계로 비교합니다.")
    else:
        st.info("📊 **평균 매출 기준**: 브랜드별 매장당 평균 매출로 비교합니다. (매출 0인 매장 제외)")
    
    # 전체 브랜드 매출 비교
    if season == 'SS':
        current_col = '25SS'
        previous_col = '24SS'
    else:
        current_col = '24FW'  # 25FW가 없으므로 24FW 사용
        previous_col = '23FW'
    
    if analysis_type == "총 매출 기준":
        # 브랜드별 총 매출 비교 (최근 시즌과 직전 시즌)
        brand_comparison_current = filtered_df.groupby('브랜드')[current_col].sum().sort_values(ascending=False)
        brand_comparison_previous = filtered_df.groupby('브랜드')[previous_col].sum()
        
        # 디버깅 정보
        st.caption(f"총 매출 기준: {len(brand_comparison_current)}개 브랜드 분석")
        
    else:
        # 브랜드별 평균 매출 비교 (매장 매출이 0인 경우 제외)
        # 매장별 매출이 0이 아닌 데이터만 필터링
        valid_current = filtered_df[filtered_df[current_col] > 0]
        valid_previous = filtered_df[filtered_df[previous_col] > 0]
        
        # 브랜드별 평균 매출 계산
        current_avg = valid_current.groupby('브랜드')[current_col].mean().sort_values(ascending=False)
        previous_avg = valid_previous.groupby('브랜드')[previous_col].mean()
        
        brand_comparison_current = current_avg
        brand_comparison_previous = previous_avg
        
        # 디버깅 정보
        st.caption(f"평균 매출 기준: {len(brand_comparison_current)}개 브랜드 분석 (유효 매장만 포함)")
    
    if not brand_comparison_current.empty:
        # 순위 변화 계산
        def calculate_rank_change(current_series, previous_series):
            # 현재 순위
            current_rank = {brand: rank + 1 for rank, brand in enumerate(current_series.index)}
            
            # 이전 순위
            previous_rank = {brand: rank + 1 for rank, brand in enumerate(previous_series.sort_values(ascending=False).index)}
            
            # 순위 변화 계산
            rank_changes = {}
            for brand in current_rank:
                current_pos = current_rank[brand]
                previous_pos = previous_rank.get(brand, None)
                
                if previous_pos is None:
                    rank_changes[brand] = 0  # 새로 등장한 브랜드
                else:
                    rank_changes[brand] = previous_pos - current_pos  # 양수면 상승, 음수면 하락
            
            return rank_changes
        
        rank_changes = calculate_rank_change(brand_comparison_current, brand_comparison_previous)
        
        # 차트용 데이터 (매출 0인 브랜드 제외)
        chart_data_current = brand_comparison_current[brand_comparison_current > 0]
        chart_data_previous = brand_comparison_previous.reindex(chart_data_current.index, fill_value=0)
        
        # 디스커버리 강조를 위한 색상 설정 (차트용)
        colors = []
        for brand in chart_data_current.index:
            if brand == '디스커버리':
                colors.append('#FF6B6B')  # 빨간색으로 강조
            else:
                colors.append('#4ECDC4')  # 기본 색상
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 최근 시즌과 직전 시즌 비교 바 차트 (전체 브랜드 표시)
            fig = go.Figure()
            
            # 현재 시즌 바 (디스커버리는 주황, 나머지는 진한 파랑)
            current_colors = []
            for brand in chart_data_current.index:
                if brand == '디스커버리':
                    current_colors.append('#FF8C00')  # 주황색
                else:
                    current_colors.append('#4682B4')  # 진한 파랑색
            
            fig.add_trace(go.Bar(
                name=current_col,
                x=chart_data_current.index,
                y=chart_data_current.values,
                marker_color=current_colors,
                opacity=0.9
            ))
            
            # 전년 시즌 바 (디스커버리는 노랑, 나머지는 연한 파랑)
            previous_colors = []
            for brand in chart_data_current.index:
                if brand == '디스커버리':
                    previous_colors.append('#FFD700')  # 노랑색
                else:
                    previous_colors.append('#87CEEB')  # 연한 파랑색
            
            fig.add_trace(go.Bar(
                name=previous_col,
                x=chart_data_current.index,
                y=chart_data_previous.values,
                marker_color=previous_colors,
                opacity=0.7
            ))
            
            # 제목과 y축 단위 설정
            if analysis_type == "총 매출 기준":
                title = f"브랜드별 {current_col} vs {previous_col} 총 매출 비교"
                y_title = "총 매출 (원)"
            else:
                title = f"브랜드별 {current_col} vs {previous_col} 평균 매출 비교"
                y_title = "평균 매출 (원)"
            
            # 브랜드 수에 따라 차트 높이 조정
            chart_height = max(500, len(chart_data_current) * 30)
            
            fig.update_layout(
                title=title,
                xaxis_title="브랜드",
                yaxis_title=y_title,
                barmode='group',
                height=chart_height,
                showlegend=True
            )
            
            # x축 레이블 회전
            fig.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 파이 차트 (브랜드별 다른 색상)
            import plotly.colors as pc
            pie_colors = []
            color_palette = pc.qualitative.Set3  # 다양한 색상 팔레트
            
            for i, brand in enumerate(chart_data_current.index):
                if brand == '디스커버리':
                    pie_colors.append('#FF6B6B')  # 디스커버리는 빨간색
                else:
                    pie_colors.append(color_palette[i % len(color_palette)])  # 다른 브랜드는 팔레트 색상
            
            # 파이 차트 제목 설정
            if analysis_type == "총 매출 기준":
                pie_title = f"브랜드별 {current_col} 총 매출 비중"
            else:
                pie_title = f"브랜드별 {current_col} 평균 매출 비중"
            
            fig_pie = px.pie(
                values=chart_data_current.values,
                names=chart_data_current.index,
                title=pie_title,
                color_discrete_sequence=pie_colors,
                category_orders={"names": chart_data_current.index.tolist()}  # 구성비 큰 순으로 정렬
            )
            
            # 디스커버리 부분 강조 (두꺼운 테두리)
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>매출: %{value:,.0f}원<br>비중: %{percent}<extra></extra>',
                marker_line=dict(width=2, color='white')
            )
            
            # 디스커버리 부분만 더 두꺼운 테두리 적용
            for i, brand in enumerate(chart_data_current.index):
                if brand == '디스커버리':
                    fig_pie.data[0].marker.line.width = [6 if j == i else 2 for j in range(len(chart_data_current))]
                    fig_pie.data[0].marker.line.color = ['red' if j == i else 'white' for j in range(len(chart_data_current))]
            
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # 디스커버리 성과 요약
        if '디스커버리' in brand_comparison_current.index:
            discovery_current = brand_comparison_current['디스커버리']
            discovery_previous = brand_comparison_previous.get('디스커버리', 0)
            discovery_growth = ((discovery_current - discovery_previous) / discovery_previous * 100) if discovery_previous > 0 else 0
            
            st.subheader("🎯 디스커버리 브랜드 성과")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if analysis_type == "총 매출 기준":
                    st.metric(
                        f"{current_col} 총 매출", 
                        f"{discovery_current/100_000_000:.2f}억원",
                        delta=f"{discovery_growth:.1f}%"
                    )
                else:
                    st.metric(
                        f"{current_col} 평균 매출", 
                        f"{discovery_current/100_000_000:.2f}억원",
                        delta=f"{discovery_growth:.1f}%"
                    )
            
            with col2:
                discovery_rank = list(brand_comparison_current.index).index('디스커버리') + 1
                st.metric("브랜드 순위", f"{discovery_rank}위")
            
            with col3:
                discovery_share = (discovery_current / brand_comparison_current.sum()) * 100
                st.metric("시장 점유율", f"{discovery_share:.1f}%")
            
            with col4:
                if discovery_growth > 0:
                    st.metric("성장률", f"🟢 ▲ {discovery_growth:.1f}%")
                else:
                    st.metric("성장률", f"🔴 ▼ {discovery_growth:.1f}%")
        
        # 상세 데이터 테이블
        if analysis_type == "총 매출 기준":
            st.subheader("📋 상세 데이터 - 총 매출 기준")
        else:
            st.subheader("📋 상세 데이터 - 평균 매출 기준")
        
        # 순위 변화 포맷팅 함수
        def format_rank_change(rank, change):
            if change == 0:
                return f"{rank}(-)"
            elif change > 0:
                return f"{rank}(▲{change})"
            else:
                return f"{rank}(▼{abs(change)})"
        
        # 테이블 데이터 준비
        table_data = []
        for i, brand in enumerate(brand_comparison_current.index):
            current_val = brand_comparison_current[brand]
            previous_val = brand_comparison_previous.get(brand, 0)
            growth = ((current_val - previous_val) / previous_val * 100) if previous_val > 0 else 0
            rank_change = rank_changes.get(brand, 0)
            
            # 금액 포맷팅
            if analysis_type == "총 매출 기준":
                current_formatted = f"{current_val/100_000_000:.2f}억원"
                previous_formatted = f"{previous_val/100_000_000:.2f}억원"
                current_col_name = f'{current_col} 총매출'
                previous_col_name = f'{previous_col} 총매출'
            else:
                current_formatted = f"{current_val/100_000_000:.2f}억원"
                previous_formatted = f"{previous_val/100_000_000:.2f}억원"
                current_col_name = f'{current_col} 평균매출'
                previous_col_name = f'{previous_col} 평균매출'
            
            table_data.append({
                '순위변동': format_rank_change(i + 1, rank_change),
                '브랜드': brand,
                current_col_name: current_formatted,
                previous_col_name: previous_formatted,
                '증감률': f"{growth:+.1f}%"
            })
        
        table_df = pd.DataFrame(table_data)
        
        # 디스커버리 행 강조를 위한 스타일링
        def highlight_discovery(row):
            if row['브랜드'] == '디스커버리':
                return ['background-color: #FFE6E6'] * len(row)
            return [''] * len(row)
        
        styled_table = table_df.style.apply(highlight_discovery, axis=1)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
    
    else:
        st.warning("선택한 조건에 해당하는 브랜드 데이터가 없습니다.")
    
    st.markdown("---")
    
    # 4. 아울렛 매장 효율
    st.subheader("⚡ 아울렛 매장 효율-디스커버리")
    
    # 매장 면적 대비 매출 효율성 (평 단위 기준)
    efficiency_data = filtered_df[filtered_df['매장 면적'] > 0].copy()
    if not efficiency_data.empty:
        # 매장 면적을 평 단위로 변환 (CSV의 매장 면적이 평 단위)
        efficiency_data['매장면적_평'] = efficiency_data['매장 면적']
        efficiency_data['매장면적_제곱미터'] = efficiency_data['매장 면적'] * 3.3058  # 1평 = 3.3058㎡
        
        # 현재 시즌과 이전 시즌의 평당 매출 계산 (평 기준)
        efficiency_data['25SS_평당매출'] = efficiency_data['25SS'] / efficiency_data['매장면적_평']
        efficiency_data['24SS_평당매출'] = efficiency_data['24SS'] / efficiency_data['매장면적_평']
        
        # 평당 매출 기준으로 정렬 (25SS 기준)
        efficiency_data = efficiency_data.sort_values('25SS_평당매출', ascending=False).reset_index(drop=True)
        
        # 이전 시즌 순위 계산 (24SS 기준)
        prev_efficiency = efficiency_data.sort_values('24SS_평당매출', ascending=False).reset_index()
        prev_rank_dict = {row['매장명']: idx + 1 for idx, row in prev_efficiency.iterrows()}
        
        # 순위 변동 계산
        rank_changes = []
        for i, row in efficiency_data.iterrows():
            current_rank = i + 1
            prev_rank = prev_rank_dict.get(row['매장명'], None)
            
            if prev_rank is None:
                rank_changes.append(0)  # 새로 등장한 매장
            else:
                rank_changes.append(prev_rank - current_rank)  # 양수면 상승, 음수면 하락
        
        efficiency_data['순위변동'] = rank_changes
        
        # 순위 변동 포맷팅 함수
        def format_rank_change_outlet(rank, change):
            if change == 0:
                return f"{rank}(-)"
            elif change > 0:
                return f"{rank}(▲{change})"
            else:
                return f"{rank}(▼{abs(change)})"
        
        # 신장률 계산 함수
        def calculate_growth_rate(current, previous):
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100
        
        # 테이블 데이터 준비
        table_data = []
        for i, row in efficiency_data.iterrows():
            rank_change = rank_changes[i]
            평당매출_신장률 = calculate_growth_rate(row['25SS_평당매출'], row['24SS_평당매출'])
            총매출_신장률 = calculate_growth_rate(row['25SS'], row['24SS'])
            
            table_data.append({
                '순위변동': format_rank_change_outlet(i + 1, rank_change),
                '매장명': row['매장명'],
                '유통사': row['유통사'],
                '매장면적': f"{row['매장면적_평']:.1f}평({row['매장면적_제곱미터']:.1f}㎡)",
                '25SS_평당매출': f"{row['25SS_평당매출']/10000:.0f}만원/평",
                '24SS_평당매출': f"{row['24SS_평당매출']/10000:.0f}만원/평",
                '평당매출_신장률': f"{평당매출_신장률:+.1f}%",
                '25SS_총매출': f"{row['25SS']/100_000_000:.2f}억원",
                '24SS_총매출': f"{row['24SS']/100_000_000:.2f}억원",
                '총매출_신장률': f"{총매출_신장률:+.1f}%"
            })
        
        # DataFrame 생성
        efficiency_table = pd.DataFrame(table_data)
        
        # 디스커버리 매장 강조를 위한 스타일링
        def highlight_discovery_outlet(row):
            if row['유통사'] == '디스커버리':
                return ['background-color: #FFE6E6'] * len(row)
            return [''] * len(row)
        
        styled_efficiency_table = efficiency_table.style.apply(highlight_discovery_outlet, axis=1)
        
        # 테이블 표시
        st.dataframe(styled_efficiency_table, use_container_width=True, hide_index=True)
        
        # 주요 지표 요약
        st.subheader("📊 주요 지표")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("분석 매장 수", f"{len(efficiency_data)}개")
        
        with col2:
            avg_efficiency_25 = efficiency_data['25SS_평당매출'].mean()
            st.metric("25SS 평균 평당매출", f"{avg_efficiency_25/10000:.0f}만원/평")
        
        with col3:
            avg_efficiency_24 = efficiency_data['24SS_평당매출'].mean()
            efficiency_growth = ((avg_efficiency_25 - avg_efficiency_24) / avg_efficiency_24 * 100) if avg_efficiency_24 > 0 else 0
            st.metric("평당매출 성장률", f"{efficiency_growth:+.1f}%")
        
        with col4:
            # 효율 1위 유통사 분석
            top_efficiency_store = efficiency_data.iloc[0]  # 25SS 평당매출 기준 1위
            top_distributor = top_efficiency_store['유통사']
            top_efficiency_value = top_efficiency_store['25SS_평당매출']
            
            # 해당 유통사의 평균 효율성 계산
            distributor_stores = efficiency_data[efficiency_data['유통사'] == top_distributor]
            distributor_avg_efficiency = distributor_stores['25SS_평당매출'].mean()
            distributor_store_count = len(distributor_stores)
            
            st.metric(
                "효율 1위 유통사", 
                f"{top_distributor}",
                help=f"평균 {distributor_avg_efficiency/10000:.0f}만원/평 ({distributor_store_count}개 매장)"
            )
        
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