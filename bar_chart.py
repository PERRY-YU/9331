import pandas as pd
import matplotlib.pyplot as plt


plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 读取数据
df = pd.read_csv('world_population_data.csv')

# 取前十名国家
df = df.sort_values(by='人口数量', ascending=False).head(10)

# Population Distribution Bar Chart
plt.figure(figsize=(10, 6))
plt.bar(df['国家'], df['人口数量'])
plt.xlabel('国家')
plt.ylabel('人口数量')
plt.title('全球国家人口数量分布')
plt.xticks(rotation=45)
plt.show()
