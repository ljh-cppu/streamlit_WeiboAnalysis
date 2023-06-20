import pandas as pd
import streamlit as st
import time
import numpy as np
import io
import jieba
from stylecloud import gen_stylecloud
from PIL import Image

st.set_page_config(page_title="WordCloud", page_icon="☁", layout="wide")

st.markdown("# ☁词云图在线生成☁")

data = pd.DataFrame()
uploaded_file = st.file_uploader("Choose a CSV file", accept_multiple_files=False)
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data
test_df = pd.read_csv('./static/test.csv').to_csv(index=False).encode("utf-8")
st.download_button(
    label="下载示例文件",
    data=test_df,
    file_name='test_bot.csv',
    mime='text/csv',
)


# 分词数据

def textdata():
    text_df = data[['评论内容']].dropna()
    text = ''
    words = {}
    stopwords = open("./static/stopwords.txt", "r", encoding='utf-8').read()
    for i in text_df.values.tolist():
        li = [x for x in jieba.lcut(i[0]) if len(x) >= 2 and x not in stopwords]
        for i in li:
            words[i] = words.get(i, 0) + 1
    return words


if st.button('🚀生成'):
    if data.empty:
        st.warning("⚠请先上传文件")
    else:
        col1, space, col2 = st.columns([0.5, 0.3, 0.2])
        with col1:
            words = textdata()
            #生成词云图
            gen_stylecloud(text=words,  # 可以用字典
                           size=512,  # stylecloud 的大小（长度和宽度）
                           icon_name="fas fa-cloud",
                           background_color='white',
                           font_path='./static/潮字社时光简.ttf',
                           max_font_size=500,  # stylecloud 中的最大字号
                           max_words=1000,  # stylecloud 可包含的最大单词数
                           output_name='./static/词云.png',
                           palette='tableau.BlueRed_6',
                           stopwords=False
                           )
            #展示图片
            image = Image.open('./static/词云.png')
            #页面布局图片
            st.image(image, caption='舆情词云图')
        with col2:
            x = list(words.items())
            words = sorted(x, key=lambda x: x[1], reverse=True)
            data = pd.DataFrame(words, columns=['word', 'num'])
            data
            file = data.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="下载文件",
                data=file,
                file_name='word_fre.csv',
                mime='text/csv',
            )
