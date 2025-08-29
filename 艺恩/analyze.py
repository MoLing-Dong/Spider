# -*- coding: utf-8 -*-

import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Bar, Pie
from wordcloud import WordCloud

# 读取数据
df = pd.read_csv('list.csv')

# 根据ProvinceName分类城市
grouped = df.groupby('CityName')

# 根据获取的数据绘制图表
# 只要前20个城市
top20 = df['CityName'].value_counts().head(20)

# 创建Bar对象
bar = Bar(
    init_opts=opts.InitOpts(
        width='1000px',
        height='600px',
    )
)

# 添加x轴数据
bar.add_xaxis(top20.index.tolist())

# 添加y轴数据
bar.add_yaxis('场次', top20.values.tolist())

# 设置标题
bar.set_global_opts(
    title_opts=opts.TitleOpts(
        title='各城市电影场次对比',
        subtitle='数据来源：艺恩',
    ),
    xaxis_opts=opts.AxisOpts(
        name='城市',
        #     显示所有x轴标签
        axislabel_opts=opts.LabelOpts(
            interval=0,
        )
    ),
    yaxis_opts=opts.AxisOpts(
        name='场次',
    )
)

# 保存图表
bar.render('city_bar.html')
top50 = df['CityName'].value_counts().head(50)

# 生成城市场次占所有场次比重的词云，只需要前20个城市
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    font_path='msyh.ttc'
).generate_from_frequencies(top50)

# 保存词云
wordcloud.to_file('city_wordcloud.png')

# 饼图
pie = Pie()

# 计算前20个城市的总场次
top20_counts = df['ProvinceName'].value_counts().head(20)

# 将前20个城市的数据
data_pair = [list(z) for z in zip(top20_counts.index.tolist(), top20_counts.values.tolist())]

# 添加数据到饼图
pie.add(
    series_name='城市',
    data_pair=data_pair,
)
# 显示百分比
pie.set_series_opts(
    label_opts=opts.LabelOpts(
        formatter='{b}: {d}%'
    )
)
# 设置标题
pie.set_global_opts(
    title_opts=opts.TitleOpts(
        title='各城市电影场次占比',
        subtitle='数据来源：艺恩',
    ),
    legend_opts=opts.LegendOpts(
        orient='vertical',
        pos_top='15%',
        pos_left='2%',
    )
)

# 渲染图表
pie.render('city_pie.html')

# 显示所有的AvgBoxOffice的频率分布图.
# 对AvgBoxOffice进行频率统计，取整数部分的频率
# 对所有的AvgBoxOffice进行取整操作
df['AvgBoxOffice'] = df['AvgBoxOffice'].astype(int)
show_freq = df['AvgBoxOffice'].value_counts().sort_index()

bar = Bar(
    init_opts=opts.InitOpts(
        width='1000px',
        height='600px',
    )
)
# 计算AvgBoxOffice的频率
# 添加x轴数据
bar.add_xaxis(show_freq.index.tolist())
# 添加y轴数据
bar.add_yaxis('频率', show_freq.values.tolist())
# 设置标题
bar.set_global_opts(
    title_opts=opts.TitleOpts(
        title='AvgBoxOffice频率分布图',
        subtitle='数据来源：艺恩',
    ),
    xaxis_opts=opts.AxisOpts(
        name='AvgBoxOffice',
    ),
    yaxis_opts=opts.AxisOpts(
        name='频率',
    )
)
# 保存图表
bar.render('show_bar.html')
