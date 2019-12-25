#!/usr/bin/python3
# coding:utf-8

from bs4 import BeautifulSoup
import time
import requests
import pickle
import tkinter as tk
import os,sys
import threading
import win32api
import win32con
from tkinter import ttk
from tkinter import messagebox as mBox

# 生成资源文件目录访问路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False): #是否Bundle Resource
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 开机启动
def start_up():
    APP_NAME = 'NetTool'  # 要添加的项值名称
    app_path =  os.path.split(os.path.realpath(__file__))[0]+'\\NetTool.exe' # 要添加的路径

    # 注册表项名
    APP_KEY_NAME = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    
    # 异常处理
    try:
        APP_KEY = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, APP_KEY_NAME, 0, win32con.KEY_ALL_ACCESS)
        if usr['startup']:
            win32api.RegSetValueEx(APP_KEY, APP_NAME, 0, win32con.REG_SZ, f'"{app_path}"')
            write_log('开机启动设置成功')
            write_log('开机启动路径：'+app_path, 0)
        else:
            win32api.RegDeleteValue(APP_KEY, APP_NAME)
            write_log('开机启动已经移除')
        win32api.RegCloseKey(APP_KEY)


    except:
        mBox.showinfo(title='开机启动', message='添加开机启动失败！')

# 退出函数
def quit():
    window.tk.call('winico', 'taskbar', 'delete', icon)
    sys.exit(0)

# 日志文件
def write_log(log,insert=1): # log为日志 insert参数控制是否插入text窗口
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
    with open('log.txt','a') as text:
        content = f'[{timestamp}] {log}\n'
        text.write(content)
    if insert:
        t.config(state='normal')
        t.insert('end',log+'\n\n')
        t.config(state='disabled')

# 设置用户信息
def usr_set(usr_dict):
    with open('c:/usr_set.pickle', 'wb') as file:
        pickle.dump(usr_dict, file)
    write_log('保存用户设置:成功')

# 读取用户信息
def usr_read():
    global usr
    if os.path.exists('c:/usr_set.pickle'):
        with open('c:/usr_set.pickle', 'rb') as file:
            usr = pickle.load(file)
    else: 
        usr    = {'usrname':'',
                  'password':'',
                  'channelshow':'',
                  'channel':'',
                  'autologin':0,
                  'stayonline':0,
                  'autowithdraw':0,
                  'startup':0}
    write_log('读取用户设置:成功',0)

# 自动登录
def auto_login():
    write_log('自动登录功能启动')
    for i in range(180):
        code = net_test()
        if  code == 0:
            write_log('开始自动登录')
            net_login()
            break
        elif code == 1:
            write_log(f'自动登录:在 {i} 秒停止,已成功联网')
            break
        else:
            write_log('无法连接至网络')
            break

    if usr['autowithdraw'] == 1:
        t.config(state='normal')
        t.insert('end','自动登录完成，将在 3 秒后自动隐藏'+'\n\n')
        t.config(state='disabled')
        time.sleep(3)
        window.withdraw()

# 登录
def net_login():
    # get请求，拉取流水号信息
    s = requests.Session()
    LOGIN_URL = 'https://i.njtech.edu.cn'
    try:
        r = s.get(LOGIN_URL)
    except:
        print('未连接wifi')
    else:
        content = r.text
        bs = BeautifulSoup(content,'lxml')
        lt = bs.find('',{'name':'lt'}).attrs['value']
        execution = bs.find('',{'name':'execution'}).attrs['value']

        # post请求
        params = {	'username': usr['usrname'],
            		'password': usr['password'],
            		'channelshow': usr['channelshow'],
            		'channel': usr['channel'],
            		'lt':f'{lt}',
            		'execution': f'{execution}',
            		'_eventId': 'submit',
            		'login': '登录'}
        s.post(r.url, params)

    time.sleep(2)
    if net_test():
        write_log('登录:登录成功')
    else:
        write_log('登录:登录失败')

