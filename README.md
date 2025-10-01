# DX OUTLET 매출 대시보드

## 📊 개요
DX OUTLET 매출 데이터를 분석하고 시각화하는 Streamlit 대시보드입니다.

## 🚀 주요 기능
- **아울렛 동향 분석**: 디스커버리 브랜드의 시즌별 매출 흐름 분석
- **동업계 MS 현황**: 브랜드별 매출 순위 및 경쟁 분석
- **아울렛 매장당 효율**: 매장별 평당 매출 효율성 분석
- **매장 효율 분석**: 디스커버리 매장들의 상세 효율성 분석
- **AI 분석**: 재미나이 API를 활용한 인사이트 도출

## 📁 파일 구조
```
├── dashboard_streamlit.py    # 메인 대시보드 파일
├── requirements.txt          # Python 패키지 의존성
├── README.md                # 프로젝트 설명서
└── DX OUTLET MS DB.csv      # 데이터 파일 (업로드 필요)
```

## 🛠️ 설치 및 실행

### 로컬 실행
```bash
pip install -r requirements.txt
streamlit run dashboard_streamlit.py
```

### Streamlit Cloud 배포
1. GitHub에 저장소 생성
2. 파일들을 저장소에 업로드
3. [Streamlit Cloud](https://share.streamlit.io/)에서 배포

## 📊 데이터 요구사항
- CSV 파일명: `DX OUTLET MS DB.csv`
- 필수 컬럼: 브랜드, 유통사, 매장명, 매장 면적, 시즌별 매출 데이터

## 🤖 AI 분석 기능
- 재미나이 2.5 Flash API 사용
- Google AI Studio에서 API 키 발급 필요
- 아울렛 동향 및 동업계 MS 현황 AI 분석 제공

## 📈 분석 내용
- 유통사별 디스커버리 매출 비교
- 브랜드별 MS 현황 및 순위 변화
- 매장별 평당 매출 효율성 분석
- 시즌별 매출 패턴 분석