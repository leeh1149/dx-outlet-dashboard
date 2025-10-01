@echo off
chcp 65001 >nul
echo ================================================================================
echo Git 명령어로 GitHub에 업로드하기 (GitHub Desktop 대신 사용 가능)
echo ================================================================================
echo.
echo 주의: 이 방법은 Git이 설치되어 있어야 합니다.
echo Git 다운로드: https://git-scm.com/download/win
echo.
echo GitHub Desktop 사용을 더 추천합니다!
echo.
pause
echo.

REM Git 초기화
echo [1/6] Git 저장소 초기화 중...
git init
echo.

REM 사용자 설정
echo [2/6] Git 사용자 설정...
git config user.email "leeh1149@gmail.com"
git config user.name "leeh1149"
echo.

REM 파일 추가
echo [3/6] 파일 추가 중...
git add dashboard_streamlit.py
git add requirements.txt
git add README.md
git add .gitignore
echo.

REM 커밋
echo [4/6] 커밋 생성 중...
git commit -m "Initial commit: DX Outlet Dashboard"
echo.

REM 브랜치 이름 변경
echo [5/6] 브랜치를 main으로 설정...
git branch -M main
echo.

echo [6/6] GitHub 원격 저장소 연결
echo.
echo ================================================================================
echo 다음 단계:
echo ================================================================================
echo.
echo 1. GitHub.com에서 새 저장소 만들기:
echo    https://github.com/new
echo.
echo 2. Repository name: dx-outlet-dashboard
echo.
echo 3. Public으로 설정 (또는 Private)
echo.
echo 4. "Create repository" 클릭
echo.
echo 5. 생성 후 나오는 명령어 중 아래 명령어를 복사해서 실행:
echo.
echo    git remote add origin https://github.com/YOUR-USERNAME/dx-outlet-dashboard.git
echo    git push -u origin main
echo.
echo ================================================================================
echo.
echo GitHub Desktop을 사용하면 이 과정이 훨씬 쉽습니다!
echo.
pause



