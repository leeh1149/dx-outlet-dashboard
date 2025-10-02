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
        result_df[f'{season}시즌 총 매출'] = result_df[f'{season}시즌 총 매출'].apply(format_amount)
        result_df[f'전년{season}시즌 총 매출'] = result_df[f'전년{season}시즌 총 매출'].apply(format_amount)
        result_df[f'{season}시즌 평균매출'] = result_df[f'{season}시즌 평균매출'].apply(format_amount)
        result_df[f'전년{season}시즌 평균매출'] = result_df[f'전년{season}시즌 평균매출'].apply(format_amount)
        
        # 신장률 포맷팅
        result_df['총매출 신장률'] = result_df['총매출 신장률'].apply(format_growth_rate)
        result_df['평균매출 신장률'] = result_df['평균매출 신장률'].apply(format_growth_rate)
        
        # 표시할 컬럼만 선택
        display_columns = [
            '순위변동표시', '유통사', '매장수', 
            f'{season}시즌 총 매출', f'전년{season}시즌 총 매출', '총매출 신장률',
            f'{season}시즌 평균매출', f'전년{season}시즌 평균매출', '평균매출 신장률'
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
            st.metric(f"{season}시즌 총 매출", formatted_sales)
        
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
                f"{season}시즌 총 매출": st.column_config.TextColumn(f"{season}시즌 총 매출", help=f"{season}시즌 총 매출액 (억원)"),
                f"전년{season}시즌 총 매출": st.column_config.TextColumn(f"전년{season}시즌 총 매출", help=f"전년 {season}시즌 총 매출액 (억원)"),
                "총매출 신장률": st.column_config.TextColumn("총매출 신장률", help="총매출 증감률"),
                f"{season}시즌 평균매출": st.column_config.TextColumn(f"{season}시즌 평균매출", help=f"{season}시즌 매장당 평균 매출 (억원)"),
                f"전년{season}시즌 평균매출": st.column_config.TextColumn(f"전년{season}시즌 평균매출", help=f"전년 {season}시즌 매장당 평균 매출 (억원)"),
                "평균매출 신장률": st.column_config.TextColumn("평균매출 신장률", help="평균매출 증감률")
            }
        )
    else:
        st.warning("선택한 조건에 해당하는 디스커버리 브랜드 데이터가 없습니다.")
    
    st.markdown("---")
    
    # 2. 동업계 MS 현황
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
            
            # 디스커버리 부분 강조 (두꺼운 테두리 및 굵은 글씨)
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>매출: %{value:,.0f}원<br>비중: %{percent}<extra></extra>',
                marker_line=dict(width=2, color='white'),
                textfont=dict(size=12, color='black')  # 모든 텍스트를 검은색으로 설정
            )
            
            # 디스커버리 부분만 더 두꺼운 테두리 및 굵은 글씨 적용
            for i, brand in enumerate(chart_data_current.index):
                if brand == '디스커버리':
                    fig_pie.data[0].marker.line.width = [6 if j == i else 2 for j in range(len(chart_data_current))]
                    fig_pie.data[0].marker.line.color = ['red' if j == i else 'white' for j in range(len(chart_data_current))]
                    # 디스커버리 텍스트를 굵게 표시
                    fig_pie.data[0].textfont.size = [16 if j == i else 12 for j in range(len(chart_data_current))]
                    fig_pie.data[0].textfont.color = ['black'] * len(chart_data_current)  # 모든 텍스트를 검은색으로
            
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # 디스커버리 성과 요약
        if '디스커버리' in brand_comparison_current.index:
            discovery_current = brand_comparison_current['디스커버리']
            discovery_previous = brand_comparison_previous.get('디스커버리', 0)
            discovery_growth = ((discovery_current - discovery_previous) / discovery_previous * 100) if discovery_previous > 0 else 0
            
            # 디스커버리 순위 변화 계산
            discovery_rank_change = rank_changes.get('디스커버리', 0)
            discovery_current_rank = list(brand_comparison_current.index).index('디스커버리') + 1
            
            # 시장 점유율 변화 계산
            discovery_current_share = (discovery_current / brand_comparison_current.sum()) * 100
            discovery_previous_share = (discovery_previous / brand_comparison_previous.sum()) * 100 if brand_comparison_previous.sum() > 0 else 0
            discovery_share_change = discovery_current_share - discovery_previous_share
            
            st.subheader("🎯 디스커버리 브랜드 성과")
            
            # 요약 정보 표시
            if analysis_type == "총 매출 기준":
                st.info(f"**매출 {discovery_current/100_000_000:.2f}억원** | **브랜드 순위 {discovery_current_rank}위{format_rank_change(discovery_current_rank, discovery_rank_change)[len(str(discovery_current_rank)):]}** | **시장 점유율 {discovery_current_share:.1f}%({discovery_share_change:+.1f}%)**")
            else:
                st.info(f"**평균 매출 {discovery_current/100_000_000:.2f}억원** | **브랜드 순위 {discovery_current_rank}위{format_rank_change(discovery_current_rank, discovery_rank_change)[len(str(discovery_current_rank)):]}** | **시장 점유율 {discovery_current_share:.1f}%({discovery_share_change:+.1f}%)**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if analysis_type == "총 매출 기준":
                    st.metric(
                        f"{current_col} 총 매출", 
                        f"{discovery_current/100_000_000:.2f}억원",
                        delta=f"{discovery_growth:+.1f}%"
                    )
                else:
                    st.metric(
                        f"{current_col} 평균 매출", 
                        f"{discovery_current/100_000_000:.2f}억원",
                        delta=f"{discovery_growth:+.1f}%"
                    )
            
            with col2:
                rank_display = format_rank_change(discovery_current_rank, discovery_rank_change)
                st.metric("브랜드 순위", rank_display)
            
            with col3:
                st.metric("시장 점유율", f"{discovery_current_share:.1f}%", delta=f"{discovery_share_change:+.1f}%")
            
            with col4:
                if discovery_growth > 0:
                    st.metric("성장률", f"🟢 ▲ {discovery_growth:.1f}%")
                elif discovery_growth < 0:
                    st.metric("성장률", f"🔴 ▼ {discovery_growth:.1f}%")
                else:
                    st.metric("성장률", f"⚪ {discovery_growth:.1f}%")
        
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
        
        # 합계 행 추가
        total_current = brand_comparison_current.sum()
        total_previous = brand_comparison_previous.sum()
        total_growth = ((total_current - total_previous) / total_previous * 100) if total_previous > 0 else 0
        
        # 합계 행 데이터
        if analysis_type == "총 매출 기준":
            total_current_formatted = f"{total_current/100_000_000:.2f}억원"
            total_previous_formatted = f"{total_previous/100_000_000:.2f}억원"
        else:
            total_current_formatted = f"{total_current/100_000_000:.2f}억원"
            total_previous_formatted = f"{total_previous/100_000_000:.2f}억원"
        
        # 합계 행을 테이블 데이터에 직접 추가
        table_data.append({
            '순위변동': '',
            '브랜드': '합계',
            current_col_name: total_current_formatted,
            previous_col_name: total_previous_formatted,
            '증감률': f"{total_growth:+.1f}%"
        })
        
        # 최종 DataFrame 생성
        final_table_df = pd.DataFrame(table_data)
        
        # 디스커버리와 합계 행 강조를 위한 스타일링
        def highlight_discovery_and_total(row):
            if row['브랜드'] == '디스커버리':
                return ['background-color: #FFE6E6'] * len(row)
            elif row['브랜드'] == '합계':
                return ['background-color: #E6F3FF', 'font-weight: bold'] * len(row)
            return [''] * len(row)
        
        styled_table = final_table_df.style.apply(highlight_discovery_and_total, axis=1)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
    
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