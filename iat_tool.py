# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 19:30:59 2023

@author: ryan

网页版本的IAT数据处理工具，挂载在streamlit上对外使用

使用逻辑：
1. 下载模板
2. 上传数据表
3. 校验数据表（列名、被试数）
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
@st.cache_data
def convert_df(dataframe):
    return dataframe.to_csv().encode('utf-8')

local_path = os.getcwd()
data_model = convert_df(pd.read_csv(os.path.join(local_path, 'data_sample.csv')))

# 数据表校验
def check_data(dataframe):
    default_col = ['Participant','Running','Stim_ACC','Stim_RT']
    missing = [col for col in default_col if col not in dataframe]
    if len(missing) == 0:
        st.info("数据表中包含所有所需的列。下方显示为上传的数据内容：")
        return True
    else:
        st.info(f"※数据表缺少以下列：{', '.join(missing)}")
        return False

# 数据表概览
def data_overview(dataframe):
    rows = dataframe.shape[0]
    parts = dataframe['Participant'].nunique()
    types = ', '.join(dataframe['Running'].unique().tolist())
    
    return (rows, parts, types)

# 

# 页面绘制
st.title('IAT数据处理工具')
st.info('从这里开始一些测试')
st.write(' ')

st.header('Step 1. 下载数据模板')
st.info('点击下载数据模板，并按照模板填写数据表')
st.text('※请勿改动数据模板的列名！！')
st.download_button('下载数据模板',
                   data=data_model,
                   file_name='data_sample.csv',
                   mime='text/csv')

st.write(' ')
st.header('Step 2. 上传IAT实验数据')
st.info('将填写完的数据文件上传')
check_res = False
data_file = st.file_uploader('选择数据文件（※仅csv格式！！）')
if data_file is not None:
    user_data = pd.read_csv(data_file)
    check_res = check_data(user_data)
    if check_res == True:
        st.dataframe(user_data)
        res = data_overview(user_data)
        st.subheader('数据表概览', divider='rainbow')
        st.text('数据行数： ' + str(res[0]))
        st.text('包含的受试者人数： ' + str(res[1]))
        st.text('包含的IAT阶段： ' + str(res[2]))
    
if check_res == True:
    st.write(' ')
    st.header('Step 3. 选择预处理参数')
    st.info('选定各项数据预处理方式及参数')
    
    st.subheader('受试者剔除标准', divider=True)
    part_speed_fast = st.checkbox('过快反应')
    if part_speed_fast:
        part_too_fast = st.number_input('过快反应阈值：', min_value=0, value=300, placeholder="请输入整数时长...")
        part_too_fast_per = st.number_input('过快反应占比：', min_value=0, max_value=100, value=10, placeholder="请输入整数百分比...")
        st.write('所有试次中，反应时低于 ', part_too_fast, 'ms 的试次超过 ', part_too_fast_per, '% 的受试者数据将被剔除')
    part_speed_slow = st.checkbox('过慢反应')
    if part_speed_slow:
        part_too_slow = st.number_input('过慢反应阈值：', min_value=0, value=10000, placeholder="请输入整数时长...")
        part_too_slow_per = st.number_input('过慢反应占比：', min_value=0, max_value=100, value=10, placeholder="请输入整数百分比...")
        st.write('所有试次中，反应时高于 ', part_too_slow, 'ms 的试次超过 ', part_too_slow_per, '% 的受试者数据将被剔除')
    part_acc = st.checkbox('错误率')
    if part_acc:
        part_acc_num = st.number_input('错误率阈值：', min_value=0, max_value=100, value=35, placeholder="请输入整数百分比...")
        st.write('所有试次中，错误率超过 ', part_acc_num, '% 的受试者数据将被剔除')
    part_sd = st.checkbox('反应时超出群体反应时标准差')
    if part_sd:
        part_sd_num = st.number_input('反应时标准差倍数：', min_value=0, max_value=10, value=3, placeholder="请输入整数倍标准差...")
        st.write('所有试次的平均反应时在所有参与者平均反应时± ', part_sd_num, ' 个标准差以外的受试者数据将被剔除')
    
    st.text('剔除结果：')
    
    
    st.subheader('试次剔除标准', divider=True)
    trial_speed_fast = st.checkbox('过快反应')
    if trial_speed_fast:
        trial_too_fast = st.number_input('过快反应阈值：', min_value=0, value=300, placeholder="请输入整数时长...")
        st.write('所有试次中，反应时低于 ', trial_too_fast, 'ms 的试次数据将被剔除')
    trial_speed_slow = st.checkbox('过慢反应')
    if trial_speed_slow:
        trial_too_slow = st.number_input('过慢反应阈值：', min_value=0, value=10000, placeholder="请输入整数时长...")
        st.write('所有试次中，反应时高于 ', trial_too_slow, 'ms 的试次数据将被剔除')
    
    st.text('剔除结果：')
    
    st.subheader('错误反应处理', divider=True)
    trial_speed_fast = st.checkbox('过快反应')
    if trial_speed_fast:
        trial_too_fast = st.number_input('过快反应阈值：', min_value=0, value=300, placeholder="请输入整数时长...")
        st.write('所有试次中，反应时低于 ', trial_too_fast, 'ms 的试次数据将被剔除')

# st.balloons()