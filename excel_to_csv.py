import pandas as pd
import os

def excel_to_csv(excel_file, csv_file=None):
    """
    Excel 파일을 CSV 파일로 변환하는 함수
    """
    try:
        # Excel 파일 읽기
        print(f"Excel 파일 읽는 중: {excel_file}")
        df = pd.read_excel(excel_file)
        
        # CSV 파일명이 지정되지 않으면 자동 생성
        if csv_file is None:
            csv_file = excel_file.replace('.xlsx', '.csv').replace('.xls', '.csv')
        
        # CSV 파일로 저장
        print(f"CSV 파일로 저장 중: {csv_file}")
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"변환 완료!")
        print(f"원본 파일: {excel_file}")
        print(f"변환된 파일: {csv_file}")
        print(f"데이터 행 수: {len(df)}")
        print(f"데이터 열 수: {len(df.columns)}")
        
        # 데이터 미리보기
        print("\n데이터 미리보기 (처음 5행):")
        print(df.head())
        
        return csv_file
        
    except Exception as e:
        print(f"에러 발생: {e}")
        return None

if __name__ == "__main__":
    # DX OUTLET MS DB.xlsx 파일을 CSV로 변환
    excel_file = "DX OUTLET MS DB.xlsx"
    
    if os.path.exists(excel_file):
        csv_file = excel_to_csv(excel_file)
        if csv_file:
            print(f"\n✅ 변환 성공: {csv_file}")
        else:
            print("❌ 변환 실패")
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {excel_file}")

