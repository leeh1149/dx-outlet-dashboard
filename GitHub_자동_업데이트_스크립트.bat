@echo off
echo ========================================
echo GitHub 자동 업데이트 스크립트
echo ========================================
echo.

echo 1. Git 설치 확인 중...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git이 설치되어 있지 않습니다.
    echo Git을 설치해주세요: https://git-scm.com/download/win
    echo.
    echo 설치 후 이 스크립트를 다시 실행해주세요.
    pause
    exit /b 1
)

echo Git이 설치되어 있습니다.
echo.

echo 2. 현재 디렉토리 확인...
echo 현재 위치: %CD%
echo.

echo 3. Git 저장소 상태 확인...
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo Git 저장소가 초기화되지 않았습니다.
    echo Git 저장소를 초기화합니다...
    git init
    git remote add origin https://github.com/leeh1149/OUTLETDASHBOARD.git
    git branch -M main
)

echo 4. 변경된 파일 확인...
git add .
git status

echo 5. 변경사항 커밋...
git commit -m "Update dashboard_streamlit.py - Improved features and UI"

echo 6. GitHub에 푸시...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ 업데이트 완료!
    echo ========================================
    echo.
    echo GitHub 저장소가 성공적으로 업데이트되었습니다.
    echo Streamlit Cloud에서 자동으로 재배포됩니다.
    echo.
    echo 대시보드 URL: https://jb9gcmjivepixpauprtsfy.streamlit.app/
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 업데이트 실패
    echo ========================================
    echo.
    echo GitHub에 푸시하는 중 오류가 발생했습니다.
    echo GitHub 인증이 필요할 수 있습니다.
    echo.
    echo 해결 방법:
    echo 1. GitHub Personal Access Token 설정
    echo 2. Git Credential Manager 사용
    echo 3. 수동으로 GitHub에서 파일 업데이트
    echo.
)

pause
