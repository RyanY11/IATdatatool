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
from PIL import Image

# 数据模板下载
@st.cache_data
def convert_df(dataframe):
    '''
    读取数据模板，再次转换为CSV支持下载
    '''
    return dataframe.to_csv().encode('utf-8')


# 数据表校验
def check_data(dataframe):
    '''
    校验数据列是否齐全，是否有缺失值
    传入——
    dataframe: 需要处理的数据表
    返回——
    T/F: 校验成功/失败
    '''
    default_col = ['Participant','Running','Stim_ACC','Stim_RT']
    missing = [col for col in default_col if col not in dataframe]
    if len(missing) == 0:
        st.info("数据表中包含所有所需的列。下方显示为上传的数据内容：")
        check_null = dataframe[((pd.isna(dataframe['Participant'])) | (pd.isna(dataframe['Running'])) | (pd.isna(dataframe['Stim_ACC'])) | pd.isna(dataframe['Stim_RT']))]
        if len(check_null) == 0:
            return True
        else:
            st.info('※数据表有缺失值，详见下表：')
            st.write(check_null)
            st.write('建议检查数据表，处理后再重新上传')
    else:
        st.info(f"※数据表缺少以下列：{', '.join(missing)}")
        return False


# 数据表概览
def data_overview(dataframe):
    '''
    校验数据通过后，展示上传的数据表
    传入——
    dataframe: 需要处理的数据表
    返回——
    (rows, participants, types): 数据行数/被试数/IAT阶段名称
    '''
    rows = str(dataframe.shape[0])
    parts = str(dataframe['Participant'].nunique())
    types = ','.join(dataframe['Running'].unique().tolist())
    
    return (rows, parts, types)


# 总体-过快/过慢剔除
def total_speed_flt(dataframe, t_type, value, percent):
    '''
    输入——
    dataframe: 传入数据表
    t_type: 判断类型过快fast，过慢slow
    value: 过快/过慢的判定阈值
    percent: 过快/过慢反应占比的判定阈值
    返回——
    output_df: 剔除详情表
    flt_list: 剔除的受试者ID list
    '''
    
    output_df = pd.DataFrame(columns=['受试者编号','处理原因','详情'])
    flt_list = []
    part_list = dataframe['Participant'].unique().tolist()
    for i in part_list:
        total = len(dataframe[(dataframe['Participant']==i)])
        if t_type == 'fast':
            flt_df = dataframe[(dataframe['Participant']==i) & (dataframe['Stim_RT']<value)]
        else:
            flt_df = dataframe[(dataframe['Participant']==i) & (dataframe['Stim_RT']>value)]
        count = len(flt_df)
        ratio = round((count / total), 5)
        if ratio > 0.01*percent:
            if t_type == 'fast':
                text = '过快反应试次数： ' + str(count) + '，占比： ' + str(100*ratio) + '%'
                add_line = {'受试者编号': i, '处理原因': '过快反应占比高于设定值', '详情': text}
            else:
                text = '过慢反应试次数： ' + str(count) + '，占比： ' + str(100*ratio) + '%'
                add_line = {'受试者编号': i, '处理原因': '过慢反应占比高于设定值', '详情': text}

            output_df.loc[len(output_df), :] = add_line
            flt_list.append(i)
    
    return (output_df, flt_list)


# 总体-错误率剔除
def total_error_rate_flt(dataframe, percent):
    '''
    输入——
    dataframe: 传入数据表
    percent: 错误率占比的判定阈值
    返回——
    output_df: 剔除详情表
    flt_list: 剔除的受试者ID list
    '''
    
    output_df = pd.DataFrame(columns=['受试者编号','处理原因','详情'])
    flt_list = []
    part_list = dataframe['Participant'].unique().tolist()
    for i in part_list:
        total = len(dataframe[(dataframe['Participant']==i)])
        wrong = len(dataframe[(dataframe['Participant']==i) & (dataframe['Stim_ACC']==0)])
        ratio =round((wrong / total), 5)
        if ratio > 0.01*percent:
            text = '错误率为： ' + str(100*ratio) + '%'
            add_line = {'受试者编号': i, '处理原因': '错误率高于设定值', '详情': text}
            output_df.loc[len(output_df), :] = add_line
            flt_list.append(i)

    return (output_df, flt_list)


