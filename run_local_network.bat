@echo off
echo ========================================
echo DX OUTLET Dashboard - Local Network
echo ========================================
echo.
echo 같은 WiFi에 연결된 다른 기기에서 접속할 수 있습니다.
echo.

REM 가상환경 활성화 (있는 경우)
if exist "myvenv\Scripts\activate.bat" (
    call myvenv\Scripts\activate.bat
)

REM Streamlit 실행 (모든 네트워크 인터페이스에서 접속 가능)
streamlit run dashboard_streamlit.py --server.address=0.0.0.0 --server.port=8501

pause


