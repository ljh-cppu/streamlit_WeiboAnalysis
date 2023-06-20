import time

import jieba
import jieba.posseg as jp
import numpy as np
import pandas as pd
import pyLDAvis.gensim_models
import streamlit as st
import streamlit.components.v1 as components
from gensim.corpora.dictionary import Dictionary  # 读取需要处理的文本
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamodel import LdaModel
import pyecharts.options as opts
from pyecharts.charts import Line

st.set_page_config(page_title="LDA", page_icon="🗯", layout="wide")

st.markdown("# 🗯LDA主题分析🗯")

data = pd.DataFrame()
uploaded_file = st.file_uploader("Choose a CSV file", accept_multiple_files=False)
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data

test_df = pd.read_csv("./static/lda.csv").to_csv(index=False).encode("utf-8")
st.download_button(
    label="下载示例文件",
    data=test_df,
    file_name="test.csv",
    mime="text/csv",
)


top_num = st.slider("选择主题数", 0, 10, 3)
if st.button("🚀生成"):
    if data.empty:
        st.warning("⚠请先上传文件")
    else:
        data = data[["评论内容"]].dropna()
        texts = list(data["评论内容"].values)
        # 词性标注条件
        flags = ("n", "nr", "ns", "nt", "eng", "v", "d", "vn", "vd")
        # 停用词表
        stopwords = open("./static/stopwords.txt", "r", encoding="utf-8").read()
        # 分词
        words_ls = []
        for text in texts:  # 采用jieba进行分词
            words = [word.word for word in jp.cut(text) if word.flag in flags and word.word not in stopwords]
            words_ls.append(words)  # 构造词典
        dictionary = Dictionary(words_ls)
        # 基于词典，使【词】→【稀疏向量】，并将向量放入列表，形成【稀疏向量集】
        corpus = [dictionary.doc2bow(words) for words in words_ls]
        tab1, tab2 = st.tabs(["🌲主题展示", "📒困惑度曲线"])
        with tab1:
            # lda模型，num_topics设置主题的个数
            lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=top_num, random_state=100, iterations=50)
            # U_Mass Coherence
            ldaCM = CoherenceModel(model=lda, corpus=corpus, dictionary=dictionary, coherence="u_mass")
            plot = pyLDAvis.gensim_models.prepare(lda, corpus, dictionary)
            # 保存到本地html
            pyLDAvis.save_html(plot, "./static/pyLDAvis.html")

            with open("./static/ldavis.v3.0.0.js", 'r', encoding='gbk') as f:
                js_code1 = f.read()
            with open("./static/d3.v5.js", encoding='utf-8') as f:
                js_code2 = f.read()
            with open("./static/ldavis.v1.0.0.css", 'r', encoding='gbk') as f:
                css_code1 = f.read()
            with open("./static/pyLDAvis.html", 'r', encoding='utf-8') as f:
                ht = f.read()
            ht = ht.replace(
                '<link rel="stylesheet" type="text/css" '
                'href="https://cdn.jsdelivr.net/gh/bmabey/pyLDAvis@3.4.0/pyLDAvis/js/ldavis.v1.0.0.css">',
                '')
            html = f'<style>{css_code1}</style><script type="text/javascript">{js_code1}</script><script type="text' \
                   f'/javascript">{js_code2}</script>{ht} '

            components.html(html, width=1210, height=840)
            with open("./static/pyLDAvis.html", 'w', encoding='utf-8') as f:
                f.write(html)
            st.download_button(
                label="下载文件",
                data=open("./static/pyLDAvis.html", encoding='utf-8').read(),
                file_name='./static/pyLDAvis.html',
                mime='text/csv',
            )
        with tab2:

            def perplexity(num_topics):
                ldamodel = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, iterations=50,
                                    random_state=100)  # passes为迭代次数，次数越多越精准
                return ldamodel.log_perplexity(corpus)


            x = range(1, 10)  # 主题范围数量
            y = [perplexity(i) for i in x]


            c = (
                Line()
                .add_xaxis(x)
                .add_yaxis("Perplexity", y)
                .set_global_opts(legend_opts=opts.LegendOpts(pos_left="left"),yaxis_opts=opts.AxisOpts(is_scale=True))
                .set_series_opts(opts.LabelOpts(is_show=False))
            )
            html2 = c.render_embed()
            components.html(html2, width=1210, height=840)