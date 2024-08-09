import sqlite3
def importUserInfo(filepath):
    '''
    此函数可以实现向用户信息数据库导入合法用户信息的功能
    :param filepath:存有合法用户信息的txt文件
    '''
    try:
        with open(filepath,mode='r') as f:  # 读取文件
            userInfo_list=f.readlines()  # 用列表存储合法用户信息
            if userInfo_list==[]:  # 文件为空则停止
                return
            else:
                for i in range(len(userInfo_list)):
                    userInfo_list[i]=userInfo_list[i].split(' ')  # 将每一个用户的账号和密码拆开
                    # 在数据库中插入数据
                    database2.execute("INSERT INTO users2 (account, password, nums) VALUES (?, ?, ?)", (userInfo_list[i][0],userInfo_list[i][1],''))
                    database2.commit()  # 确认提交对数据库的修改
    except:
        print('文件不存在或格式不正确！')

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
file=input('请输入包含待导入数据的txt文件路径：')  # 输入要导入的文件路径
file=file.strip('"').replace('\\',"\\\\")  # 对文件路径进行处理
importUserInfo(file)  # 导入用户信息
