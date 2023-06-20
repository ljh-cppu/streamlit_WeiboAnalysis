import streamlit as st
import pandas as pd



#设置页面标头的内容
st.set_page_config(
    page_title="微博舆情分析系统",
    page_icon="🚔",
    initial_sidebar_state="collapsed",
)


#主页一级标题
st.write("# 欢迎使用微博舆情分析系统 👋")
#侧边栏设置内容
st.sidebar.success("请点击以上DEMO☝☝")
#主页设置其他内容
st.markdown(
    """
    &emsp;&emsp;舆情分析系统是一种基于大数据和人工智能技术的应用系统，主要用于对社会舆情进行监测、分析和预测。
    该系统可以从互联网、社交媒体等多个数据源中采集海量数据，使用自然语言处理、机器学习等技术对数据进行处理和分析，从而提取出舆情事件的关键信息和趋势，为政府、企业等决策者提供决策支持和预警服务。
    ### 我们可以做什么🤗🤗
    - 统计分析 📈
    - 词云图 ☁
    - 主题分析 🗨
    - 情感分析 💬
    - 文本摘要 🗟
    - 数据爬取 🕸
    - 未完待续...
"""
)