# 总体-反应时标准差剔除
def total_rt_std_flt(dataframe, times):
    '''
    输入——
    dataframe: 传入数据表
    times: 被试反应时超出群体标准差倍数
    返回——
    output_df: 剔除详情表
    flt_list: 剔除的受试者ID list
    '''
    
    output_df = pd.DataFrame(columns=['受试者编号','处理原因','详情'])
    flt_list = []
    part_list = dataframe['Participant'].unique().tolist()
    total_std = round((dataframe['Stim_RT'].std()), 3)
    for i in part_list:
        part_df = dataframe[(dataframe['Participant']==i)]
        part_std = round((part_df['Stim_RT'].std()), 3)
        if part_std > (times*total_std):
            dif = round((part_std/total_std), 3)
            text = '受试者反应时标准差为： ' + str(part_std) + '，是群体标准差的： ' + str(dif) + '倍'
            add_line = {'受试者编号': i, '处理原因': '反应时标准差超出设定值倍数', '详情': text}
            output_df.loc[len(output_df), :] = add_line
            flt_list.append(i)
        
    return (output_df, flt_list)

            
# 合并总体剔除情况
def flt_merge(output_df_list, flt_list, dataframe, order_name):
    '''
    传入——
    output_df_list: 几种总体剔除结果的dataframe list
    flt_list: 剔除的受试者ID list
    dataframe: 待处理数据表
    order_name: 排序索引列名
    返回——
    output_df: 剔除的情况表
    left_df: 剩余被试的数据表
    '''
    
    output_df = pd.concat(output_df_list, axis=0, join='outer', ignore_index=True)
    output_df.sort_values(by=order_name,inplace=True)
    # new_list = list(dict.fromkeys(flt_list))
    new_list = list(set(flt_list))
    left_df = dataframe[~dataframe['Participant'].isin(new_list)]
    
    return (output_df, left_df)


# 试次-过快/过慢剔除
def trial_speed_flt(dataframe, t_type, value):
    '''
    输入——
    dataframe: 传入数据表
    t_type: 判断类型过快fast，过慢slow
    value: 过快/过慢的判定阈值
    返回——
    output_df: 剔除详情表
    flt_list: 剔除的试次index list
    '''
    
    output_df = pd.DataFrame(columns=['试次编号','处理原因','详情'])
    flt_list = []
    index_list = dataframe.index.tolist()
    for i in index_list:
        trial_rt = dataframe[(dataframe.index==i)]['Stim_RT'].values[0]
        if t_type == 'fast':
            if trial_rt < value:
                text = '试次反应时为： ' + str(trial_rt)
                add_line = {'试次编号': i, '处理原因': '反应时低于设定值', '详情': text}
                output_df.loc[len(output_df), :] = add_line
                flt_list.append(i)
        else:
            if trial_rt > value:
                text = '试次反应时为：'+ str(trial_rt)
                add_line = {'试次编号': i, '处理原因': '反应时高于设定值', '详情': text}
                output_df.loc[len(output_df), :] = add_line
                flt_list.append(i)
    output_df.sort_values(by='试次编号',inplace=True)
    
    return (output_df, flt_list)
    

