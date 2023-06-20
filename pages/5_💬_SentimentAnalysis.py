import bayes
import jieba
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyecharts import options as opts
from pyecharts.charts import Grid, Liquid
from pyecharts.commons.utils import JsCode

st.set_page_config(page_title="Sentiment", page_icon="💬")

st.markdown("# 🥰情感分析😑")

model = bayes.Bayes()
data = pd.DataFrame()


def classify_one(words):
    """

    :type words: list
    """
    sentiment = model.classify(words)

    if not sentiment[1] > 0.6 and sentiment[1] >= 0.4:
        st.info(f'neutral  {sentiment[1]:.2f}')
    else:
        st.info(f'{sentiment[0]}  {sentiment[1]:.2f}')


def classify_mult(word):
    word = jieba.lcut(word)
    sentiment = model.classify(word)
    if not sentiment[1] > 0.6 and sentiment[1] >= 0.4:
        return 'neutral'
    else:
        return sentiment[0]


select = st.radio(
    "",
    ('单条检测', '批量检测'), index=0, horizontal=True, label_visibility="collapsed")

if select == '单条检测':
    st.text_input('请输入单条文本 (例如: 希望不要继续造谣！)', value='希望不要继续造谣！', key="text_one", help="""[基于朴素贝叶斯的情感分类方法](
    https://zhuanlan.zhihu.com/p/32834778)""")
    words = jieba.lcut(st.session_state.text_one)
    classify_one(words)

elif select == '批量检测':
    uploaded_file = st.file_uploader("请上传包含'评论内容'列的CSV文件：")
    test_df = pd.read_csv('./static/微博评论.csv').to_csv(index=False).encode("utf-8")
    st.download_button(
        label="下载示例文件",
        data=test_df,
        file_name='test_upload.csv',
        mime='text/csv',
    )
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        data
    if st.button('🚀检测'):
        if data.empty:
            st.warning("⚠请先上传文件")
        else:
            col1, col2 = st.tabs(['各部分占比', '数据展示'])
            with col2:
                data = data[['评论内容']].dropna()
                data['sentiment'] = data['评论内容'].apply(classify_mult)
                data
                file = data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="下载文件",
                    data=file,
                    file_name='sentiment.csv',
                    mime='text/csv',
                )
            with col1:
                #获取各情感的占比
                sentiment_data = data['sentiment'].value_counts() / data.shape[0]
                #对情感词进行排序，方便后面使用
                sentiment_data = sorted(list(sentiment_data.items()), key=lambda x: x[0])
                st.write('各情感占比', unsafe_allow_html=True)
                #echart绘制负向情感水球图
                l1 = Liquid().add(
                    sentiment_data[0][0],
                    [sentiment_data[0][1]],
                    color=['#FF0000'],
                    center=["15%", "50%"],
                )
                #echart绘制正向情感水球图
                l2 = Liquid().add(
                    sentiment_data[2][0],
                    [sentiment_data[2][1]],
                    color=['#1FFF06'],
                    center=["45%", "50%"],
                )
                #echart绘制中向情感水球图
                l3 = (
                    Liquid()
                        .add(sentiment_data[1][0], [sentiment_data[1][1]], center=["75%", "50%"])
                )

                grid = Grid().add(l1, grid_opts=opts.GridOpts()).add(l2, grid_opts=opts.GridOpts()).add(l3,
                                                                                                        grid_opts=opts.GridOpts())
                html = grid.render_embed()
                components.html(html, width=820, height=500)
