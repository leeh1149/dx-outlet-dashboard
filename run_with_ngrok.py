"""
ngrok을 사용하여 Streamlit 앱을 외부에 공개하는 스크립트
"""
from pyngrok import ngrok
import subprocess
import sys

def main():
    # ngrok 터널 시작 (포트 8501은 Streamlit 기본 포트)
    try:
        public_url = ngrok.connect(8501)
        print("=" * 50)
        print(f"🌐 Public URL: {public_url}")
        print("=" * 50)
        print("위 URL을 복사하여 누구와도 공유할 수 있습니다!")
        print("종료하려면 Ctrl+C를 누르세요.")
        print("=" * 50)
        
        # Streamlit 앱 실행
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'dashboard_streamlit.py'])
    except Exception as e:
        print(f"오류 발생: {e}")
        print("pyngrok을 먼저 설치해주세요: pip install pyngrok")

if __name__ == "__main__":
    main()


