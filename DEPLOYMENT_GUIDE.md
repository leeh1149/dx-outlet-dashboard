# 🚀 Streamlit Cloud 자동 배포 가이드

이 가이드는 DX OUTLET 매출 분석 대시보드를 Streamlit Cloud에 자동 배포하는 방법을 안내합니다.

## 📋 사전 준비사항

1. **GitHub 계정** - 무료 계정으로 충분
2. **Streamlit Cloud 계정** - GitHub 계정으로 자동 가입 가능
3. **Git 설치** - [Git 다운로드](https://git-scm.com/downloads)

## 🔧 1단계: GitHub 저장소 생성

### 1.1 로컬 Git 저장소 초기화
```bash
# 프로젝트 폴더로 이동
cd "C:\Users\AD0581\Documents\ai study"

# Git 저장소 초기화
git init

# 모든 파일 추가
git add .

# 첫 번째 커밋
git commit -m "Initial commit: DX OUTLET 대시보드"
```

### 1.2 GitHub에서 새 저장소 생성
1. [GitHub.com](https://github.com) 접속
2. "New repository" 클릭
3. 저장소 이름 입력 (예: `dx-outlet-dashboard`)
4. "Public" 선택 (무료 Streamlit Cloud 사용)
5. "Create repository" 클릭

### 1.3 로컬 저장소와 GitHub 연결
```bash
# GitHub 저장소 URL로 연결 (YOUR_USERNAME을 실제 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/dx-outlet-dashboard.git

# main 브랜치로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 🌐 2단계: Streamlit Cloud 배포

### 2.1 Streamlit Cloud 접속
1. [share.streamlit.io](https://share.streamlit.io/) 접속
2. "Sign in with GitHub" 클릭
3. GitHub 계정으로 로그인

### 2.2 새 앱 생성
1. "New app" 버튼 클릭
2. 다음 설정 입력:
   - **Repository**: `YOUR_USERNAME/dx-outlet-dashboard`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py` ⚠️ **중요!**
   - **App URL**: `dx-outlet-dashboard` (원하는 URL)
3. "Deploy!" 클릭

### 2.3 배포 완료
- 배포는 보통 2-3분 소요
- 배포 완료 후 자동으로 앱 URL 제공
- URL 형식: `https://dx-outlet-dashboard.streamlit.app`

## 🔄 3단계: 자동 배포 확인

### 3.1 코드 업데이트 시 자동 재배포
```bash
# 코드 수정 후
git add .
git commit -m "Update dashboard features"
git push origin main
```

### 3.2 자동 배포 확인
- GitHub에 푸시하면 Streamlit Cloud가 자동으로 변경사항 감지
- 약 1-2분 후 새 버전이 자동 배포됨
- Streamlit Cloud 대시보드에서 배포 상태 확인 가능

## 📁 중요한 파일들

### 필수 파일
- `streamlit_app.py` - Streamlit Cloud에서 실행할 메인 파일
- `requirements.txt` - Python 패키지 의존성
- `DX OUTLET MS DB.csv` - 데이터 파일

### 설정 파일
- `.streamlit/config.toml` - Streamlit 설정
- `packages.txt` - 시스템 패키지 (필요시)
- `.gitignore` - Git 무시 파일

## 🛠️ 문제 해결

### 자주 발생하는 문제들

#### 1. "Main file path" 오류
- **문제**: `dashboard_streamlit.py`로 설정
- **해결**: `streamlit_app.py`로 변경

#### 2. 데이터 파일을 찾을 수 없음
- **문제**: CSV 파일이 Git에 추가되지 않음
- **해결**: `git add "DX OUTLET MS DB.csv"` 실행

#### 3. 패키지 설치 오류
- **문제**: requirements.txt에 문제
- **해결**: 버전 호환성 확인 후 수정

#### 4. 한글 인코딩 문제
- **문제**: CSV 파일의 한글 깨짐
- **해결**: 파일이 UTF-8로 저장되었는지 확인

## 📊 배포 후 확인사항

1. **앱 로딩 확인**
   - 대시보드가 정상적으로 로드되는지 확인
   - 모든 차트와 데이터가 표시되는지 확인

2. **필터링 기능 테스트**
   - 유통사, 매장, 브랜드 필터가 작동하는지 확인
   - 데이터 테이블이 정상 업데이트되는지 확인

3. **다운로드 기능 테스트**
   - CSV 다운로드가 정상 작동하는지 확인

## 🔗 유용한 링크

- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Actions 설정](https://docs.github.com/en/actions)
- [Streamlit 공식 문서](https://docs.streamlit.io/)

## 📞 지원

문제가 발생하면:
1. Streamlit Cloud 로그 확인
2. GitHub Issues 생성
3. Streamlit 커뮤니티 포럼 활용

---

**축하합니다! 🎉 이제 DX OUTLET 대시보드가 자동으로 배포되고 있습니다!**
