# -*- coding: utf-8 -*-
"""
Created on Sun May 12 00:53:37 2019

@author: yzpry
"""

from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.messagebox import *
import os
import numpy as np
import math
import csv
import xlrd

def selectPath():
    orig_file_path = askdirectory()
    path.set(orig_file_path)

shuru = Tk()
path = StringVar()
orig_file_path = StringVar()
shuru.title(u"IAT数据批处理工具V2.0.0")

#choose the file path
Label(shuru,text=u"打开数据文件存储位置").grid(row = 0, column = 0)
l1 = Label(shuru,text=u"请选择数据文件路径：").grid(row = 1, column = 0)
c1 = Entry(shuru, textvariable = path).grid(row = 1, column = 1)
b1 = Button(shuru, text = u"文件夹选择", command = selectPath).grid(row = 1, column = 2)

#input the name of condition
Label(shuru,text=u"条件名称").grid(row = 6, column = 0)
l3 = Label(shuru, text=u"请输入相容条件名称：").grid(row = 7, column = 0)
l4 = Label(shuru, text=u"请输入不相容条件名称：").grid(row = 8, column = 0)
c3_text = StringVar()
c4_text = StringVar()
c3 = Entry(shuru, textvariable = c3_text).grid(row = 7, column = 1)
c4 = Entry(shuru, textvariable = c4_text).grid(row = 8, column = 1)
c3_text.set(" ")
c4_text.set(" ")

#input the processing rules
Label(shuru,text=u"处理规则").grid(row = 10, column = 0)
l5 = Label(shuru, text=u"请输入“过快”反应时阈值：").grid(row = 11, column = 0)
l6 = Label(shuru, text=u"请输入“过慢”反应时阈值：").grid(row = 12, column = 0)
l7 = Label(shuru, text=u"请输入“错误反应”惩罚反应时：").grid(row = 13, column = 0)
c5_text = StringVar()
c6_text = StringVar()
c7_text = StringVar()
c5 = Entry(shuru, textvariable = c5_text).grid(row = 11, column = 1)
c6 = Entry(shuru, textvariable = c6_text).grid(row = 12, column = 1)
c7 = Entry(shuru, textvariable = c7_text).grid(row = 13, column = 1)
c5_text.set(" ")
c6_text.set(" ")
c7_text.set(" ")
l8 = Label(shuru, text="ms").grid(row = 11, column = 2)
l9 = Label(shuru, text="ms").grid(row = 12, column = 2)
l10 = Label(shuru, text="ms").grid(row = 13, column = 2)
Label(shuru,text=u"附加选项").grid(row = 14, column = 0)
c8 = IntVar()
Checkbutton(shuru, text=u"取log变换", variable=c8).grid(row=15, column = 0,sticky=W)

