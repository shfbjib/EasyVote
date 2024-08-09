import socket,struct,random,sqlite3
from datetime import datetime,timedelta
from getCurrentTime import *
from  encryption_decryption import *

def sendData(message_str):
    '''
    此函数可以实现发送加密后数据的功能
    :param message_str:未加密的数据
    '''
    cipher=selfmade_encryption(message_str.encode())  # 对明文进行加密
    header = struct.pack('i', len(cipher))  # 打包为二进制数据
    channel.sendall(header)  # 发送密文长度的数据包
    channel.sendall(cipher)  # 发送密文数据
def recv_data():
    '''
    此函数可以实现接受密文并解密成明文的功能
    :return: 解密得到的明文字符串
    '''
    Header = channel.recv(4)  # 接收密文长度的数据包
    Len = struct.unpack('i', Header)[0]  # 解二进制数据包
    received_data_bytes = channel.recv(Len)  # 接收密文数据
    received_data=selfmade_decryption(received_data_bytes)  # 解密得到明文
    return received_data
def createNewRoom():
    '''
    此函数实现服务器端在数据库中创建一个新投票房间
    '''
    nums = random.sample(range(10000000, 99999999),1)[0] # 随机生成一个不重复的八位数
    theme,candidateList,votingTime=None,None,None  # 创建存储投票房间数据的变量
    votes=''
    for i in range(3):  # 依次读取投票活动简介、候选人名单、投票时长的数据
        data=recv_data()
        if i==0:  # 读取投票活动简介
            theme=data
        elif i==1:  # 读取候选人名单
            candidateList=data
            for i in range(len(data.split(' '))):  # 计算候选人数目，并初始化与之对应的0票数
                votes+='0 '
        else:  # 读取投票时长
            votingTime=data
    # 在数据库中插入当前投票房间的数据
    database.execute("INSERT INTO users (nums, theme,candidateList,votes,votingTime) VALUES (?, ?, ?, ?, ?)",
                     (nums,theme, candidateList,votes,votingTime))
    database.commit()  # 确认提交对数据库的修改
    sendData(str(nums))  # 给客户端发送新创建投票房间的号码
def enterRightRooms():
    '''
    此函数实现进入与房间号匹配的投票间以及处理房间号不存在的异常情况
    '''
    data = int(recv_data())  # 接收客户端发来的投票房间号
    cursor_temp=database.execute("SELECT * FROM users WHERE nums = ?", (data,))  # 查询数据库中房间号匹配的数据
    dataList=cursor_temp.fetchall()  # 获取查询到的记录
    if len(dataList)==0:  # 判断数据库中是否存在此房间号的信息
        sendData('No')  # 向客户端发送No答复
    else:
        room_information=str(dataList).strip('[]')  # 处理得到投票房间信息的字符串
        sendData(room_information)  # 向客户端发送该投票房间的数据
def updateSQL():
    '''
    此函数可以实现更新投票房间数据库和用户信息数据库的功能，并实现每人在同一个房间内只能投一票的检验
    '''
    new_votes = recv_data()  # 接收更新后的票数数据
    numbers=recv_data()  # 接收客户端发来的投票房间号
    user_account=recv_data()  # 接收客户端发来的账号
    user_password=recv_data()  # 接收客户端发来的密码
    # 从数据库中查询是否存在匹配的数据项
    cursor_temp = database2.execute("SELECT * FROM users2 WHERE account = ? AND password = ?", (user_account, user_password))
    info_list = cursor_temp.fetchall()  # 获取全部的匹配项
    voted_nums_list=info_list[0][3].split(" ")  # 将获取到的已投票的房间号逐个存入列表中
    for i in range(len(voted_nums_list)):  # 遍历每一个已投票的房间号
        if voted_nums_list[i]==numbers:  # 判断当前要投票的房间号是否在列表中
            sendData('No')  # 如果有，则拒绝投票请求，告知客户端
            return
    sendData('Yes')  # 通过筛查，允许此次投票，告知客户端
    numb=info_list[0][3]+' '+numbers  # 将当前房间号添加到已投票的房间信息中
    database.execute("UPDATE users SET votes = ? WHERE nums = ?", (new_votes, numbers))  # 更新数据库中对应房间的票数
    database.commit()  # 确认提交对数据库的修改
    database2.execute("UPDATE users2 SET nums = ? WHERE account = ? AND password = ?", (numb, user_account, user_password))  # 更新用户已投票的房间号数据
    database2.commit()  # 确认提交对数据库的修改
