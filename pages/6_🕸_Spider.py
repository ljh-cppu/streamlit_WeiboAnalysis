import streamlit as st
import pandas as pd
import crawl
import os
from PIL import Image

st.set_page_config(page_title="Spider", page_icon="🕸")

st.markdown("# 🕸爬取微博数据🕸")

st.markdown(
    """
    &emsp;&emsp;还在发愁没有数据？\n
    &emsp;&emsp;还在为2万条数据苦恼？\n
    &emsp;&emsp;不会爬虫？\n
    &emsp;&emsp;点击下方按钮👇

"""
)

cookies = st.text_input('输入cookies',
                        value='SCF=As_KFkwQbxtg6e_oOzNxIChehTpoWqgeftNNXeNmlLmP_7cd6-oy-jskefv2mMs43r6ySwBQLgQWO3sp-LrS6vs.; SUB=_2A25JiAExDeRhGeFK71IY9izJyjWIHXVrcq95rDV6PUNbktAGLRPYkW1NQ3TJAZko2xVn0yeBpcvbu0SuzDLx7V1u; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhszfTOq4dBy9DLdT2FXw6n5JpX5KMhUgL.FoMXSh54SozfeK.2dJLoI7UjIJn_eh27; ALF=1689517665; _T_WM=68123311795; XSRF-TOKEN=ce1974; WEIBOCN_FROM=1110006030; MLOGIN=1; mweibo_short_token=698f7b8213; M_WEIBOCN_PARAMS=oid%3D4914285564137486%26lfid%3D4914285564137486%26luicode%3D20000174%26uicode%3D20000174')
weibo_id_list = st.text_input('输入weibo_id（不同id用空格分开 4444 5555 6666）', value='4909917352494814').split()
st.markdown("""如何获取cookies和weibo_id? 
            \n https://m.weibo.cn/detail/4909917352494814""")
col1, col2 = st.columns(2)

with col1:
    st.markdown("weibo_id")
    st.image(Image.open('./static/t1.png'))

with col2:
    st.markdown("cookies")
    st.image(Image.open('./static/t2.png'))

if st.button('🚀开爬'):
    comment_file = './static/微博评论.csv'
    # 如果文件存在,先删除
    if os.path.exists(comment_file):
        print('csv文件已经存在,先删除:', comment_file)
        os.remove(comment_file)
    # 爬取评论
    crawl.get_comments(v_weibo_ids=weibo_id_list, v_comment_file=comment_file, cookies=cookies)
    st.info('爬取完成！', icon="ℹ️")
    st.balloons()
    # 下载数据
    data_down = pd.read_csv('./static/微博评论.csv').to_csv(index=False).encode("utf-8")
    st.download_button(
        label="下载文件",
        data=data_down,
        file_name='微博评论.csv',
        mime='text/csv',
    )
