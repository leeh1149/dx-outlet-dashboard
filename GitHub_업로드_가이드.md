# 🚀 GitHub 업로드 가이드 (Git 없이)

## 방법 1: GitHub 웹사이트에서 직접 업로드

### 1단계: GitHub 저장소 생성
1. [GitHub](https://github.com)에 로그인
2. 우측 상단 "+" 버튼 → "New repository" 클릭
3. 저장소 정보 입력:
   - **Repository name**: `dx-outlet-dashboard`
   - **Description**: `DX OUTLET 매출 대시보드`
   - **Public** 선택 (Streamlit Cloud 무료 배포를 위해)
   - "Create repository" 클릭

### 2단계: 파일 업로드
1. 생성된 저장소 페이지에서 "uploading an existing file" 클릭
2. 다음 파일들을 드래그 앤 드롭 또는 "choose your files" 클릭:
   - `dashboard_streamlit.py`
   - `requirements.txt`
   - `README.md`
   - `DX OUTLET MS DB.csv` (데이터 파일)
   - `STREAMLIT_CLOUD_배포_가이드.md`

3. "Commit changes" 클릭

## 방법 2: Git 설치 후 자동화 스크립트 사용

### 1단계: Git 설치
1. [Git for Windows](https://git-scm.com/download/win) 다운로드
2. 설치 프로그램 실행 (기본 설정으로 설치)
3. 설치 완료 후 명령 프롬프트 재시작

### 2단계: 자동화 스크립트 실행
1. `배포_자동화_스크립트.bat` 파일 더블클릭
2. 스크립트가 자동으로 Git 설정을 완료
3. GitHub 저장소 생성 후 제공된 명령어 실행

## 방법 3: GitHub Desktop 사용

### 1단계: GitHub Desktop 설치
1. [GitHub Desktop](https://desktop.github.com/) 다운로드
2. 설치 후 GitHub 계정으로 로그인

### 2단계: 저장소 생성 및 업로드
1. "Create a new repository on your hard drive" 클릭
2. 저장소 정보 입력:
   - **Name**: `dx-outlet-dashboard`
   - **Local path**: 현재 프로젝트 폴더
   - **Public** 선택
3. "Create repository" 클릭
4. 모든 파일이 자동으로 추가됨
5. "Commit to main" 클릭
6. "Publish repository" 클릭

## ⚠️ 중요 사항

### 필수 파일 확인
- ✅ `dashboard_streamlit.py` - 메인 대시보드
- ✅ `requirements.txt` - Python 패키지 의존성
- ✅ `README.md` - 프로젝트 설명서
- ⚠️ `DX OUTLET MS DB.csv` - 데이터 파일 (반드시 업로드!)

### 파일 크기 제한
- GitHub 무료 계정: 파일당 100MB 제한
- CSV 파일이 100MB를 초과하면 Git LFS 사용 필요

### 보안 주의사항
- API 키는 코드에 직접 포함하지 말 것
- Streamlit Cloud Secrets 기능 사용 권장

## 🎯 다음 단계: Streamlit Cloud 배포

GitHub 업로드 완료 후:
1. [Streamlit Cloud](https://share.streamlit.io/) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 배포 설정:
   - **Repository**: `dx-outlet-dashboard`
   - **Branch**: `main`
   - **Main file path**: `dashboard_streamlit.py`
5. "Deploy" 클릭

배포 완료 후 제공되는 URL로 대시보드에 접근 가능!
