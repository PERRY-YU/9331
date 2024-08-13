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
SELECT 
    ns.NewsID, 
    CONCAT(DATE_FORMAT(nn.DeclareDate, '%Y-%m-%d'), ' ', TIME_FORMAT(nn.FullDeclareDate, '%H:%i:%s')) AS FullDeclareDateTime,
    nn.Autor, 
    nn.NewsSource, 
    nn.NewsContent, 
    ns.ShortName
FROM 
    news_security ns
JOIN 
    news_newsinfo nn ON ns.NewsID = nn.NewsID
WHERE 
    ns.SecurityType = 'A股';

'''

cursor.execute(query)

result = cursor.fetchall()

columns = ['NewsID', 'FullDeclareDate', 'Autor', 'NewsSource', 'NewsContent', 'Industry']

df = pd.DataFrame(result, columns=columns)

output_path = 'a_stock_news_details.xlsx'
df.to_excel(output_path, index=False)

cursor.close()
conn.close()

print(f"Query results saved to {output_path}")