def loginAccounts():
    '''
    此函数可以实现服务器对客户端登录进行检验的功能
    '''
    account_=recv_data()  # 接收账号
    password_=recv_data()  # 接收密码
    # 从数据库中查询是否存在匹配的数据项
    cursor_temp = database2.execute("SELECT * FROM users2 WHERE account = ? AND password = ?", (account_,password_))
    info_list=cursor_temp.fetchall()  # 获取全部的匹配项
    if info_list==[]:  # 如果该用户信息不在数据库中
        sendData('No')  # 发送登录失败的消息
    else:
        sendData('Yes')  # 发送登录成功的消息
def clearExpiredData():
    '''
    此函数来实现清除超过投票截止日期3天的数据记录，自动维护数据库
    '''
    Time=curr_time()  # 获取当前时间
    cursor.execute('SELECT * FROM users')  # 查询全部数据
    datalist = cursor.fetchall()  # 得到全部数据的列表
    for i in range(len(datalist)):  # 手动遍历数据
        deadline_time_list=datalist[i][5].split(" ")  # 将每个房间的投票截止时间转换成列表来存储
        for j in range(len(deadline_time_list)):  # 将年月日时分信息转换成整型
            deadline_time_list[j]=int(deadline_time_list[j])
        # 创建投票截止时间对象
        deadline_time = datetime(deadline_time_list[0],deadline_time_list[1],deadline_time_list[2],deadline_time_list[3],deadline_time_list[4],0)
        deadline = deadline_time + timedelta(days=3)  # 额外保留过期房间信息3天
        if deadline<Time:  # 判断房间信息是否超过截止日期3天
            database.execute("DELETE FROM users WHERE votingTime = ?", (datalist[i][5],))  # 删除超过截止日期3天的数据
            database.commit()  # 确认提交对数据库的修改

soc=socket.socket()  # 创建socket套接字对象
soc.bind(('127.0.0.1',10169))  # 绑定服务器主机和端口
soc.listen(10000)  # 设置允许同时访问服务器的最大人数

database = sqlite3.connect('database.db')  # 创建投票房间数据库
cursor = database.cursor()  # 生成数据库的游标
# 创建数据库里的数据项
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        nums INTEGER,
        theme TEXT NOT NULL,
        candidateList TEXT NOT NULL,
        votes TEXT NOT NULL,
        votingTime TEXT NOT NULL
    )
''')
database.commit()  # 确认提交对数据库的修改

database2 = sqlite3.connect('database2.db')  # 创建用户信息数据库
cursor2 = database2.cursor()  # 生成数据库的游标
# 创建数据库里的数据项
cursor2.execute('''
    CREATE TABLE IF NOT EXISTS users2 (
        id INTEGER PRIMARY KEY,
        account TEXT NOT NULL,
        password TEXT NOT NULL,
        nums TEXT NOT NULL
    )
''')
database2.commit()  # 确认提交对数据库的修改

channel,address=soc.accept()  # 等待并接受客户端的连接
while True:  # 确保服务器不会主动停止运行
    clearExpiredData()  # 先检查是否需要清理过期数据
    data0=recv_data()  # 接受客户端发来的数据
    if data0=='|':  # 如果收到'|'，表示客户端要创建一个新的投票房间
        createNewRoom()
    elif data0=='||':  # 如果收到'||'，表示客户端要进入房间号对应的投票房间
        enterRightRooms()
    elif data0=='|||':  # 如果收到'|||'，表示要更新数据库中投票房间的信息
        updateSQL()
    elif data0=='||||':  # 如果收到'||||'，表示要处理登录请求
        loginAccounts()