#print the input
def on_click():
    bb = path.get().strip()
    #bb = abs_filepath.get().strip()
    cc = c3_text.get().strip()
    dd = c4_text.get().strip()
    ee = c5_text.get().strip()
    ff = c6_text.get().strip()
    gg = c7_text.get().strip()
    hh = c8.get()
    print(ee)
    print(ff)
    
    context = str(u"数据文件位置：%s \n 相容条件名：%s \n 不相容条件名：%s \n 过快：%s \n 过慢：%s \n 惩罚：%s \n 是否取Log %s" %(bb,cc,dd,ee,ff,gg,hh))
    showinfo(title=u"请确认输入信息", message = context)
    
    #Prepare the output file    
    os.chdir(bb)
    file_list = os.listdir(bb)
    print(file_list)
    
    op = open('output.csv','a+')
    op.write('Subject,deleted,RTcon,RTincon,all_correct_std,d\n')
    
    for i in range(0,len(file_list)):
        op.write(str(file_list[i]) + ',')
        
        pid = []
        condition = []
        acc = []
        rt = []
        con = []
        incon= []
        con_all = []
        incon_all = []
        all_cor = []
        dele = 0
    
        try:
            data = xlrd.open_workbook(os.path.join(bb,file_list[i]))
            table = data.sheets()[0]
            nrows = table.nrows
            ncols = table.ncols

            #store the data into lists
            for a in range(1,nrows):
                pid_val = str(table.cell(a,1).value)
                pid.append(pid_val)    
                condition_val = str(table.cell(a,5).value)
                condition.append(condition_val)
                acc_val = str(table.cell(a,6).value)
                acc.append(acc_val)
                rt_val = str(table.cell(a,7).value)
                rt.append(rt_val)

            #deltete the data which were too fast or too slow
            for b in range(len(rt)-1,-1,-1):
                if float(rt[b]) > float(ff) or float(rt[b]) < float(ee):
                    del pid[b]
                    del condition[b]
                    del acc[b]
                    del rt[b]
                    dele = dele + 1

            op.write(str(dele) + ',')

            #calculate the mean rt of right trials
            for c in range(len(rt)):
                if (acc[c]) == '1.0' and condition[c] == cc:
                    con.append(float(rt[c]))
                elif (acc[c]) == '1.0' and condition[c] == dd:
                    incon.append(float(rt[c]))
                else:
                    print('Dealing with other trials...')
 
            con_cor_rt_mean = np.mean(con)
            incon_cor_rt_mean = np.mean(incon)    
        
        #deal with the wrong trials'rt    
            for d in range(len(rt)):
                if (acc[d]) == '0.0' and condition[d] == cc:
                    rt[d] = con_cor_rt_mean + float(gg)
                elif (acc[d]) == '0.0' and condition[d] == dd:
                    rt[d] = incon_cor_rt_mean + float(gg)
                else:
                    print('Dealing with other trials...')

        #calculate the group mean
            for e in range(len(rt)):
                if condition[e] == cc:
                    con_all.append(float(rt[e]))
                elif condition[e] == dd:
                    incon_all.append(float(rt[e]))
                else:
                    print('Dealing with other trials...')

        #calculate the standard diviation of all right trials
            for f in range(len(rt)):
                if acc[f] == '1.0':
                    if condition[f] == cc or condition[f] == dd:
                        all_cor.append(float(rt[f]))
                    
            if hh == 1:
                log_con_all = []
                log_incon_all = []
                log_all_cor = []
                
                for d1 in con_all:
                    log_con_all.append(math.log(float(d1)))
                for d2 in incon_all:
                    log_incon_all.append(math.log(float(d2)))
                
                log_con_all_rt_mean = np.mean(log_con_all)
                log_incon_all_rt_mean = np.mean(log_incon_all)
                
                for d3 in all_cor:
                    log_all_cor.append(math.log(float(d3)))
                    
                op.write(str(log_con_all_rt_mean) + ',')
                op.write(str(log_incon_all_rt_mean) + ',')
                
                log_all_rt_std = np.std(log_all_cor)
                                
        #calculate the d value   
                log_d_val = (log_incon_all_rt_mean - log_con_all_rt_mean) / log_all_rt_std

                op.write(str(log_all_rt_std) + ',')
                op.write(str(log_d_val) + '\n')
                
                all_cor_std = np.std(all_cor)
                
            else:
                con_all_rt_mean = np.mean(con_all)
                incon_all_rt_mean = np.mean(incon_all)
                    
                op.write(str(con_all_rt_mean) + ',')
                op.write(str(incon_all_rt_mean) + ',')
 
                all_rt_std = np.std(all_cor)

        #calculate the d value   
                d_val = (incon_all_rt_mean - con_all_rt_mean) / all_rt_std

                op.write(str(all_rt_std) + ',')
                op.write(str(d_val) + '\n')

        except FileNotFoundError:
            print(u"Error: 没有找到“" + file_list[i] + u"”文件，读取文件失败")
 
            op.write('\n')
        else:
            print("File " + file_list[i] + "处理完毕")

    showinfo(title=u'IAT数据批处理工具', message = u'数据批处理完成！')
    
    shuru.destroy()
    
Button(shuru, text=u"确定", command = on_click).grid(row = 16, column = 1, sticky=W, pady=4)

shuru.mainloop()

#print the input
def on_click():
    print(path)
    showinfo(title=u'IAT数据批处理工具', message = u'数据批处理完成！')
    
    shuru.destroy()

shuru.mainloop()