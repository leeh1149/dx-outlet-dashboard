# 🚀 Streamlit Cloud 배포 가이드 (무료)

## 준비 단계

### 1. GitHub 계정 만들기
- [GitHub](https://github.com) 접속하여 계정 생성

### 2. GitHub Desktop 설치 (선택사항, 더 쉬움)
- [GitHub Desktop](https://desktop.github.com/) 다운로드 및 설치

## 배포 단계

### Step 1: GitHub에 저장소 생성

#### 방법 A: GitHub Desktop 사용 (추천)
1. GitHub Desktop 실행
2. File → Add Local Repository
3. 현재 폴더(`ai study`) 선택
4. "Publish repository" 클릭
5. 저장소 이름 입력 (예: `dx-outlet-dashboard`)
6. "Keep this code private" 체크 해제 (또는 유지)
7. Publish 클릭

#### 방법 B: 명령어 사용
```bash
cd "C:\Users\AD0581\Documents\ai study"

# Git 초기화
git init

# 파일 추가
git add dashboard_streamlit.py requirements.txt README.md .gitignore

# 데이터 파일도 추가 (필요한 경우)
git add "DX OUTLET MS DB.csv"

# 커밋
git commit -m "Initial commit: DX Outlet Dashboard"

# GitHub에 저장소 만든 후 연결
git remote add origin https://github.com/YOUR_USERNAME/dx-outlet-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2: Streamlit Cloud에 배포

1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. "Sign up" → "Continue with GitHub" 클릭
3. GitHub 계정으로 로그인 및 권한 승인
4. "New app" 클릭
5. 다음 정보 입력:
   - Repository: `your-username/dx-outlet-dashboard`
   - Branch: `main`
   - Main file path: `dashboard_streamlit.py`
6. "Deploy!" 클릭

### Step 3: 배포 완료!

몇 분 후 앱이 배포되고 다음과 같은 URL을 받게 됩니다:
```
https://your-app-name.streamlit.app
```

이 URL을 누구와도 공유할 수 있습니다! 🎉

## 추가 설정 (선택사항)

### 데이터 보안
민감한 데이터가 있다면:

1. `.gitignore`에 데이터 파일 추가:
```
*.csv
*.xlsx
```

2. Streamlit Cloud의 Secrets 기능 사용:
   - 앱 설정 → Secrets
   - 민감한 정보를 Key-Value로 저장
   - 코드에서 `st.secrets["key"]`로 접근

### 커스텀 도메인
Streamlit Cloud Pro 버전에서 지원 (유료)

## 문제 해결

### 배포 실패 시
1. requirements.txt 확인
2. 로그 확인 (Streamlit Cloud 대시보드)
3. 파일 경로 확인 (상대 경로 사용)

### 데이터 파일 로딩 오류
코드에서 데이터 파일 경로를 상대 경로로 변경:
```python
# 나쁜 예
df = pd.read_csv('C:\\Users\\..\\data.csv')

# 좋은 예
df = pd.read_csv('data.csv')
```

## 업데이트 방법

파일 수정 후:
```bash
git add .
git commit -m "Update dashboard"
git push
```

자동으로 재배포됩니다! 🔄


