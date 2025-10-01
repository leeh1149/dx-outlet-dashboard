# ngrok을 사용한 임시 배포

## 설치
```bash
# ngrok 다운로드: https://ngrok.com/download
# 또는 pip으로 설치
pip install pyngrok
```

## 사용 방법

### 방법 1: 직접 실행
```bash
# 터미널 1: Streamlit 앱 실행
streamlit run dashboard_streamlit.py

# 터미널 2: ngrok 터널 시작
ngrok http 8501
```

### 방법 2: Python 스크립트 사용
아래 스크립트를 실행하세요:
```python
# run_with_ngrok.py
from pyngrok import ngrok
import subprocess
import sys

# ngrok 터널 시작
public_url = ngrok.connect(8501)
print(f'Public URL: {public_url}')

# Streamlit 앱 실행
subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'dashboard_streamlit.py'])
```

## 주의사항
- 무료 버전은 URL이 매번 변경됩니다
- 세션이 종료되면 URL도 사라집니다
- 테스트 용도로만 사용하세요