# 试次-错误反应处理
def trial_wrong_flt(dataframe, t_type, value):
    '''
    输入——
    dataframe: 传入数据表
    t_type: 错误反应处理方式：1-基于该受试者所有正确反应时的平均值,2-基于该试次的错误反应时
    value: 惩罚增加的反应时值
    返回——
    output_df: 处理详情表
    # flt_list: 处理的试次index list
    processed_df: 处理后的数据表
    '''
    
    change_list = []
    
    if t_type == 1:
        output_df = pd.DataFrame(columns=['试次编号','处理原因','受试者正确反应时均值','详情'])
        part_list = dataframe['Participant'].unique().tolist()
        for j in part_list:
            part_df = dataframe[(dataframe['Participant']==j)]
            part_cor_df = part_df[part_df['Stim_ACC']==1]
            part_rt_avg = int((part_cor_df['Stim_RT'].mean()))
            index_list = part_df.index.tolist()
            for i in index_list:
                trial_acc = part_df[(part_df.index==i)]['Stim_ACC'].values[0]
                trial_rt = part_df[(part_df.index==i)]['Stim_RT'].values[0]
                if trial_acc == 0:
                    text = '错误试次反应时为：'+ str(trial_rt)
                    add_line = {'试次编号': i, '处理原因': '错误反应', '受试者正确反应时均值': str(part_rt_avg), '详情': text}
                    output_df.loc[len(output_df), :] = add_line
                    # flt_list.append(i)
                    
                    change_list.append({'line': i, 'value': part_rt_avg + value})
    
    elif t_type == 2:
        output_df = pd.DataFrame(columns=['试次编号','处理原因','详情'])
        index_list = dataframe.index.tolist()
        for i in index_list:
            trial_acc = dataframe[(dataframe.index==i)]['Stim_ACC'].values[0]
            trial_rt = dataframe[(dataframe.index==i)]['Stim_RT'].values[0]
            if trial_acc == 0:
                text = '错误试次反应时为：'+ str(trial_rt)
                add_line = {'试次编号': i, '处理原因': '错误反应', '详情': text}
                output_df.loc[len(output_df), :] = add_line
                # flt_list.append(i)
                
                change_list.append({'line': i, 'value': trial_rt + value})
                
    else:
        pass
    output_df.sort_values(by='试次编号',inplace=True)
    
    processed_df = dataframe.copy()
    for k in change_list:
        processed_df.loc[k['line'], 'Stim_RT'] = k['value']
    
    return (output_df, processed_df)


# 描述统计结果
def data_descriptive(dataframe):
    '''
    输入——
    dataframe: 传入数据表
    返回——
    output_df: 描述统计详情表
    '''
    
    output_df = pd.DataFrame(columns=['阶段名称','反应时均值','反应时标准差','正确率均值','正确率标准差'])
    stage_list = dataframe['Running'].unique().tolist()
    for i in stage_list:
        stage_df = dataframe[(dataframe['Running']==i)]
        stage_rt_avg = round((stage_df['Stim_RT'].mean()), 3)
        stage_rt_std = round((stage_df['Stim_RT'].std()), 3)
        stage_acc_avg = round((stage_df['Stim_ACC'].mean()), 3)
        stage_acc_std = round((stage_df['Stim_ACC'].std()), 3)
        add_line = {'阶段名称': i, '反应时均值': stage_rt_avg, '反应时标准差': stage_rt_std, '正确率均值': stage_acc_avg, '正确率标准差': stage_acc_std}
        output_df.loc[len(output_df), :] = add_line

    return output_df


# 计算数据指标
def val_calculate(dataframe, listname):
    '''
    输入——
    dataframe: 传入数据表
    cong_list: 条件列表
    返回——
    rt_avg: 包含条件列表中名称的反应时均值
    rt_std: 包含条件列表中名称的反应时标准差
    '''
    
    df_slice = dataframe.loc[dataframe['Running'].isin(listname),:]
    rt_avg = round((df_slice['Stim_RT'].mean()), 3)
    rt_std = round((df_slice['Stim_RT'].std()), 3)
    
    return rt_avg, rt_std

