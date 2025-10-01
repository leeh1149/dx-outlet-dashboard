@echo off
echo ========================================
echo DX OUTLET Dashboard 배포 자동화 스크립트
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

echo 3. Git 저장소 초기화...
git init
if %errorlevel% neq 0 (
    echo Git 초기화 실패
    pause
    exit /b 1
)

echo 4. 파일 추가...
git add .
if %errorlevel% neq 0 (
    echo 파일 추가 실패
    pause
    exit /b 1
)

echo 5. 커밋 생성...
git commit -m "Initial commit: DX OUTLET Dashboard"
if %errorlevel% neq 0 (
    echo 커밋 생성 실패
    pause
    exit /b 1
)

echo 6. 메인 브랜치 설정...
git branch -M main
if %errorlevel% neq 0 (
    echo 브랜치 설정 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo Git 설정 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. GitHub에서 새 저장소를 생성하세요 (Public으로 설정)
echo 2. 아래 명령어를 실행하세요:
echo    git remote add origin https://github.com/[사용자명]/[저장소명].git
echo    git push -u origin main
echo.
echo 3. Streamlit Cloud에서 배포하세요:
echo    https://share.streamlit.io/
echo.
pause
