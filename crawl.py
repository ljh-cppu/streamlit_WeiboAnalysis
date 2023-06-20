import os
import requests
import pandas  as pd
import datetime
from time import sleep
import random
import re
import streamlit as st


def trans_time(v_str):
    '''转换GMT时间为标准格式'''
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'  # 星期、月、日、时间、+0800、年
    timeArray = datetime.datetime.strptime(v_str, GMT_FORMAT)
    ret_time = timeArray.strftime("%Y-%m-%d %H:%M:%S")  # 改为年-月-日 时：分：秒
    return ret_time


def tran_gender(gender_tag):
    '''转换性别'''
    if gender_tag == 'm':
        return '男'
    elif gender_tag == 'f':
        return '女'
    else:
        return '未知'


def get_comments(v_weibo_ids, v_comment_file, v_max_page=None,cookies=None):
    for weibo_id in v_weibo_ids:
        # 初始化max_id
        max_id = '0'
        max_id_type = 0
        # 爬取前n页，可任意修改
        page = 1
        while True:
            #         for page in range(1,v_max_page + 1):
            wait_seconds = random.uniform(0, 3)  # 等待时长秒
            print('开始等待{}秒'.format(wait_seconds))
            in1 = st.info('开始等待{}秒'.format(wait_seconds), icon="ℹ️")
            sleep(wait_seconds)
            print('开始爬取第{}页'.format(page))
            in1 = st.info('开始爬取第{}页'.format(page), icon="ℹ️")
            if page == 1:  # 第一页没有max_id参数
                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type={}'.format(weibo_id, weibo_id,
                                                                                               max_id_type)
            else:  # 非第一页，需要max_id参数
                if max_id == 0:  # 如果发现max_id为0,说明没有下一页了，break结束循环
                    print("max_id is 0,break now")
                    break
                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type={}'.format(weibo_id,
                                                                                                         weibo_id,
                                                                                                         max_id,
                                                                                                         max_id_type)  # 加入max_id
                print(url)
                #             ua = UserAgent(path=location)#反爬

            headers = {
                "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42',
                # 如果cookie失效，会返回-100响应码
                "x-requested-with": "XMLHttpRequest",
                "cookie": cookies,
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9",
                "referer": "https://weibo.com/detail/{}".format(weibo_id),
                "mweibo-pwa": '1'
            }
            r = requests.get(url, headers=headers)  # proxies=proxies,
            print(r.status_code)  # 查看响应码
            #             print(r.json()) #查看响应内容
            try:
                max_id = r.json()['data']['max_id']
                max_id_type = r.json()['data']['max_id_type']
                print(max_id, max_id_type)
                datas = r.json()['data']['data']
            except Exception as e:
                print('excepted:' + str(e))
                max_id = 0
                continue
            page_list = []  # 评论页码#构建一系列列表
            id_list = []  # 评论id
            text_list = []  # 评论内容
            time_list = []  # 评论时间
            like_count_list = []  # 评论点赞数
            source_list = []  # 评论IP归属地
            user_name_list = []  # 评论者姓名
            user_id_list = []  # 评论者id
            user_gender_list = []  # 评论者性别
            follow_count_list = []  # 评论者关注数
            followers_count_list = []  # 评论者粉丝数
            for data in datas:
                page_list.append(page)  # 填列表
                id_list.append(data['id'])
                dr = re.compile(r'<[^>]+>', re.S)  # 用正则表达式清洗评论数据，re.m为多行,re.s为单行一长溜
                text2 = dr.sub('', data['text'])
                text_list.append(text2)  # 评论内容
                time_list.append(trans_time(v_str=data['created_at']))  # 评论时间
                like_count_list.append(data['like_count'])  # 评论点赞数
                source_list.append(data['source'])  # 评论者IP归属地
                user_name_list.append(data['user']['screen_name'])  # 评论者姓名
                user_id_list.append(data['user']['id'])  # 评论者id
                user_gender_list.append(tran_gender(data['user']['gender']))
                follow_count_list.append(data['user']['follow_count'])
                followers_count_list.append(data['user']['followers_count'])
            df = pd.DataFrame(
                {
                    '微博id': [weibo_id] * len(time_list),
                    '评论页码': page_list,
                    '评论id': id_list,
                    '评论时间': time_list,
                    '评论者赞数': like_count_list,
                    '评论者IP归属地': source_list,
                    '评论者姓名': user_name_list,
                    '评论者id': user_id_list,
                    '评论者性别': user_gender_list,
                    '评论者关注数': follow_count_list,
                    '评论者粉丝数': followers_count_list,
                    '评论内容': text_list
                }
            )
            if os.path.exists(v_comment_file):  # 如果文件存在，不再设置表头
                header = False
            else:  # 否则，设置csv表头
                header = True
            # 保存csv文件
            df.to_csv(v_comment_file, mode='a+', index=False, header=header)  # 追加的模式，爬取的每一页都写到文件里
            print('结果保存成功:{}'.format(v_comment_file))
            page += 1
