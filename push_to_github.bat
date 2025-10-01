@echo off
chcp 65001 >nul
echo ================================================================================
echo GitHub에 프로젝트 업로드하기
echo ================================================================================
echo.
echo 저장소: https://github.com/leeh1149/OUTLETDASHBOARD.git
echo.
pause
echo.

cd /d "%~dp0"

echo [1/7] Git 설정 확인...
git config user.email "leeh1149@gmail.com"
git config user.name "leeh1149"
echo ✅ 완료
echo.

echo [2/7] Git 초기화...
git init
echo ✅ 완료
echo.

echo [3/7] 원격 저장소 연결...
git remote remove origin 2>nul
git remote add origin https://github.com/leeh1149/OUTLETDASHBOARD.git
echo ✅ 완료
echo.

echo [4/7] 필수 파일 추가...
git add dashboard_streamlit.py
git add requirements.txt
git add README.md
git add .gitignore
echo ✅ 완료
echo.

echo [5/7] 커밋 생성...
git commit -m "Initial commit: DX Outlet Dashboard"
echo ✅ 완료
echo.

echo [6/7] 브랜치 설정...
git branch -M main
echo ✅ 완료
echo.

echo [7/7] GitHub에 푸시...
echo.
echo ⚠️ GitHub 로그인이 필요할 수 있습니다.
echo    창이 열리면 로그인해주세요.
echo.
git push -u origin main
echo.

echo ================================================================================
echo 🎉 업로드 완료!
echo ================================================================================
echo.
echo 브라우저에서 확인: https://github.com/leeh1149/OUTLETDASHBOARD
echo.
echo 다음 단계:
echo 1. https://streamlit.io/cloud 접속
echo 2. Continue with GitHub
echo 3. New app 클릭
echo 4. Repository: leeh1149/OUTLETDASHBOARD 선택
echo 5. Main file: dashboard_streamlit.py
echo 6. Deploy! 클릭
echo.
echo ================================================================================
pause

