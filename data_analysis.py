import pandas as pd
import numpy as np

# CSV 파일 읽기
df = pd.read_csv('DX OUTLET MS DB.csv')

print("=== 데이터 기본 정보 ===")
print(f"총 행 수: {len(df)}")
print(f"총 열 수: {len(df.columns)}")
print("\n컬럼명:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\n=== 유통사별 데이터 ===")
print("유통사 목록:")
print(df['유통사'].value_counts())

print("\n=== 매장명별 데이터 ===")
print("매장명 목록:")
print(df['매장명'].value_counts())

print("\n=== 형태별 데이터 ===")
print("형태 목록:")
print(df['형태'].value_counts())

print("\n=== 브랜드별 데이터 ===")
print("브랜드 목록:")
print(df['브랜드'].value_counts())

print("\n=== 샘플 데이터 ===")
print(df.head())

print("\n=== 데이터 타입 ===")
print(df.dtypes)

