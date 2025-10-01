# 📊 DX OUTLET 매출 분석 대시보드

DX OUTLET의 매장별, 브랜드별 매출 데이터를 시각화하고 분석할 수 있는 Streamlit 대시보드입니다.

## 🚀 주요 기능

### 📈 시계열 분석
- 시즌별 매출 추이 분석 (23SS ~ 25SS)
- 시즌별 매출 비교 차트

### 🏪 매장별 분석
- 매장별 매출 순위 (TOP 10)
- 매장 면적 대비 매출 분석
- 유통사별 매장 현황

### 🏷️ 브랜드별 분석
- 브랜드별 매출 비중 (파이 차트)
- 브랜드별 시계열 매출 히트맵
- 브랜드 성과 분석

### 🔍 데이터 필터링
- 유통사별 필터링 (롯데, 신세계, 현대, 마리오)
- 매장별 필터링
- 브랜드별 필터링

### 📋 데이터 관리
- 실시간 데이터 테이블
- 필터링된 데이터 다운로드 (CSV)
- 주요 지표 대시보드

## 🛠️ 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd ai-study
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 대시보드 실행
```bash
streamlit run dashboard_streamlit.py
```

## 📊 데이터 구조

### CSV 파일 구조
- **형태**: 아울렛
- **유통사**: 롯데, 신세계, 현대, 마리오
- **매장명**: 지역별 아울렛 매장명
- **브랜드**: 디스커버리, 노스페이스, 코오롱스포츠, K2 등
- **시즌별 매출**: 23SS, 23FW, 24SS, 24FW, 25SS
- **매장 면적**: 매장 크기 정보 (㎡)

### 데이터 전처리
- 매출 데이터를 숫자형으로 변환
- 결측값을 0으로 처리
- 매장 면적 데이터 정규화

## 🌐 배포

### Streamlit Cloud 자동 배포 (추천)

#### 1단계: GitHub 저장소 생성
```bash
# Git 저장소 초기화
git init
git add .
git commit -m "Initial commit: DX OUTLET 대시보드"

# GitHub에 새 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git branch -M main
git push -u origin main
```

#### 2단계: Streamlit Cloud 배포
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. "New app" 클릭
3. GitHub 계정 연결
4. 저장소 선택: `YOUR_USERNAME/YOUR_REPOSITORY`
5. **Main file path**: `streamlit_app.py` (중요!)
6. **App URL**: 원하는 URL 설정 (예: `dx-outlet-dashboard`)
7. "Deploy!" 클릭

#### 3단계: 자동 배포 확인
- 코드가 업데이트되면 자동으로 재배포됩니다
- GitHub에 푸시할 때마다 Streamlit Cloud가 자동으로 앱을 업데이트합니다

### GitHub Actions 자동 배포
저장소에 포함된 `.github/workflows/deploy.yml` 파일이 자동으로 배포를 관리합니다.

## 📁 프로젝트 구조

```
ai-study/
├── streamlit_app.py           # Streamlit Cloud 메인 앱 (배포용)
├── dashboard_streamlit.py     # 로컬 개발용 대시보드
├── requirements.txt           # Python 의존성
├── packages.txt              # 시스템 패키지 (필요시)
├── README.md                 # 프로젝트 문서
├── DX OUTLET MS DB.csv       # 데이터 파일
├── .streamlit/
│   └── config.toml           # Streamlit 설정
└── .github/
    └── workflows/
        └── deploy.yml        # GitHub Actions 배포 설정
```

## 🔧 기술 스택

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Deployment**: GitHub Actions, Streamlit Cloud

## 📈 주요 지표

- 총 매장 수
- 총 브랜드 수
- 25SS 총 매출
- 평균 매장 면적

## 🎯 사용 방법

1. **필터 설정**: 사이드바에서 유통사, 매장, 브랜드를 선택
2. **탭 탐색**: 시계열, 매장별, 브랜드별 분석 탭 확인
3. **데이터 다운로드**: 테이블 탭에서 필터링된 데이터 다운로드
4. **인터랙티브 차트**: 차트 클릭 및 호버로 상세 정보 확인

## 📞 문의

프로젝트 관련 문의사항이 있으시면 GitHub Issues를 통해 연락해주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
