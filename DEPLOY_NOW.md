# 🚀 지금 바로 배포하기!

**GitHub 저장소**: https://github.com/leeh1149/OUTLETDASHBOARD.git
**계정**: leeh1149@gmail.com

---

## ✅ 1단계: GitHub에 파일 업로드 (5분)

### 방법 A: GitHub Desktop 사용 (강력 추천!)

#### 1. GitHub Desktop이 없다면 설치
- 다운로드: https://desktop.github.com
- 설치 후 GitHub 계정(leeh1149@gmail.com)으로 로그인

#### 2. 저장소 클론
1. GitHub Desktop 실행
2. **File → Clone repository** 클릭
3. **URL** 탭 선택
4. Repository URL 입력:
   ```
   https://github.com/leeh1149/OUTLETDASHBOARD.git
   ```
5. Local path 선택: 
   ```
   C:\Users\AD0581\Documents\OUTLETDASHBOARD
   ```
6. **Clone** 클릭

#### 3. 파일 복사
다음 파일들을 복사:

**원본 위치**: `C:\Users\AD0581\Documents\ai study\`
**대상 위치**: `C:\Users\AD0581\Documents\OUTLETDASHBOARD\`

복사할 파일:
- ✅ dashboard_streamlit.py
- ✅ requirements.txt
- ✅ README.md
- ✅ .gitignore
- 📁 DX OUTLET MS DB.csv (선택사항, 용량이 크지 않다면)
- 📁 매출데이터.xlsx (선택사항)

#### 4. 커밋 및 푸시
1. GitHub Desktop에서 왼쪽에 변경된 파일 목록 확인
2. 왼쪽 하단 "Summary" 입력:
   ```
   Initial commit: DX Outlet Dashboard
   ```
3. **"Commit to main"** 클릭
4. 상단 **"Push origin"** 클릭

#### 5. ✅ 업로드 완료!
브라우저에서 확인: https://github.com/leeh1149/OUTLETDASHBOARD

---

### 방법 B: Git 명령어 사용 (개발자용)

PowerShell이나 명령 프롬프트를 열고:

```powershell
# 현재 프로젝트 폴더로 이동
cd "C:\Users\AD0581\Documents\ai study"

# Git 초기화 (이미 되어있을 수도 있음)
git init

# 원격 저장소 연결
git remote add origin https://github.com/leeh1149/OUTLETDASHBOARD.git

# 파일 추가
git add dashboard_streamlit.py
git add requirements.txt
git add README.md
git add .gitignore

# 커밋
git commit -m "Initial commit: DX Outlet Dashboard"

# 브랜치 이름 확인 및 변경
git branch -M main

# GitHub에 푸시
git push -u origin main
```

---

## ✅ 2단계: Streamlit Cloud 배포 (5분)

### 1. Streamlit Cloud 접속
👉 https://streamlit.io/cloud

### 2. 로그인
- **"Sign in"** 또는 **"Sign up"** 클릭
- **"Continue with GitHub"** 선택
- GitHub 계정으로 로그인
- **"Authorize streamlit"** 클릭 (권한 승인)

### 3. 앱 생성
1. **"New app"** 버튼 클릭

2. **배포 설정 입력:**
   ```
   Repository: leeh1149/OUTLETDASHBOARD
   Branch: main
   Main file path: dashboard_streamlit.py
   ```

3. **App URL** (선택사항):
   - 원하는 이름으로 변경 가능
   - 예: `dx-outlet-dashboard`
   - 최종 URL: `https://dx-outlet-dashboard.streamlit.app`

4. **Advanced settings** 클릭 (선택사항):
   - Python version: 3.11 (기본값)

5. **"Deploy!"** 클릭

### 4. 배포 대기
- 빌드 로그가 실시간으로 표시됩니다
- 약 2-5분 소요 ⏰
- 초록색 "Your app is live!" 메시지가 나타나면 완료!

### 5. ✅ 배포 완료!
```
🎉 https://your-app-name.streamlit.app
```

---

## 🎯 요약

1. **GitHub에 업로드** (5분)
   - GitHub Desktop으로 저장소 클론
   - 파일 복사
   - 커밋 & 푸시

2. **Streamlit Cloud 배포** (5분)
   - https://streamlit.io/cloud
   - Continue with GitHub
   - New app → 저장소 선택 → Deploy!

3. **완료!** 🚀
   - 전 세계 어디서나 접속 가능!

---

## 🆘 문제 해결

### GitHub 업로드 실패
- **인증 오류**: GitHub에 로그인되어 있는지 확인
- **권한 오류**: 저장소가 본인 계정인지 확인

### Streamlit Cloud 배포 실패
- **"File not found"**: Main file path가 `dashboard_streamlit.py`인지 확인
- **"Module not found"**: requirements.txt가 업로드되었는지 확인
- **빌드 실패**: Logs 탭에서 자세한 오류 확인

### 파일이 너무 큰 경우 (100MB+)
GitHub는 대용량 파일 제한이 있습니다.
- CSV/Excel 파일은 .gitignore에 추가
- 사용자가 대시보드에서 직접 업로드하도록 설계
  (현재 앱은 이미 이렇게 되어 있음!)

---

## 📞 다음 단계

배포 완료 후:
1. ✅ URL 북마크 저장
2. ✅ 모바일에서 접속 테스트
3. ✅ 친구들과 공유
4. ✅ 필요시 코드 수정 후 다시 푸시 (자동 재배포!)

**화이팅! 🚀**



