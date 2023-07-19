# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 19:30:59 2023

@author: ryan

网页版本的IAT数据处理工具，挂载在streamlit上对外使用

使用逻辑：
1. 下载模板
2. 上传数据表
3. 校验数据表
4. 展示数据表概述
5. 输入分析条件和参数
6. 核心计算
7. 可视化展示分析结果
8. 下载结果表格

"""

import streamlit as st
import pandas as pd
import os

# 数据模板下载
@st.cache
def convert_df(dataframe):
    return dataframe.to_csv().encode('utf-8')

local_path = os.getcwd()
data_model = convert_df(pd.read_csv(os.path.join(local_path, 'data_sample.csv')))

# 页面绘制
st.title('IAT数据处理工具')
st.info('从这里开始一些测试')
st.write(' ')

st.header('Step 1. 下载数据模板')
st.info('点击下载数据模板，并按照模板填写数据表')
st.download_button('下载数据模板',
                   data=data_model,
                   file_name='data_sample.csv',
                   mime='text/csv')

st.write(' ')
st.header('Step 2. 上传IAT实验数据')
st.info('将填写完的数据文件上传')
data_file = st.file_uploader('选择数据文件')
if data_file is not None:
    user_data = pd.read_csv(data_file)
    st.dataframe(user_data)

# st.balloons()