# 生成结果文件
def core_analysis(dataframe, cong_list, incong_list):
    '''
    输入——
    dataframe: 传入数据表
    cong_list: 一致条件列表
    incong_list: 不一致条件列表
    返回——
    output_df: 处理后的数据表
    '''
    
    output_df = pd.DataFrame(columns=['受试者编号', '一致反应时均值', '一致反应时标准差', '不一致反应时均值', '不一致反应时标准差', 
                                      '全部反应时均值', '全部反应时标准差', 'd值'])
    part_list = dataframe['Participant'].unique().tolist()
    for i in part_list:
        part_df = dataframe[(dataframe['Participant']==i)]
        
        both_list = cong_list + incong_list

        part_cong_rt_avg, part_cong_rt_std = val_calculate(part_df, cong_list)
        part_incong_rt_avg, part_incong_rt_std = val_calculate(part_df, incong_list)
        part_both_rt_avg, part_both_rt_std = val_calculate(part_df, both_list)
        
        if direction == 'incong - cong':
            d_val = round(((part_incong_rt_avg - part_cong_rt_avg) / part_both_rt_std), 3)
        else:
            d_val = round(((part_cong_rt_avg - part_incong_rt_avg) / part_both_rt_std), 3)
        
        add_line = {'受试者编号': i, '一致反应时均值': part_cong_rt_avg, '一致反应时标准差': part_cong_rt_std, 
                   '不一致反应时均值': part_incong_rt_avg, '不一致反应时标准差': part_incong_rt_std, 
                   '全部反应时均值': part_both_rt_avg, '全部反应时标准差': part_both_rt_std, 'd值': d_val}
        output_df.loc[len(output_df), :] = add_line
    
    return output_df


# 页面逻辑与绘制
st.title('IAT数据处理工具')
st.info('工具简介')
st.write('Hi，欢迎你来到这~')
st.write(' ')
st.write('这是一个在线的IAT（内隐联想测验）数据处理工具，它能够帮助你便捷地处理研究参与者在IAT实验中的反应时和正确率数据，并最终完成内隐方向强度d值的计算。')
st.write('接下来，请按照页面上的指示，上传固定好格式的实验数据表格，依据你的参考文献选取各项数据处理的方式和参数，确认后即可在页面上看到自动处理的结果，并支持下载结果表格。')
st.write('这是一个开源的小工具，开源地址详见页面末尾。')
st.write('此外，请放心，你的实验数据上传后只是在浏览器本地的缓存中进行处理，并不会泄露。')
st.write(' ')

part_method = {}
trial_method = {}
wrong_method = {}

st.header('Step 1. 下载数据模板')
st.info('点击下载数据模板，并按照模板填写数据表')
st.write('数据表中需要包含的信息：')
st.write('Participant - 受试者编号（建议为纯数字）')
st.write('Running - 该trial属于实验的阶段名称（比如stage4代表联合测验相容条件，stage7代表联合测验反转不相容条件）')
st.write('Stim_ACC - 该trial的正误')
st.write('Stim_RT - 该trial的反应时')
st.write(' ')
st.text('※请勿改动数据模板的列名！！')

local_path = os.getcwd()
data_model = convert_df(pd.read_csv(os.path.join(local_path, 'data_sample.csv')))

st.download_button('下载数据模板',
                   data=data_model,
                   file_name='data_sample.csv',
                   mime='text/csv', key=9)

st.write(' ')
st.header('Step 2. 上传IAT实验数据')
st.info('将填写完的数据文件上传')
check_res = False
check_name = False
data_file = st.file_uploader('选择数据文件（※仅csv格式！！）')
if data_file is not None:
    user_data = pd.read_csv(data_file)
    check_res = check_data(user_data)
    if check_res == True:
        st.dataframe(user_data)
        res_rows,res_parts,res_types = data_overview(user_data)
        st.subheader('数据表概览', divider='rainbow')
        st.write('数据行数： ' + res_rows)
        st.write('包含的受试者人数： ' + res_parts)
        st.write('包含的IAT阶段： ' + res_types)

