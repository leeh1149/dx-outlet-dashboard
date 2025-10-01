import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json

def analyze_store_efficiency():
    """
    디스커버리 브랜드의 매장별 평수 대비 시즌별 매출액 분석
    """
    # CSV 파일 읽기
    df = pd.read_csv('DX OUTLET MS DB.csv')
    
    # 디스커버리 브랜드만 필터링
    discovery_df = df[df['브랜드'] == '디스커버리'].copy()
    
    # 매장 면적이 있는 데이터만 필터링 (NaN 제거)
    discovery_df = discovery_df.dropna(subset=['매장 면적'])
    
    # 시즌별 컬럼 정의
    seasons = ['23SS', '23FW', '24SS', '24FW', '25SS']
    
    # 매장별 효율성 계산
    efficiency_data = []
    
    for _, row in discovery_df.iterrows():
        store_name = row['매장명']
        area = row['매장 면적']
        
        store_data = {
            '매장명': store_name,
            '유통사': row['유통사'],
            '매장면적': area,
            '매장면적_평': area * 3.3058  # 평방미터를 평으로 변환
        }
        
        # 각 시즌별 매출액과 효율성 계산 (평수 대비)
        area_pyeong = area * 3.3058  # 평방미터를 평으로 변환
        
        for season in seasons:
            sales = row[season] if pd.notna(row[season]) else 0
            efficiency = sales / area_pyeong if area_pyeong > 0 else 0  # 평당 매출액
            
            store_data[f'{season}_매출액'] = sales
            store_data[f'{season}_효율성'] = efficiency
        
        efficiency_data.append(store_data)
    
    efficiency_df = pd.DataFrame(efficiency_data)
    
    # 매장별 평균 효율성 계산
    efficiency_columns = [f'{season}_효율성' for season in seasons]
    efficiency_df['평균효율성'] = efficiency_df[efficiency_columns].mean(axis=1)
    
    # 효율성 순으로 정렬
    efficiency_df = efficiency_df.sort_values('평균효율성', ascending=False)
    
    return efficiency_df, seasons

def create_efficiency_charts(efficiency_df, seasons):
    """
    매장 효율성 시각화 차트 생성
    """
    charts = {}
    
    # 1. 매장별 평균 효율성 순위 차트
    fig1 = go.Figure()
    
    fig1.add_trace(go.Bar(
        x=efficiency_df['매장명'],
        y=efficiency_df['평균효율성'],
        text=[f"{val:,.0f}" for val in efficiency_df['평균효율성']],
        textposition='auto',
        marker_color='lightblue',
        name='평균 효율성'
    ))
    
    fig1.update_layout(
        title='디스커버리 매장별 평균 효율성 (평당 매출액)',
        xaxis_title='매장명',
        yaxis_title='평당 매출액 (원)',
        xaxis_tickangle=-45,
        height=500
    )
    
    charts['efficiency_ranking'] = fig1.to_html(full_html=False, include_plotlyjs=False)
    
    # 2. 시즌별 효율성 히트맵
    heatmap_data = []
    for season in seasons:
        season_data = efficiency_df[f'{season}_효율성'].tolist()
        heatmap_data.append(season_data)
    
    fig2 = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=efficiency_df['매장명'].tolist(),
        y=seasons,
        colorscale='Viridis',
        text=[[f"{val:,.0f}" for val in row] for row in heatmap_data],
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig2.update_layout(
        title='디스커버리 매장별 시즌별 효율성 히트맵',
        xaxis_title='매장명',
        yaxis_title='시즌',
        height=400
    )
    
    charts['efficiency_heatmap'] = fig2.to_html(full_html=False, include_plotlyjs=False)
    
    # 3. 매장면적 vs 평균효율성 산점도
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=efficiency_df['매장면적'],
        y=efficiency_df['평균효율성'],
        mode='markers+text',
        text=efficiency_df['매장명'],
        textposition='top center',
        marker=dict(
            size=10,
            color=efficiency_df['평균효율성'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="평균 효율성")
        ),
        name='매장'
    ))
    
    fig3.update_layout(
        title='매장면적 vs 평균효율성',
        xaxis_title='매장면적 (평방미터)',
        yaxis_title='평균 효율성 (평당 매출액)',
        height=500
    )
    
    charts['area_vs_efficiency'] = fig3.to_html(full_html=False, include_plotlyjs=False)
    
    # 4. 시즌별 매출액 트렌드
    fig4 = go.Figure()
    
    for _, row in efficiency_df.head(10).iterrows():  # 상위 10개 매장만 표시
        store_name = row['매장명']
        season_sales = [row[f'{season}_매출액'] for season in seasons]
        
        fig4.add_trace(go.Scatter(
            x=seasons,
            y=season_sales,
            mode='lines+markers',
            name=store_name,
            line=dict(width=2)
        ))
    
    fig4.update_layout(
        title='상위 10개 매장의 시즌별 매출액 트렌드',
        xaxis_title='시즌',
        yaxis_title='매출액 (원)',
        height=500
    )
    
    charts['seasonal_trend'] = fig4.to_html(full_html=False, include_plotlyjs=False)
    
    return charts

def get_store_details(efficiency_df, store_name):
    """
    특정 매장의 상세 정보 반환
    """
    store_data = efficiency_df[efficiency_df['매장명'] == store_name]
    
    if store_data.empty:
        return None
    
    store_info = store_data.iloc[0]
    
    details = {
        '매장명': store_info['매장명'],
        '유통사': store_info['유통사'],
        '매장면적': store_info['매장면적'],
        '매장면적_평': store_info['매장면적_평'],
        '평균효율성': store_info['평균효율성'],
        '시즌별_매출액': {},
        '시즌별_효율성': {}
    }
    
    seasons = ['23SS', '23FW', '24SS', '24FW', '25SS']
    for season in seasons:
        details['시즌별_매출액'][season] = store_info[f'{season}_매출액']
        details['시즌별_효율성'][season] = store_info[f'{season}_효율성']
    
    return details

if __name__ == "__main__":
    # 분석 실행
    efficiency_df, seasons = analyze_store_efficiency()
    
    print("=== 디스커버리 매장 효율성 분석 결과 ===")
    print(f"총 매장 수: {len(efficiency_df)}")
    print("\n상위 10개 매장 효율성:")
    print(efficiency_df[['매장명', '유통사', '매장면적', '평균효율성']].head(10))
    
    # 차트 생성
    charts = create_efficiency_charts(efficiency_df, seasons)
    
    # 결과를 JSON 파일로 저장
    result = {
        'efficiency_data': efficiency_df.to_dict('records'),
        'charts': charts,
        'seasons': seasons
    }
    
    with open('store_efficiency_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n분석 완료! 결과가 'store_efficiency_analysis.json'에 저장되었습니다.")
