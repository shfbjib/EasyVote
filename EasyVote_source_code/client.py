from tkinter import *
from tkinter import messagebox
import socket,struct,os,sys
import matplotlib.pyplot as plt
from getCurrentTime import *
from  encryption_decryption import *

client=socket.socket()  # 创建socket套接字对象
client.connect(('127.0.0.1',10169))  # 建立与服务器的连接
def sendData(message_str):
    '''
    此函数可以实现发送加密后的密文数据的功能
    :param message_str:明文(str类型)
    '''
    cipher=selfmade_encryption(message_str.encode())  # 加密得到密文
    header = struct.pack('i', len(cipher))  # 打包为二进制数据
    client.sendall(header)  # 发送密文长度的数据包
    client.sendall(cipher)  # 发送密文数据
def recv_data():
    '''
    此函数可以实现接收密文并解密的功能
    :return:解密得到的明文(str类型)
    '''
    Header = client.recv(4)  # 接收密文长度的数据包
    Len = struct.unpack('i', Header)[0]  # 解二进制数据包
    received_data_bytes = client.recv(Len)  # 接收密文数据
    received_data=selfmade_decryption(received_data_bytes)  # 解密得到明文
    return received_data
def loginAccounts(account,password):
    '''
    此函数可以实现客户端处理用户请求登录的功能
    :param account:用户输入的账号(str类型)
    :param password:用户输入的密码(str类型)
    '''
    sendData('||||')  # 发送指令数据
    sendData(account)  # 发送用户输入的账号
    sendData(password)  # 发送用户输入的密码
    response=recv_data()  # 接收来自服务器的响应信息
    if response=='No':
        messagebox.showerror(title='error', message='抱歉，您的账号不在系统中！')  # 登录失败
    else:
        enter_room()  # 登录成功，进入输入投票房间号的窗口
