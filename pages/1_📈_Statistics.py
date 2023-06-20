import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Map
from pyecharts.commons.utils import JsCode

data = pd.DataFrame()
st.set_page_config(page_title="Statistic", page_icon="📈", layout="wide")

st.markdown("# 📈统计分析📈")

# 上传数据
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


# 时序数据

def plotdata():
    data['评论时间'] = pd.to_datetime(data['评论时间'])
    data.index = pd.DatetimeIndex(data['评论时间'].dt.strftime("%Y-%m-%d %H:%M:%S"))
    return pd.DataFrame(data.resample('H').size(), columns=['num'])


# 地区数据

def mapdata():
    data['评论者IP归属地'].replace('来自(.*?)', '', regex=True, inplace=True)
    data3 = data.groupby('评论者IP归属地', as_index=False).count()
    data3.sort_values(by='微博id', ascending=False, inplace=True)
    min_data = min(data3['微博id'])
    max_data = max(data3['微博id'])
    data3 = data3[['评论者IP归属地', '微博id']].values.tolist()
    # 寻找中国省份
    provinces = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北',
                 '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '中国澳门', '中国台湾',
                 '中国香港']
    data3_c = [[i[0] + '省', i[1]] for i in data3 if i[0] in provinces]
    fix_pro = ['北京省', '天津省', '内蒙古省', '上海省', '广西省', '重庆省', '西藏省', '宁夏省', '新疆省', '中国澳门省', '中国台湾省', '中国香港省']
    fixed_pro = ['北京市', '天津市', '内蒙古自治区', '上海市', '广西壮族自治区', '重庆市', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区', '台湾省', '香港特别行政区',
                 '澳门特别行政区']

    def fix_province(pro):
        if pro in fix_pro:
            pro = fixed_pro[fix_pro.index(pro)]
        return pro

    data3_c = [[fix_province(i[0]), i[1]] for i in data3_c]
    # 寻找外国省份
    provinces = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北',
                 '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '中国澳门', '中国台湾',
                 '中国香港']
    data3_word = [[i[0], i[1]] for i in data3 if i[0] not in provinces]
    return data3_c, min_data, max_data, data3_word


if st.button('🚀分析'):
    if data.empty:
        st.warning("⚠请先上传文件")
    else:
        # 曲线图绘制
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        p_data = plotdata()
        # chart = st.line_chart(x=p_data.index[0],y=p_data['num'][0])
        chart = st.line_chart(p_data.iloc[0:1, :])
        #实时更新曲线图
        for i in range(1, p_data.shape[0] + 1):
            status_text.text("%i%% Complete" % (i / p_data.shape[0] * 100))
            chart.add_rows(p_data.iloc[0 + i:1 + i, :])
            progress_bar.progress(i / p_data.shape[0])
            time.sleep(0.1)

        progress_bar.empty()

        data3_c, min_data, max_data, data3_word = mapdata()
        #echart生成地图
        m1 = Map()
        m1.add("各省", data_pair=data3_c, maptype="china", is_map_symbol_show=False)  # 去除标记点
        m1.set_series_opts(label_opts=opts.LabelOpts(is_show=True))  # 去除省份名称
        m1.set_global_opts(
            title_opts=opts.TitleOpts(title="中国评论者IP归属地分布"),
            visualmap_opts=opts.VisualMapOpts(
                is_calculable=True,
                dimension=0,
                pos_left="30",
                pos_top="center",
                range_text=["High", "Low"],
                range_color=["lightskyblue", "red"],
                textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                min_=min_data,
                max_=max_data,
            ),
            toolbox_opts=opts.ToolboxOpts(is_show=True)
        )
        m1 = m1.render_embed()
        components.html(m1, width=1000, height=500)
        #echart生成柱状图
        b1 = (
            Bar()
                .add_xaxis([i[0] for i in data3_word])
                .add_yaxis("地区", [i[1] for i in data3_word], category_gap="40%")
                .set_series_opts(
                itemstyle_opts={
                    "normal": {
                        "color": JsCode(
                            """new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgba(0, 244, 255, 1)'
                    }, {
                        offset: 1,
                        color: 'rgba(0, 77, 167, 1)'
                    }], false)"""
                        ),
                        "barBorderRadius": [30, 30, 30, 30],
                        "shadowColor": "rgb(0, 160, 221)",
                    }
                }, label_opts=opts.LabelOpts(position="top")
            )
                .set_global_opts(title_opts=opts.TitleOpts(title="海外评论者IP归属地各地数量"),
                                 toolbox_opts=opts.ToolboxOpts(is_show=True),
                                 datazoom_opts=opts.DataZoomOpts(is_show=True)
                                 )

        ).render_embed()
        components.html(b1, width=1000, height=500)
        # Streamlit widgets automatically run the script from top to bottom. Since
        # this button is not connected to any other logic, it just causes a plain
        # rerun.
        st.button("Re-run")
