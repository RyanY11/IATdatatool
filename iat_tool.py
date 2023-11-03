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

# 总体-过快/过慢剔除
def total_speed_flt(dataframe, type, value, percent):
    '''
    输入——
    dataframe: 传入数据表
    type: 判断类型过快fast，过慢slow
    value: 过快的判定阈值
    percent: 过快反应占比的判定阈值
    返回——
    output_df: 剔除详情表
    flt_list: 剔除的受试者ID list
    '''
    output_df = pd.DataFrame(columns=['受试者编号','剔除原因','详情'])
    flt_list = []
    part_list = dataframe['Participant'].unique().tolist()
    for i in part_list:
        total = len(dataframe['Participant']==i)
        if type == 'fast':
            flt_df = dataframe[(dataframe['Participant']==i) & (dataframe['Stim_RT']<value)]
        else:
            flt_df = dataframe[(dataframe['Participant']==i) & (dataframe['Stim_RT']>value)]
        count = len(flt_df)
        ratio = count / total
        if ratio > 0.01*percent:
            if type == 'fast':
                text = '过快反应试次数： ' + str(count) + '占比： ' + str(100*ratio) + '%'
                add_line = {'受试者编号': i, '剔除原因': '过快反应占比高于设定值', '详情': text}
            else:
                text = '过慢反应试次数： ' + str(count) + '占比： ' + str(100*ratio) + '%'
                add_line = {'受试者编号': i, '剔除原因': '过慢反应占比高于设定值', '详情': text}
            output_df.append(add_line, ignore_index=True)
            flt_list.append(i)
    
    return (output_df, flt_list)
    

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
    part_speed_fast = st.checkbox('总体过快反应')
    if part_speed_fast:
        part_too_fast = st.number_input('过快反应阈值：', min_value=0, value=300, placeholder="请输入整数时长...")
        part_too_fast_per = st.number_input('过快反应占比：', min_value=0, max_value=100, value=10, placeholder="请输入整数百分比...")
        st.write('所有试次中，反应时低于 ', part_too_fast, ' ms 的试次超过 ', part_too_fast_per, '% 的受试者数据将被剔除')
        
    part_speed_slow = st.checkbox('总体过慢反应')
    if part_speed_slow:
        part_too_slow = st.number_input('过慢反应阈值：', min_value=0, value=10000, placeholder="请输入整数时长...")
        part_too_slow_per = st.number_input('过慢反应占比：', min_value=0, max_value=100, value=10, placeholder="请输入整数百分比...")
        st.write('所有试次中，反应时高于 ', part_too_slow, ' ms 的试次超过 ', part_too_slow_per, '% 的受试者数据将被剔除')
    part_acc = st.checkbox('错误率')
    if part_acc:
        part_acc_num = st.number_input('错误率阈值：', min_value=0, max_value=100, value=35, placeholder="请输入整数百分比...")
        st.write('所有试次中，错误率超过 ', part_acc_num, '% 的受试者数据将被剔除')
    part_sd = st.checkbox('反应时超出群体反应时标准差')
    if part_sd:
        part_sd_num = st.number_input('反应时标准差倍数：', min_value=0, max_value=10, value=3, placeholder="请输入整数倍标准差...")
        st.write('所有试次的平均反应时在所有参与者平均反应时± ', part_sd_num, ' 个标准差以外的受试者数据将被剔除')
    
    if st.button('受试者剔除预处理'):
        part_fast_flt = total_speed_flt(user_data, 'fast', part_too_fast, part_too_fast_per)[0]
    
        st.text('剔除结果：')
        st.write(part_fast_flt)
    
    st.subheader('试次剔除标准', divider=True)
    trial_speed_fast = st.checkbox('试次过快反应')
    if trial_speed_fast:
        trial_too_fast = st.number_input('过快反应阈值：', min_value=0, value=300, placeholder="请输入整数时长...")
        st.write('所有试次中，反应时低于 ', trial_too_fast, ' ms 的试次数据将被剔除')
    trial_speed_slow = st.checkbox('试次过慢反应')
    if trial_speed_slow:
        trial_too_slow = st.number_input('过慢反应阈值：', min_value=0, value=10000, placeholder="请输入整数时长...")
        st.write('所有试次中，反应时高于 ', trial_too_slow, ' ms 的试次数据将被剔除')
    
    if st.button('受试者剔除预处理'):
        part_fast_flt = total_speed_flt(user_data, 'fast', part_too_fast, part_too_fast_per)[0]
    
        st.text('剔除结果：')
        st.write(part_fast_flt)
    
    st.subheader('错误反应处理', divider=True)
    trial_wrong = st.checkbox('错误反应')
    if trial_wrong:
        trial_wrong_choi = st.radio('选择对错误反应的处理方式',['基于该受试者所有正确反应时的平均值','基于该试次的错误反应时'])
        trial_wrong_val = st.number_input('反应时增加：', min_value=0, value=300, placeholder="请输入整数时长...")
        if trial_wrong_choi == '基于该受试者所有正确反应时的平均值':
            st.write('错误反应的反应时将替换为该受试者所有正确反应时平均值+ ', trial_too_fast, ' ms')
        else:
            st.write('错误反应的反应时将替换为该试次反应时+ ', trial_too_fast, ' ms')
        
    st.text('剔除结果：')

confirm = False

if check_res == True:
    st.write(' ')
    st.header('Step 4. 确认以上处理方式')
    st.info('检查已选定的数据预处理方式，确认无误即可开始分析')
    
    st.subheader('已选定的处理方式', divider=True)
    st.text('受试者剔除标准')
    
    st.text('试次剔除标准')
    
    st.text('错误反应处理')
    
    if st.button('确认'):
        st.write('已确认处理方式')
        confirm = True
    
if confirm == True:
    st.write(' ')
    st.header('Step 5. 描述性结果展示')
    st.info('每个阶段的反应时和正确率结果展示')

if confirm == True:
    st.write(' ')
    st.header('Step 6. 得到分析结果')
    st.info('计算后的结果展示及下载')
    
    # res_name,res_data = convert_df(file)

    # st.subheader('下载结果文件', divider='rainbow')
    # dl_name = str(res_name) + '.csv'
    # st.download_button(label=res_name,
    #                 data=res_data,
    #                 file_name=dl_name,
    #                 mime='csv')

    st.write('')
    st.info('完成~')
    st.balloons()

st.write(' ')
st.header('一些参考文献')
st.write('[1]杨晨, & 陈增祥. (2019). 数字有形状吗?数字信息精确性和品牌标识形状的匹配效应. 心理学报, 51(7), 16.')
st.write('[2]钱淼, 周立霞, 鲁甜甜, 翁梦星, & 傅根跃. (2015). 幼儿友好型内隐联想测验的建构及有效性. 心理学报, 47(7), 903–913.')
st.write('[3]Greenwald, A. G., Nosek, B. A., & Banaji, M. R. (2003).Understanding and using the implicit association test: An improved scoring algorithm. Journal of Personality and Social Psychology,  85(2), 197–216.')
