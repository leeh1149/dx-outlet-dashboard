# 🚀 Streamlit Cloud 배포 가이드

## 📋 배포 전 준비사항

### 1. 필수 파일 확인
- ✅ `dashboard_streamlit.py` - 메인 대시보드 파일
- ✅ `requirements.txt` - Python 패키지 의존성
- ✅ `README.md` - 프로젝트 설명서
- ⚠️ `DX OUTLET MS DB.csv` - 데이터 파일 (GitHub에 업로드 필요)

### 2. GitHub 저장소 생성
1. [GitHub](https://github.com)에 로그인
2. "New repository" 클릭
3. 저장소 이름 입력 (예: `dx-outlet-dashboard`)
4. Public으로 설정 (Streamlit Cloud 무료 배포를 위해)
5. "Create repository" 클릭

## 🔧 배포 단계

### Step 1: GitHub에 파일 업로드
```bash
# 로컬에서 Git 초기화 (이미 Git 저장소가 아닌 경우)
git init
git add .
git commit -m "Initial commit: DX OUTLET Dashboard"

# GitHub 저장소와 연결
git remote add origin https://github.com/[사용자명]/[저장소명].git
git branch -M main
git push -u origin main
```

### Step 2: Streamlit Cloud 배포
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. "Sign in with GitHub" 클릭하여 GitHub 계정으로 로그인
3. "New app" 버튼 클릭
4. 배포 설정:
   - **Repository**: 생성한 GitHub 저장소 선택
   - **Branch**: `main` 선택
   - **Main file path**: `dashboard_streamlit.py`
   - **App URL**: 원하는 URL 입력 (예: `dx-outlet-dashboard`)

### Step 3: 고급 설정 (선택사항)
- **Python version**: 3.9 이상
- **Secrets**: API 키 등 민감한 정보가 있는 경우

## ⚠️ 주의사항

### 1. 데이터 파일 업로드
- `DX OUTLET MS DB.csv` 파일을 GitHub에 업로드해야 함
- 파일 크기가 25MB를 초과하면 Git LFS 사용 필요

### 2. API 키 보안
- 재미나이 API 키는 Streamlit Cloud의 Secrets 기능 사용
- 코드에서 직접 API 키를 하드코딩하지 말 것

### 3. 파일 경로
- 로컬에서는 `'DX OUTLET MS DB.csv'`로 직접 로드
- Streamlit Cloud에서는 상대 경로 사용

## 🔍 배포 후 확인사항

### 1. 앱 접속 테스트
- 배포된 URL로 접속
- 데이터 로드 확인
- 모든 기능 정상 작동 확인

### 2. 성능 모니터링
- 로딩 시간 확인
- 메모리 사용량 모니터링
- 오류 로그 확인

## 🛠️ 문제 해결

### 자주 발생하는 문제
1. **데이터 파일을 찾을 수 없음**
   - CSV 파일이 GitHub에 업로드되었는지 확인
   - 파일명과 경로가 정확한지 확인

2. **패키지 설치 오류**
   - `requirements.txt`의 패키지 버전 확인
   - 호환되지 않는 패키지 제거

3. **API 키 오류**
   - Streamlit Cloud Secrets에 API 키 등록
   - 코드에서 환경변수로 API 키 읽기

## 📞 지원
배포 과정에서 문제가 발생하면:
1. Streamlit Cloud 로그 확인
2. GitHub Issues에 문제 보고
3. Streamlit Community Forum 참조