def createVotingRoomWindow(room_information,para=0):
    '''
    此函数可以实现弹出已创建投票房间信息的窗口的功能，也可以在查看当前票数时弹出包含票数的窗口
    :param room_information:投票房间信息
    :param para:用来区分 弹出已创建投票房间信息的窗口 还是 在查看当前票数时弹出包含票数的窗口
    '''
    def vote(votes_number_list,date,number,i,j):
        '''
        此函数可以实现客户端处理投票请求的功能
        :param votes_number_list: 当前票数列表
        :param date: 投票截止时间
        :param number: 投票房间号
        :param i: 确定点击的按钮位置的参数(横)
        :param j: 确定点击的按钮位置的参数(竖)
        '''
        Time=curr_time()  # 获取当前时间
        for l in range(len(date)):  # 将年月日时分信息转换成整型
            date[l] = int(date[l])
        deadline_time = datetime(date[0], date[1], date[2],date[3], date[4], 0)  # 创建datatime的实例化对象
        login_window.withdraw()  # 隐藏登录窗口
        if Time<deadline_time:  # 判断当前时间是否超过投票截止时间
            votes_number_list[5*i+j]=str(int(votes_number_list[5*i+j])+1)
            votes_number_str=' '.join(votes_number_list)  # 客户端先更新票数
            sendData('|||')  # 发送指令数据
            sendData(votes_number_str)  # 发送票数数据
            sendData(number)  # 发送投票房间号
            sendData(account_entry.get())  # 发送当前用户账号
            sendData(passowrd_entry.get())  # 发送当前用户密码
            res=recv_data()  # 接收服务器端的响应信号
            if res=='No':
                messagebox.showerror(title='error', message='您已投票，请勿重复投票！')  # 弹出请勿重复投票的提示
            else:
                messagebox.showinfo(title='提示', message='投票成功，感谢您的参与！')  # 弹出投票成功的提示信息
        else:
            messagebox.showerror(title='error', message='抱歉，投票已截止，无法继续投票！')  # 弹出超时信息
    def saveCurrentResult(room_information):
        '''
        此函数可以实现保存当前投票结果的功能
        :param room_information: 当前投票房间信息
        '''
        if not os.path.exists('saved_files'):  # 判断当前路径是否存在saved_files
            os.mkdir('saved_files')  # 如果不存在，则创建saved_files
        if not os.path.exists('saved_files\\'+room_information[1]):  # 判断当前路径是否存在当前房间号的文件夹
            os.mkdir('saved_files\\'+room_information[1])  # 如果不存在，则创建一个以当前房间号为名称的文件夹
        # 将投票结果写入txt文本中，保存原生数据
        with open('saved_files\\'+room_information[1]+'\\'+room_information[1]+'_data.txt',mode='w') as f:
            for i in range(n):
                f.write(candidate[i]+' '+votes_number_list[i]+'票'+'\n')
        # 将投票结果用柱状图保存
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为SimHei以支持中文
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        temp=[]
        for j in range(len(votes_number_list)):
            temp.append(int(votes_number_list[j]))  # 处理票数数据
        plt.figure(figsize=(12, 8))  # 设置饼状图大小
        plt.bar(candidate,temp)  # 创建带有数据的柱状图
        plt.title('投票结果')  # 添加柱状图标题
        plt.xlabel('候选人')  # 设置x轴标签
        plt.ylabel('票数')  # 设置y轴标签
        plt.savefig('saved_files\\'+room_information[1]+'\\'+room_information[1]+'_bar_graph.png')  # 保存画完的柱状图
        # 将投票结果用饼状图保存
        for k in range(len(temp)):  # 遍历每一个候选人的票数
            if not temp[k]==0:  # 判断票数是否为0，只要有不为0的票数，则进行绘制饼状图，否则跳过
                plt.figure(figsize=(6, 6))  # 设置饼状图大小
                plt.pie(temp, labels=candidate, autopct='%1.1f%%', startangle=90)  # 创建饼状图
                plt.title('投票结果(单位：票数)')  # 添加饼状图标题
                plt.savefig('saved_files\\'+room_information[1]+'\\'+room_information[1]+'_pie_chart.png')  # 保存画完的饼状图
                break
        messagebox.showinfo(title='提示', message='保存成功，请到当前目录下saved_files文件夹查看投票结果！')  # 弹出保存成功的提示

    voteRoom = Tk()  # 创建新投票房间
    voteRoom.title('易投票')  # 设置窗口的标题
    voteRoom.geometry('800x600')  # 设置窗口大小
    voteRoom.resizable(False, False)  # 固定窗口大小
    voteRoom.configure(bg='white')  # 设置背景颜色
    voteRoom.iconbitmap('Icon.ico')  # 设置窗口的图标
    # 处理投票房间的信息
    room_information=room_information.replace("'","")
    room_information=room_information.strip('()').split(", ")
    # 获取投票房间的截止时间
    date=room_information[5].split(" ")
    if int(date[4])<10 and int(date[4])>=0:
        date[4]='0'+date[4]  # 补充空位，让截止时间的格式更符合人的认知
    date=date[0]+'年'+date[1]+'月'+date[2]+'日'+date[3]+':'+date[4]  # 拼接成可读的字符串
    # 处理候选人的信息
    candidate=room_information[3].split(" ")
    n=len(candidate)  # 获取候选人数目
    k=0
    # 处理候选人票数的数据
    votes_number_list=room_information[4].strip(" ").split(" ")
    for i in range(4):
        for j in range(5):
            if k<n:
                Label(voteRoom, text=candidate[k], fg='black', bg='white',font='宋体 14').place(x=60+j*150, y=130+i*120)  # 添加候选人姓名的标签
                if para==1:
                    # 额外添加各个候选人的票数
                    Label(voteRoom, text=votes_number_list[k]+' 票', fg='black', bg='white', font='宋体 10').place(x=65 + j * 150,y=160 + i * 120)
                    save_button = Button(voteRoom, text='一键保存',command=lambda:saveCurrentResult(room_information),fg='black', bg='lightgrey',font='宋体 14')
                    save_button.place(x=630, y=75)  # 添加一键保存的按钮
                    k+=1
                    continue
                k+=1
                # 添加投票按钮
                vote_button = Button(voteRoom, text='投票',command=lambda m=i,n=j:vote(votes_number_list,room_information[5].split(" "),
                                                                room_information[1],m,n), fg='black', bg='lightgrey',font='宋体 14 bold')
                vote_button.place(x=60+j*150, y=130+i*120+30)
            else:
                break
    # 添加投票活动主题和投票截止时间的标签
    Label(voteRoom, text='  '+'活动主题：'+room_information[2], fg='black', bg='white', anchor='w', justify='left',
          font='宋体 16 bold',wraplength=790).place(x=10, y=20)
    Label(voteRoom, text='  ' + '投票截止时间：' + date, fg='black', bg='white', anchor='w', justify='left',
          font='宋体 16 bold', wraplength=790).place(x=10, y=80)
    if para==0:
        # 额外添加查看当前票数的按钮
        update_button = Button(voteRoom, text='查看当前票数',command=lambda:enterRightRooms(room_information[1],1),fg='black', bg='lightgrey', font='宋体 14')
        update_button.place(x=630, y=75)
    voteRoom.mainloop()  # 显示窗口并响应用户请求