if check_res == True:

    st.write(' ')
    st.header('Step 3. 选择预处理参数')
    st.info('在侧边栏中选定各项数据预处理方式及参数')
    st.text('※请按顺序逐个确定和填写参数！！')
    
    st.sidebar.subheader('① 指定条件阶段名', divider=True)
    cong_opts = []
    incong_opts = []
    incong_name = []
    
    cong_opts = st.sidebar.multiselect('选择相容条件阶段名', res_types.split(','))
    st.sidebar.write('将在后续计算中，包含以下相容条件阶段的数据')
    if cong_opts:
        st.write('选择的相容条件阶段名：')
        st.write(cong_opts)
        incong_name = set(res_types.split(',')).difference(set(cong_opts))
    incong_opts = st.sidebar.multiselect('选择不相容条件阶段名', incong_name)
    st.sidebar.write('将在后续计算中，包含以下不相容条件阶段的数据')
    if incong_opts:
        st.write('选择的不相容条件阶段名：')
        st.write(incong_opts)
    
    if cong_opts==[] or incong_opts==[]:
        st.warning('请至少选择一个相容条件阶段和一个不相容条件阶段')
    else:
        check_name = True
    
    st.sidebar.subheader('② 受试者剔除标准', divider=True)
    part_method_list = []

    part_speed_fast = st.sidebar.checkbox('总体过快反应')
    if part_speed_fast:
        part_too_fast = st.sidebar.number_input('过快反应阈值：', min_value=0, value=300, placeholder="请输入整数时长...", key=0)
        part_too_fast_per = st.sidebar.number_input('过快反应占比：', min_value=0, max_value=100, value=10, placeholder="请输入整数百分比...", key=1)
        st.write('所有试次中，反应时低于 ', part_too_fast, ' ms 的试次超过 ', part_too_fast_per, '% 的受试者数据将被剔除')
        
    part_speed_slow = st.sidebar.checkbox('总体过慢反应')
    if part_speed_slow:
        part_too_slow = st.sidebar.number_input('过慢反应阈值：', min_value=0, value=10000, placeholder="请输入整数时长...", key=2)
        part_too_slow_per = st.sidebar.number_input('过慢反应占比：', min_value=0, max_value=100, value=10, placeholder="请输入整数百分比...", key=3)
        st.write('所有试次中，反应时高于 ', part_too_slow, ' ms 的试次超过 ', part_too_slow_per, '% 的受试者数据将被剔除')
    part_acc = st.sidebar.checkbox('错误率')
    if part_acc:
        part_acc_num = st.sidebar.number_input('错误率阈值：', min_value=0, max_value=100, value=35, placeholder="请输入整数百分比...", key=4)
        st.write('所有试次中，错误率超过 ', part_acc_num, '% 的受试者数据将被剔除')
    part_std = st.sidebar.checkbox('反应时超出群体反应时标准差')
    if part_std:
        part_std_num = st.sidebar.number_input('反应时标准差倍数：', min_value=0, max_value=10, value=3, placeholder="请输入整数倍标准差...", key=5)
        st.write('所有试次的平均反应时在所有参与者平均反应时± ', part_std_num, ' 个标准差以外的受试者数据将被剔除')
    
    total_flt_data = []
    if part_speed_fast:
        part_fast_flt, part_fast_flt_id = total_speed_flt(user_data, 'fast', part_too_fast, part_too_fast_per)
        part_method_list.append({'方法': '总体过快反应', '参数': part_too_fast, '占比': part_too_fast_per, '剔除受试者数量': len(part_fast_flt_id)})
    if part_speed_slow:
        part_slow_flt, part_slow_flt_id = total_speed_flt(user_data, 'slow', part_too_slow, part_too_slow_per)
        part_method_list.append({'方法': '总体过慢反应', '参数': part_too_slow, '占比': part_too_slow_per, '剔除受试者数量': len(part_slow_flt_id)})
    if part_acc:
        part_rate, part_rate_id = total_error_rate_flt(user_data, part_acc_num)
        part_method_list.append({'方法': '错误率', '参数': part_acc_num, '剔除受试者数量': len(part_rate_id)})
    if part_std:
        part_times, part_times_id = total_rt_std_flt(user_data, part_std_num)
        part_method_list.append({'方法': '反应时超出群体反应时标准差', '参数': part_std_num, '剔除受试者数量': len(part_times_id)})

    st.text('② 受试者剔除-处理结果：')
    part_fb_list = []
    part_flt_list = []
    if part_speed_fast:
        part_fb_list.append(part_fast_flt)
        part_flt_list.extend(part_fast_flt_id)
    if part_speed_slow:
        part_fb_list.append(part_slow_flt)
        part_flt_list.extend(part_slow_flt_id)
    if part_acc:
        part_fb_list.append(part_rate)
        part_flt_list.extend(part_rate_id)
    if part_std:
        part_fb_list.append(part_times)
        part_flt_list.extend(part_times_id)
    
    if part_fb_list != []:
        total_flt_res, total_flt_data = flt_merge(part_fb_list, part_flt_list, user_data, '受试者编号')
        st.write(total_flt_res)
    else:
        st.write('*未选择受试者预处理方法')
    
    st.write('')
    part_method = {'受试者预处理方法': part_method_list}
    
    st.text('※确认完以上信息后再继续下一步！！')
    st.write('')
    
    st.sidebar.subheader('③ 试次剔除标准', divider=True)
    trial_method_list = []
    trial_flt_data = []
    
    trial_speed_fast = st.sidebar.checkbox('试次过快反应')
    if trial_speed_fast:
        trial_too_fast = st.sidebar.number_input('过快反应阈值：', min_value=0, value=300, placeholder="请输入整数时长...", key=6)
        st.write('所有试次中，反应时低于 ', trial_too_fast, ' ms 的试次数据将被剔除')
    trial_speed_slow = st.sidebar.checkbox('试次过慢反应')
    if trial_speed_slow:
        trial_too_slow = st.sidebar.number_input('过慢反应阈值：', min_value=0, value=10000, placeholder="请输入整数时长...", key=7)
        st.write('所有试次中，反应时高于 ', trial_too_slow, ' ms 的试次数据将被剔除')
    
    if trial_speed_fast:
        trial_fast_flt, trial_fast_flt_id = trial_speed_flt(user_data, 'fast', trial_too_fast)
        trial_method_list.append({'方法': '试次过快反应', '参数': trial_too_fast, '剔除试次数量': len(trial_fast_flt_id)})
    if trial_speed_slow:
        trial_slow_flt, trial_slow_flt_id = trial_speed_flt(user_data,'slow', trial_too_slow)
        trial_method_list.append({'方法': '试次过慢反应', '参数': trial_too_slow, '剔除试次数量': len(trial_slow_flt_id)})

    st.text('③ 试次剔除-处理结果：')
    trial_fb_list = []
    trial_flt_list = []
    if trial_speed_fast:
        trial_fb_list.append(trial_fast_flt)
        trial_flt_list.extend(trial_fast_flt_id)
    if trial_speed_slow:
        trial_fb_list.append(trial_slow_flt)
        trial_flt_list.extend(trial_slow_flt_id)
    
    if part_fb_list != []:
        if trial_fb_list != []:
            trial_flt_res, trial_flt_data = flt_merge(trial_fb_list, trial_flt_list, total_flt_data, '试次编号')
            st.write(trial_flt_res)
            trial_method = {'试次预处理方法': trial_method_list}
        else:
            st.write('*未选择试次预处理方法')
            trial_flt_data = total_flt_data.copy()
            st.text('确定不需要处理试次数据的话，可以继续下一步')
            trial_method = {'试次预处理方法': '无'}
    else:
        st.write('*请先按受试者处理后，再进行试次处理')
    st.write('')
    
    st.text('※确认完以上信息后再继续下一步！！')
    st.write('')
    
    st.sidebar.subheader('④ 错误反应处理', divider=True)
    wrong_method_list = ''
    
    t_type = 0
    trial_wrong = st.sidebar.checkbox('错误反应')
    if trial_wrong:
        trial_wrong_choi = st.sidebar.radio('选择对错误反应的处理方式',['基于该受试者所有正确反应时的平均值','基于该试次的错误反应时'])
        trial_wrong_val = st.sidebar.number_input('反应时增加：', min_value=0, value=300, placeholder="请输入整数时长...", key=8)
        if trial_wrong_choi == '基于该受试者所有正确反应时的平均值':
            t_type = 1
            st.write('错误反应的反应时将替换为该受试者所有正确反应时平均值 + ', trial_wrong_val, ' ms')
        else:
            t_type = 2
            st.write('错误反应的反应时将替换为该试次反应时 + ', trial_wrong_val, ' ms')
        
        trial_wrong_res = pd.DataFrame(columns=['试次编号','处理原因','详情'])
        if part_fb_list != []:
            trial_wrong_res, trial_wrong_data = trial_wrong_flt(trial_flt_data, t_type, trial_wrong_val)
            wrong_method_list = {'方法': trial_wrong_choi, '参数': trial_wrong_val, '处理试次数量': len(trial_wrong_data)}
            wrong_method = {'错误反应预处理方法': wrong_method_list}
        
    else:
        trial_wrong_data = trial_flt_data.copy()
        st.text('确定不需要处理试次数据的话，可以继续下一步')
        wrong_method = {'错误反应预处理方法': '无'}
    
        
    st.text('④ 错误反应-处理结果：')
    if trial_wrong:
        st.write(trial_wrong_res)
    else:
        st.text('确定不需要处理错误试次的话，可以继续下一步')
    st.write('')
    
    
    st.text('⑤ D值相减方式')

    st.sidebar.subheader('⑤ 选择D值相减方式', divider=True)
    dire = st.sidebar.radio('请选择', ['不相容任务 - 相容任务','相容任务 - 不相容任务'])
    
    if dire == "不相容任务 - 相容任务":
        st.sidebar.write("D值相减方式为： 不相容任务 - 相容任务")
        st.text('D值相减方式为： 不相容任务 - 相容任务')
        direction = 'incong - cong'
    else:
        st.sidebar.write("D值相减方式为： 相容任务 - 不相容任务")
        st.text('D值相减方式为： 相容任务 - 不相容任务')
        direction = 'cong - incong'
    
    st.text('※确认完以上信息后再继续下一步！！')
    st.write('')

