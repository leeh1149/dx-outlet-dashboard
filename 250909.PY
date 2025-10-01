import snowflake.connector
import pandas as pd

# Snowflake 접속
conn = snowflake.connector.connect(
    user="test03",
    password="Training2025!@",
    account="XUCVRNT-OP22534",
    warehouse="COMPUTE_WH",
    database="TRAINING_DB",
    schema="PUBLIC",
    role="READONLY_ROLE")
    
cur = conn.cursor()  # ✅ SQL 실행 도구(Cursor) 생성

# SQL 실행
cur.execute("SELECT PRODUCT, MONTH, SALES FROM SALES_DATA LIMIT 20")
rows = cur.fetchall()

# 컬럼 이름 가져오기
cols = []
for c in cur.description:
    cols.append(c[0])

# ⚡ 축약 버전 (참고)
# cols = [c[0] for c in cur.description]
# cols = ["PRODUCT", "MONTH", "SALES"]

# DataFrame 변환
df = pd.DataFrame(rows, columns=cols)
# df = pd.DataFrame(rows)
print(df)

# 제품별 매출 합계
print(df.groupby("PRODUCT")["SALES"].sum())

# 월별·제품별 피벗테이블
pivot = pd.pivot_table(
    df,
    values="SALES",    # 집계할 값
    index="MONTH",     # 행 기준
    columns="PRODUCT", # 열 기준
    aggfunc="sum",     # 합계
    fill_value=0       # 값 없으면 0으로 채우기
)
print(pivot)

cur.close()
conn.close()