def enterRightRooms(vote_room_str,para=0):
    '''
    此函数来获取输入文本框内的文本，在数据库中查找该投票房间号，并进入对应的投票房间
    '''
    nums=vote_room_str  # 获取文本框中输入的投票房间号
    if nums=='':  # 如果未输入内容，则原地等待
        return
    sendData('||')  # 发送指令数据
    sendData(nums)  # 发送投票房间号
    room_information=recv_data()  # 接收投票房间信息
    if room_information=='No':  # 判断当前房间号是否存在
        messagebox.showerror(title='error', message='您输入的投票房间号异常！')  # 弹出错误窗口
        return
    else:
        if para==0:  # 如果para为0，则正常创建新投票房间
            createVotingRoomWindow(room_information)
        elif para==1:  # 如果para为1，则弹出在查看当前票数时包含候选人票数的窗口
            createVotingRoomWindow(room_information,1)
def createNewRoom():
    '''
    此函数实现创建一个新的投票房间，并将其包含的关键信息存入数据库中
    '''
    def backto_loginWindow():
        newVoteRoom.destroy()  # 关闭注册新投票房间的窗口
    def sendMessage():
        '''
        此函数可以实现提取并发送输入的投票房间信息的功能
        '''
        theme=vote_room_name_entry.get()  # 获取投票活动简介
        candidateList=candidate_entry.get()  # 获取候选人名单
        votingTime=voting_time_entry.get()  # 获取投票时间
        if theme=='' or candidateList=='' or votingTime=='':  # 判断三个选项是否有空
            messagebox.showerror(title='error',message='所有选项均不能为空！')  # 提醒用户输入完整
            return
        votingTime__list=votingTime.split(' ')  # 分割投票截止时间
        if not len(votingTime__list)==5 :
            messagebox.showerror(title='error', message='您输入的投票截止时间格式不正确！')  # 弹出报错信息
            return
        year__=int(votingTime__list[0])  # 保存投票截止时间的年份
        month__=int(votingTime__list[1])  # 保存投票截止时间的月份
        day__=int(votingTime__list[2])  # 保存投票截止时间的日期
        hour__=int(votingTime__list[3])  # 保存投票截止时间的小时
        minute__=int(votingTime__list[4])  # 保存投票截止时间的分钟
        # 检查年份输入是否合法
        if not (year__>=1 and year__<=9999):
            messagebox.showerror(title='error', message='投票截止时间的年份必须在1-9999之间！')
            return
        # 检查月份输入是否合法
        if not (month__>=1 and month__<=12):
            messagebox.showerror(title='error', message='投票截止时间的月份必须在1-12之间！')
            return
        # 检查日期输入是否合法
        if (year__%4==0 and not year__%100==0) or year__%400==0:  # 判断输入的年份是否为闰年
            dic={1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
            if not (day__ >= 1 and day__ <= dic[month__]):
                messagebox.showerror(title='error', message=f'投票截止时间的日期必须在1-{dic[month__]}之间！')
                return
        else:
            dic = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
            if not (day__ >= 1 and day__ <= dic[month__]):
                messagebox.showerror(title='error', message=f'投票截止时间的日期必须在1-{dic[month__]}之间！')
                return
        # 检查小时输入是否合法
        if not (hour__ >= 0 and hour__ <= 23):
            messagebox.showerror(title='error', message='投票截止时间的小时必须在0-23之间！')
            return
        # 检查分钟输入是否合法
        if not (minute__ >= 0 and minute__ <= 59):
            messagebox.showerror(title='error', message='投票截止时间的分钟必须在0-59之间！')
            return
        sendData('|')  # 发送指令数据
        sendData(theme)  # 发送投票活动主题
        sendData(candidateList)  # 发送候选人名单数据
        sendData(votingTime)  # 发送投票截止时间
        num = recv_data()  # 接收新创建投票房间的号码
        messagebox.showinfo(title='提示', message='投票房间创建成功！房间号为'+str(num)+'，请妥善保管！')  # 显示新创建投票房间号
        backto_loginWindow()  # 关闭注册新投票房间的窗口

    newVoteRoom = Tk()  # 创建新投票房间
    newVoteRoom.title('易投票')  # 设置窗口的标题
    newVoteRoom.geometry('600x380')  # 设置窗口大小
    newVoteRoom.resizable(False, False)  # 固定窗口大小
    newVoteRoom.configure(bg='white')  # 设置背景颜色
    newVoteRoom.iconbitmap('Icon.ico')  # 设置窗口的图标
    # 设置注册页标题的属性
    Label(newVoteRoom, text='注册新投票房间', fg='black', bg='white', anchor='n', font='宋体 26 bold').pack()
    # 设置文本标签的属性
    Label(newVoteRoom, text='投票房间名称：', fg='black', bg='white', font='宋体 16').place(x=10, y=100)
    # 创建投票房间名称输入框并初始化其属性
    vote_room_name_entry = Entry(newVoteRoom, width=40, bg='lightgrey', font='宋体 12 bold')
    vote_room_name_entry.place(x=190, y=105)
    # 设置文本标签的属性
    Label(newVoteRoom, text='所有候选人姓名：', fg='black', bg='white', font='宋体 16').place(x=10, y=135)
    Label(newVoteRoom, text='(以空格隔开)', fg='black', bg='white', font='宋体 11').place(x=12, y=165)
    # 创建候选人姓名输入框并初始化其属性
    candidate_entry = Entry(newVoteRoom, width=40, bg='lightgrey', font='宋体 12 bold')
    candidate_entry.place(x=190, y=140)
    # 设置文本标签的属性
    Label(newVoteRoom, text='投票截止时间：', fg='black', bg='white', font='宋体 16').place(x=10, y=200)
    Label(newVoteRoom, text='(依次输入年月日时分，以空格隔开)', fg='black', bg='white',font='宋体 11').place(x=10, y=230)
    Label(newVoteRoom, text='(示例：2025年1月1日12:00-->2025 1 1 12 0)', fg='black', bg='white', font='宋体 11').place(x=12, y=260)
    # 创建投票时长输入框并初始化其属性
    voting_time_entry = Entry(newVoteRoom, width=20, bg='lightgrey', font='宋体 12 bold')
    voting_time_entry.place(x=270, y=200)
    # 创建提交新投票房间的按钮并初始化其属性
    summitRoom_button = Button(newVoteRoom, text='提交', command=sendMessage,fg='black', bg='lightgrey',
                                     font='宋体 14')
    summitRoom_button.place(x=460, y=300)
    # 创建返回登录页面的按钮并初始化其属性
    cancel_button = Button(newVoteRoom, text='返回',command=backto_loginWindow, fg='black', bg='lightgrey',
                               font='宋体 14')
    cancel_button.place(x=160, y=300)
    newVoteRoom.mainloop()  # 显示窗口并响应用户请求
def enter_room():
    '''
    此函数可以实现输入投票房间号并向服务器发送进入请求的功能
    '''
    enter_window=Tk()  # 创建进入投票房间的窗口
    enter_window.title('易投票')  # 设置窗口的标题
    enter_window.geometry('500x300')  # 设置窗口大小
    enter_window.resizable(False,False)  # 固定窗口大小
    enter_window.configure(bg='white')  # 设置背景颜色
    # 设置标题的属性
    Label(enter_window, text='欢迎使用易投票！',fg='black',bg='white',anchor='n',font='宋体 26 bold').pack()
    enter_window.iconbitmap('Icon.ico')  # 设置窗口的图标
    # 设置文本标签的属性
    Label(enter_window,text='请输入投票房间号：',fg='black',bg='white',font='宋体 20').place(x=10,y=100)
    # 创建单行文本输入框并初始化其属性
    vote_room_entry=Entry(enter_window,width=20,bg='lightgrey',font='宋体 12 bold')
    vote_room_entry.place(x=250,y=105)
    # 创建新建投票房间的按钮并初始化其属性
    createNewRoom_button=Button(enter_window,text='创建投票房间',command=createNewRoom,fg='black',bg='lightgrey',font='宋体 14')
    createNewRoom_button.place(x=40,y=200)
    # 创建提交房间号的按钮并初始化其属性
    summitRoomNumber_button=Button(enter_window,text='提交',command=lambda:enterRightRooms(vote_room_entry.get()),fg='black',bg='lightgrey',font='宋体 14')
    summitRoomNumber_button.place(x=340,y=200)
    enter_window.mainloop()  # 显示窗口并响应用户请求

login_window=Tk()  # 创建登录窗口
login_window.title('易投票')  # 设置窗口的标题
login_window.geometry('500x300')  # 设置窗口大小
login_window.resizable(False,False)  # 固定窗口大小
login_window.configure(bg='white')  # 设置背景颜色
# 设置标题的属性
Label(login_window, text='欢迎使用易投票！',fg='black',bg='white',anchor='n',font='宋体 26 bold').pack()
login_window.iconbitmap('Icon.ico')  # 设置窗口的图标
# 设置文本标签的属性
Label(login_window,text='账号：',fg='black',bg='white',font='宋体 16').place(x=80,y=80)
# 创建单行文本输入框并初始化其属性
account_entry=Entry(login_window,width=20,bg='lightgrey',font='宋体 12 bold')
account_entry.place(x=180,y=85)
# 设置文本标签的属性
Label(login_window,text='密码：',fg='black',bg='white',font='宋体 16').place(x=80,y=130)
# 创建单行文本输入框并初始化其属性
passowrd_entry=Entry(login_window,width=20,bg='lightgrey',font='宋体 12 bold',show='*')
passowrd_entry.place(x=180,y=135)
# 创建新建投票房间的按钮并初始化其属性
quit_button=Button(login_window,text='退出',command=sys.exit,fg='black',bg='lightgrey',font='宋体 14')
quit_button.place(x=150,y=200)
# 创建提交房间号的按钮并初始化其属性
login_button=Button(login_window,text='登录',command=lambda:loginAccounts(account_entry.get(),passowrd_entry.get()),fg='black',bg='lightgrey',font='宋体 14')
login_button.place(x=300,y=200)
login_window.mainloop()  # 显示窗口并响应用户请求
client.close()  # 断开与服务器的连接