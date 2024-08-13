import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='xuyaya',
    database='0809'
)


cursor = conn.cursor()

query = '''
SELECT COUNT(*) AS PostCount
FROM news_security ns
JOIN news_newsinfo nn ON ns.NewsID = nn.NewsID
WHERE ns.SecurityType = 'A股' AND nn.NewsSource LIKE '%东方财富网%';
'''


cursor.execute(query)

result = cursor.fetchone()

df = pd.DataFrame([result], columns=['PostCount'])

output_path = 'a_stock_eastmoney_post_count.xlsx'
df.to_excel(output_path, index=False)

cursor.close()
conn.close()

print(f"Post count saved to {output_path}")
