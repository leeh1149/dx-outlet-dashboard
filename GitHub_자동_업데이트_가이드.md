# 🚀 GitHub 자동 업데이트 가이드

## 📋 개요
`dashboard_streamlit.py` 파일을 수정할 때마다 GitHub 저장소에 자동으로 업데이트하는 방법을 제공합니다.

## 🛠️ 자동화 방법

### 방법 1: 배치 파일 사용 (간단)
```bash
GitHub_자동_업데이트_스크립트.bat
```

**사용법:**
1. `dashboard_streamlit.py` 파일 수정 완료
2. `GitHub_자동_업데이트_스크립트.bat` 더블클릭
3. 자동으로 GitHub에 업데이트

### 방법 2: Python 스크립트 사용 (고급)
```bash
python GitHub_자동_업데이트_고급_스크립트.py
```

**사용법:**
1. `dashboard_streamlit.py` 파일 수정 완료
2. 명령 프롬프트에서 Python 스크립트 실행
3. 상세한 로그와 함께 자동 업데이트

## 🔧 설정 요구사항

### Git 설치
- [Git for Windows](https://git-scm.com/download/win) 설치 필요
- 설치 후 명령 프롬프트 재시작

### GitHub 인증
1. **Personal Access Token 생성**:
   - GitHub → Settings → Developer settings → Personal access tokens
   - "Generate new token" 클릭
   - 권한: `repo` (전체 저장소 접근)
   - 토큰 복사 및 안전하게 보관

2. **Git Credential Manager 설정**:
   ```bash
   git config --global credential.helper manager-core
   ```

## 📋 자동화 프로세스

### 1단계: 파일 수정
- `dashboard_streamlit.py` 파일 수정
- 필요한 경우 다른 파일도 수정

### 2단계: 자동 업데이트 실행
- 배치 파일 또는 Python 스크립트 실행
- 자동으로 다음 작업 수행:
  - Git 저장소 상태 확인
  - 변경사항 추가 (`git add .`)
  - 커밋 생성 (`git commit`)
  - GitHub에 푸시 (`git push`)

### 3단계: Streamlit Cloud 자동 재배포
- GitHub 업데이트 완료
- Streamlit Cloud가 자동으로 변경사항 감지
- 약 2-3분 후 재배포 완료

## 🎯 사용 시나리오

### 시나리오 1: 대시보드 기능 추가
1. `dashboard_streamlit.py`에 새 기능 추가
2. `GitHub_자동_업데이트_스크립트.bat` 실행
3. Streamlit Cloud에서 자동 재배포
4. 대시보드에서 새 기능 확인

### 시나리오 2: 버그 수정
1. `dashboard_streamlit.py`에서 버그 수정
2. `python GitHub_자동_업데이트_고급_스크립트.py` 실행
3. 상세한 로그로 업데이트 과정 확인
4. Streamlit Cloud에서 수정된 버전 확인

### 시나리오 3: UI 개선
1. 대시보드 UI 개선
2. 자동 업데이트 스크립트 실행
3. 실시간으로 변경사항 반영

## ⚠️ 주의사항

### 파일 백업
- 중요한 수정 전에는 파일 백업 권장
- Git 히스토리로 이전 버전 복원 가능

### 테스트
- 로컬에서 먼저 테스트 후 업데이트
- Streamlit Cloud 재배포 후 기능 확인

### 인증 문제
- GitHub 인증 실패 시 Personal Access Token 확인
- 네트워크 연결 상태 확인

## 🔍 문제 해결

### 자주 발생하는 문제

1. **Git 인증 실패**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **원격 저장소 오류**
   ```bash
   git remote -v
   git remote set-url origin https://github.com/leeh1149/OUTLETDASHBOARD.git
   ```

3. **커밋 충돌**
   ```bash
   git pull origin main
   git push origin main
   ```

## 📞 지원
문제가 발생하면:
1. 오류 메시지 확인
2. Git 상태 확인 (`git status`)
3. 수동 업데이트 고려
4. GitHub 웹사이트에서 직접 파일 수정

## 🎉 장점
- **자동화**: 수동 업로드 불필요
- **빠른 배포**: 수정 후 즉시 반영
- **버전 관리**: Git 히스토리로 변경사항 추적
- **안정성**: 자동화된 프로세스로 실수 방지
