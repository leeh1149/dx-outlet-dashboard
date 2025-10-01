#!/usr/bin/env python3
"""
GitHub 자동 업데이트 스크립트
dashboard_streamlit.py 파일을 GitHub 저장소에 자동으로 업데이트합니다.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(command, description):
    """명령어를 실행하고 결과를 반환합니다."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ {description} 완료")
            return True, result.stdout
        else:
            print(f"❌ {description} 실패: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} 오류: {str(e)}")
        return False, str(e)

def check_git_installed():
    """Git이 설치되어 있는지 확인합니다."""
    success, output = run_command("git --version", "Git 설치 확인")
    return success

def initialize_git_repo():
    """Git 저장소를 초기화합니다."""
    # Git 저장소 초기화
    success, _ = run_command("git init", "Git 저장소 초기화")
    if not success:
        return False
    
    # 원격 저장소 추가
    success, _ = run_command("git remote add origin https://github.com/leeh1149/OUTLETDASHBOARD.git", "원격 저장소 추가")
    if not success:
        # 이미 존재하는 경우 무시
        run_command("git remote set-url origin https://github.com/leeh1149/OUTLETDASHBOARD.git", "원격 저장소 URL 설정")
    
    # 메인 브랜치 설정
    success, _ = run_command("git branch -M main", "메인 브랜치 설정")
    return success

def update_github():
    """GitHub 저장소를 업데이트합니다."""
    print("=" * 50)
    print("🚀 GitHub 자동 업데이트 시작")
    print("=" * 50)
    
    # 1. Git 설치 확인
    if not check_git_installed():
        print("❌ Git이 설치되어 있지 않습니다.")
        print("Git을 설치해주세요: https://git-scm.com/download/win")
        return False
    
    # 2. 현재 디렉토리 확인
    current_dir = Path.cwd()
    print(f"📁 현재 디렉토리: {current_dir}")
    
    # 3. dashboard_streamlit.py 파일 존재 확인
    dashboard_file = current_dir / "dashboard_streamlit.py"
    if not dashboard_file.exists():
        print("❌ dashboard_streamlit.py 파일을 찾을 수 없습니다.")
        return False
    
    print(f"✅ dashboard_streamlit.py 파일 확인: {dashboard_file}")
    
    # 4. Git 저장소 초기화 (필요한 경우)
    git_dir = current_dir / ".git"
    if not git_dir.exists():
        print("📦 Git 저장소가 없습니다. 초기화합니다...")
        if not initialize_git_repo():
            print("❌ Git 저장소 초기화 실패")
            return False
    
    # 5. 변경사항 추가
    success, output = run_command("git add .", "변경사항 추가")
    if not success:
        return False
    
    # 6. 변경사항 확인
    success, output = run_command("git status", "변경사항 확인")
    if success:
        print("📋 변경사항:")
        print(output)
    
    # 7. 커밋
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Update dashboard_streamlit.py - {timestamp}"
    success, _ = run_command(f'git commit -m "{commit_message}"', "변경사항 커밋")
    if not success:
        print("⚠️ 커밋할 변경사항이 없거나 이미 커밋되었습니다.")
    
    # 8. GitHub에 푸시
    success, output = run_command("git push origin main", "GitHub에 푸시")
    if success:
        print("=" * 50)
        print("🎉 업데이트 완료!")
        print("=" * 50)
        print("✅ GitHub 저장소가 성공적으로 업데이트되었습니다.")
        print("🔄 Streamlit Cloud에서 자동으로 재배포됩니다.")
        print("🌐 대시보드 URL: https://jb9gcmjivepixpauprtsfy.streamlit.app/")
        print("⏱️ 재배포 시간: 약 2-3분 소요")
        return True
    else:
        print("=" * 50)
        print("❌ 업데이트 실패")
        print("=" * 50)
        print("GitHub 인증이 필요할 수 있습니다.")
        print("해결 방법:")
        print("1. GitHub Personal Access Token 설정")
        print("2. Git Credential Manager 사용")
        print("3. 수동으로 GitHub에서 파일 업데이트")
        return False

def main():
    """메인 함수"""
    try:
        success = update_github()
        if success:
            print("\n🎯 다음 단계:")
            print("1. Streamlit Cloud 재배포 대기 (2-3분)")
            print("2. 대시보드에서 변경사항 확인")
            print("3. 모든 기능이 정상 작동하는지 테스트")
        else:
            print("\n🔧 문제 해결:")
            print("1. Git 인증 설정 확인")
            print("2. 네트워크 연결 확인")
            print("3. 수동 업데이트 고려")
        
        input("\nEnter 키를 눌러 종료...")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {str(e)}")

if __name__ == "__main__":
    main()