# 判断网络是否连接成功
def net_test():
    try:  
        requests.get('https://www.baidu.com',timeout=2)
        write_log('网络测试:成功联网')
        return 1
    except:
        try:
            requests.get('https://www.baidu.com',timeout=2)
            write_log('网络测试:成功联网')
            return 1
        except:            
            try:
                requests.get('https://i.njtech.edu.cn',timeout=2)
                write_log('网络测试:需要登录')
                return 0
            except:
                write_log('网络测试:无法连接至网络')
                return 2

# 保持在线
def stay_online():
    write_log('保持在线功能启动')
    while 1:
        time.sleep(300)
        code = net_test()
        if code == 0:
            write_log('保持在线:网络中断',0)
            answer = mBox.askyesno('网络中断', '网络中断，是否重连')
            if answer:
                net_login()
        elif code == 1:
            write_log('保持在线:网络连接正常',0)
        else:
            pass

# 主窗口
def main_window():
    # 创建主窗口
    global window
    window = tk.Tk()
    window.title('南京工业大学网络助手')
    window.iconbitmap(njtechico)
    w = 400
    h = 450
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # 创建标题
    l = tk.Label(window,text='网络日志')
    l.pack()

    # 创建text窗口
    global t
    t = tk.Text(window,height=18,width=40)
    t.config(state='disabled')
    t.pack()

    def log_insert(log):
        t.config(state='normal')
        t.insert('end',log+'\n')
        t.config(state='disabled')

    # 建框架
    frm = ttk.Frame(window)
    frm.pack()

    def button_login():
        if net_test() == 0:
            net_login()
        else:
            pass

    # 创建按钮
    b1 = ttk.Button(frm, text='连接', width=18, command=button_login)
    b1.pack(side='left', padx=12, pady=10)
    b2 = ttk.Button(frm, text='后台运行', width=18, command=window.withdraw)
    b2.pack(side='right', padx=12, pady=10)
    b3 = ttk.Button(window, text='设置', width=40, command=set_window)
    b3.pack()

    def window_quit():
        answer = mBox.askyesno('退出', '是否要最小化到系统托盘')
        if answer:
            window.withdraw()
        else:
            quit()
    
    window.protocol('WM_DELETE_WINDOW', window_quit)
    
