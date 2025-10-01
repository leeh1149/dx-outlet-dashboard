# ⚡ 빠른 시작 가이드

## 상황별 추천 방법

### 1️⃣ 친구/동료에게 잠깐 보여주고 싶을 때 (5분)
**→ ngrok 사용**
```bash
# pyngrok 설치
pip install pyngrok

# 실행
python run_with_ngrok.py
```
나오는 URL을 복사해서 공유하세요!

---

### 2️⃣ 같은 사무실/집 WiFi에서 다른 PC/폰으로 보고 싶을 때 (1분)
**→ 로컬 네트워크 공유**
```bash
# 방법 1: 배치 파일 실행
run_local_network.bat

# 방법 2: 직접 명령어
streamlit run dashboard_streamlit.py --server.address=0.0.0.0
```

내 IP 주소 확인:
```bash
ipconfig
# IPv4 주소 찾기 (예: 192.168.0.10)
```

다른 기기에서 접속:
```
http://192.168.0.10:8501
```

---

### 3️⃣ 인터넷 어디서나 접속 가능하게 하고 싶을 때 (20분)
**→ Streamlit Cloud 배포 (무료, 영구)**

`DEPLOY_GUIDE.md` 파일을 참고하세요!

**장점:**
- ✅ 완전 무료
- ✅ 자동 HTTPS
- ✅ URL이 영구적
- ✅ GitHub에 코드 push하면 자동 업데이트
- ✅ 별도 서버 관리 불필요

**URL 예시:**
```
https://dx-outlet-dashboard.streamlit.app
```

---

## 각 방법 비교

| 방법 | 속도 | 비용 | 영구성 | 난이도 | 추천 용도 |
|------|------|------|--------|--------|----------|
| **ngrok** | ⚡ 5분 | 무료 | ❌ 임시 | ⭐ 쉬움 | 빠른 공유/테스트 |
| **로컬 네트워크** | ⚡ 1분 | 무료 | ⏰ 실행중만 | ⭐ 매우 쉬움 | 사무실 내 공유 |
| **Streamlit Cloud** | ⏱️ 20분 | 무료 | ✅ 영구 | ⭐⭐ 보통 | 정식 배포 |

---

## 문제 해결

### "streamlit: command not found"
```bash
pip install streamlit
```

### 방화벽 차단
Windows 방화벽에서 Python 허용 필요

### 포트 이미 사용중
```bash
# 다른 포트 사용
streamlit run dashboard_streamlit.py --server.port=8502
```

---

## 다음 단계

1. ✅ 먼저 로컬에서 테스트: `streamlit run dashboard_streamlit.py`
2. 🚀 필요에 따라 위 방법 중 선택
3. 🎉 완료!

**질문이나 문제가 있으면 DEPLOY_GUIDE.md를 참고하세요!**