confirm = False

if check_name == True:
    st.write(' ')
    st.header('Step 4. 确认以上处理方式')
    st.info('检查已选定的数据预处理方式，确认无误即可开始计算d值')
    
    st.subheader('已选定的处理方式', divider=True)
    st.text('受试者剔除标准')
    st.write(part_method)
    
    st.text('试次剔除标准')
    st.write(trial_method)
    
    st.text('错误反应处理')
    st.write(wrong_method)
    
    if st.button('确认', type='primary', key=10):
        st.write('已确认处理方式')
        confirm = True
    
if confirm == True:
    st.write(' ')
    st.header('Step 5. 描述性结果展示')
    st.info('每个阶段的反应时和正确率结果展示')
    overview_res = data_descriptive(trial_wrong_data)
    st.write(overview_res)
    st.write(' ')

if confirm == True:
    st.write(' ')
    st.header('Step 6. 得到分析结果')
    st.info('计算后的结果展示及下载（保留3位小数）')
    
    res_data = core_analysis(trial_wrong_data, cong_opts, incong_opts)
    
    st.write(res_data)
    st.write('')
    
    res_data_file = convert_df(res_data)

    st.subheader('下载结果文件', divider='rainbow')
    if st.download_button(label='分析结果文件',
                    data=res_data_file,
                    file_name='iat_analysis_result.csv',
                    mime='csv', 
                    type='primary',
                    key=15):
        st.balloons()

    st.write('')
    st.write('')
    st.info('至此,全部完成~')
    

st.write(' ')
st.header('一些参考文献')
st.write('[1]杨晨, & 陈增祥. (2019). 数字有形状吗?数字信息精确性和品牌标识形状的匹配效应. 心理学报, 51(7), 16.')
st.write('[2]钱淼, 周立霞, 鲁甜甜, 翁梦星, & 傅根跃. (2015). 幼儿友好型内隐联想测验的建构及有效性. 心理学报, 47(7), 903–913.')
st.write('[3]Greenwald, A. G., Nosek, B. A., & Banaji, M. R. (2003).Understanding and using the implicit association test: An improved scoring algorithm. Journal of Personality and Social Psychology,  85(2), 197–216.')

st.write(' ')
st.header('此工具开源地址')
st.write('https://github.com/RyanY11/IATdatatool')

st.write(' ')
st.header('支持作者')
image = Image.open('QRcode1.jpg')
st.image(image, caption='如果这个小工具对你有所帮助的话，也可以请我喝杯咖啡~')
st.write('谢谢啦！ Thanks♪(･ω･)ﾉ')
