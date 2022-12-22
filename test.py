# -*- coding: utf-8 -*-
"""
IATdatatool
V3.0

"""

import streamlit as st
import openai

# 调用openai反馈一些好玩的话语
openai.api_key = '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'

a = openai.Completion.create(
  model="text-davinci-003",
  prompt="给我说一句和心理学相关的鼓励的话吧",
  top_p=1,
  temperature=0,
  max_tokens=1000
)
# print(a['choices'][0]['text'])
st.info(a['choices'][0]['text'])

# 页面绘制
st.title('IAT数据处理工具')
st.info('这是一个在线的，用于处理IAT实验数据的程序')
st.write(' ')


# st.balloons()