# 设置窗口
def set_window():
    window_setinfo = tk.Toplevel(window)
    w = 300
    h = 350
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window_setinfo.geometry('%dx%d+%d+%d' % (w, h, x, y))
    window_setinfo.title('设置')
    window_setinfo.iconbitmap(njtechico)

    frm1 = ttk.Frame(window_setinfo)
    frm1.pack(pady=20)
    frm2 = ttk.Frame(window_setinfo)
    frm2.pack()
    frm3 = ttk.Frame(window_setinfo)
    frm3.pack(pady=20)

    frm_checkbutton0 = tk.Frame(window_setinfo)
    frm_checkbutton0.pack()
    frm4 = ttk.Frame(frm_checkbutton0)
    frm4.pack(side='left')
    frm5 = ttk.Frame(frm_checkbutton0)
    frm5.pack(side='right')

    frm_checkbutton1 = tk.Frame(window_setinfo)
    frm_checkbutton1.pack()
    frm6 = ttk.Frame(frm_checkbutton1)
    frm6.pack(side='left')
    frm7 = ttk.Frame(frm_checkbutton1)
    frm7.pack(side='right')


    namebox = tk.StringVar()
    namebox.set(usr['usrname'])
    pswbox = tk.StringVar()
    pswbox.set(usr['password'])

    e1 = ttk.Entry(frm1, textvariable=namebox)
    e1.pack(side='right')
    e2 = ttk.Entry(frm2,show='*', textvariable=pswbox)
    e2.pack(side='right')

    # 下拉选单
    channel_list = ['中国移动','中国电信','校园内网']
    channelshow = tk.StringVar()
    ChannelChosen = ttk.Combobox(frm3, width=18, textvariable=channelshow, state='readonly')
    ChannelChosen['values'] = channel_list
    ChannelChosen.pack(side='right')
    if usr['channelshow'] != '':
        ChannelChosen.current(channel_list.index(usr['channelshow']))

    l1 = tk.Label(frm1, text='账号：')
    l1.pack(side='left')
    l2 = tk.Label(frm2, text='密码：')
    l2.pack(side='left')
    l3 = tk.Label(frm3, text='网络：')
    l3.pack(side='left')
    l4 = tk.Label(frm4, text='防掉线')
    l4.pack(side='left')
    l5 = tk.Label(frm5, text='自动登录')
    l5.pack(side='left')
    l6 = tk.Label(frm6, text='开机启动')
    l6.pack(side='left')
    l7 = tk.Label(frm7, text='自动隐藏')
    l7.pack(side='left')

    # 创建 CheckButton
    var1 = tk.IntVar() # 防掉线
    var2 = tk.IntVar() # 自动登录
    var1.set(usr['stayonline'])
    var2.set(usr['autologin'])

    var3 = tk.IntVar() # 开机启动
    var4 = tk.IntVar() # 自动隐藏
    var3.set(usr['startup'])
    var4.set(usr['autowithdraw'])

    c1 = tk.Checkbutton(frm4, variable=var1, onvalue=1, offvalue=0)
    c1.pack(side='right')
    c2 = tk.Checkbutton(frm5, variable=var2, onvalue=1, offvalue=0)
    c2.pack(side='right')

    c3 = tk.Checkbutton(frm6, variable=var3, onvalue=1, offvalue=0)
    c3.pack(side='right')
    c4 = tk.Checkbutton(frm7, variable=var4, onvalue=1, offvalue=0)
    c4.pack(side='right')

    # 创建确定按钮
    def save():
        channel_dict = {	'中国移动':'@cmcc',
        					'中国电信':'@telecom',
        					'校园内网':'default'}
        usr_dict = {'usrname':e1.get(),
                    'password':e2.get(),
                    'channelshow':channelshow.get(),
                    'channel':channel_dict[channelshow.get()],
                    'stayonline':var1.get(),
                    'autologin':var2.get(),
                    'startup':var3.get(),
                    'autowithdraw':var4.get()}
        usr_set(usr_dict)
        usr_read()

        start_up()

        namebox.get()
        pswbox.get()
    
    b = ttk.Button(window_setinfo, text='保存', width=18, command=save)
    b.pack(pady=15)

# 最小化 使用时请将 winico0.6 文件夹放置在python安装目录的 tcl 文件夹下
def tray():
    def menu_func(event,x,y):
        if event == 'WM_RBUTTONDOWN':    # 监听右击事件
            menu.tk_popup(x,y) # 弹出菜单
        if event == 'WM_LBUTTONDOWN':    # 监听右击事件
            window.deiconify() # 显示主页面

    window.tk.call('package', 'require', 'Winico')
    global icon
    icon = window.tk.call('winico', 'createfrom', njtechico)
    window.tk.call('winico', 'taskbar', 'add', icon,
                '-callback', (window.register(menu_func), '%m', '%x', '%y'),
                '-pos', 0,
                '-text', u'南京工业大学网络助手')

    def about():
        mBox.showinfo(title='关于', message=    '本软件非南京工业大学官方制作，仅供参考学习\n\n'+
                                                '请使用者认真鉴别软件的来源是否可靠再进行使用\n\n'+
                                                '有任何疑问或者bug，欢迎联系作者\n'+
                                                '邮箱：im.joeychan@outlook.com')

    menu = tk.Menu(window, tearoff=0)
    menu.add_command(label=u'显示主页面', command=window.deiconify)
    menu.add_command(label=u'设置', command=set_window)
    menu.add_command(label=u'关于', command=about)
    menu.add_command(label=u'退出', command=quit)

if __name__ == '__main__':

    njtechico = resource_path('njtechico.ico')    
    usr_read()
    main_window()
    tray()

    if usr['autologin']:
        threading.Thread(target=auto_login, daemon=True).start()
    if usr['stayonline']:
        threading.Thread(target=stay_online, daemon=True).start()
    window.mainloop()

