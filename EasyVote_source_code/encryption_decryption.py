from base64 import *
def selfmade_encryption(plaintext_bytes):
    '''
    此函数可以实现加密明文的功能
    :param plaintext_bytes:明文(bytes类型)
    :return:加密得到的密文(bytes类型)
    '''
    b64_plaintext_bytes=b64encode(plaintext_bytes)  # 对明文进行base64编码
    b64_plaintext_str=str(b64_plaintext_bytes).strip("b'")  # 将编码后的字节对象转换成字符串
    b64_plaintext_list=list(b64_plaintext_str)  # 将字符串的每个字符作为列表的一个元素，方便后续处理
    # 对编码后的数据进行加密
    counts=b64_plaintext_list.count('=')  # 计算“=”出现次数
    if counts==0:
        b64_plaintext_list.append('=')  # 在明文后面添加“=”
        b64_plaintext_list.append('=')
    else:
        b64_plaintext_list.pop(-1)  # 在明文后面删除“=”
    for i in range(len(b64_plaintext_list)):  # 遍历数据中每一个字符
        if i%3==1:
            if b64_plaintext_list[i]=='=':  # 跳过“=”号
                continue
            elif ord(b64_plaintext_list[i])>=48 and ord(b64_plaintext_list[i])<=57:  # 对数字移位
                b64_plaintext_list[i]=chr((ord(b64_plaintext_list[i])-44)%10+48)  # 循环向右移动4位
            elif ord(b64_plaintext_list[i])>=65 and ord(b64_plaintext_list[i])<=90:  # 对大写字母移位
                b64_plaintext_list[i] = chr((ord(b64_plaintext_list[i]) -60) % 26 + 65)  # 循环向右移动5位
            elif ord(b64_plaintext_list[i]) >= 97 and ord(b64_plaintext_list[i]) <= 122:  # 对小写字母移位
                b64_plaintext_list[i] = chr((ord(b64_plaintext_list[i]) -90) % 26 + 97)  # 循环向右移动7位
    b64_ciphertext_bytes=''.join(b64_plaintext_list).encode()  # 将加密后的所有字符拼成字节对象
    return b64_ciphertext_bytes
def selfmade_decryption(ciphertext_bytes):
    '''
    此函数可以说实现解密的功能
    :param ciphertext_bytes:密文(bytes类型)
    :return:解密得到的明文(str类型)
    '''
    ciphertext_list=list(str(ciphertext_bytes).strip("b'"))  # 将字节对象逐个字符进行拆分
    for i in range(len(ciphertext_list)):
        if i%3==1:
            if ciphertext_list[i]=='=':  # 跳过“=”号
                continue
            elif ord(ciphertext_list[i])>=48 and ord(ciphertext_list[i])<=57:  # 对数字复位
                ciphertext_list[i]=chr((ord(ciphertext_list[i])-42)%10+48)  # 循环向左移动4位
            elif ord(ciphertext_list[i])>=65 and ord(ciphertext_list[i])<=90:  # 对大写字母复位
                ciphertext_list[i] = chr((ord(ciphertext_list[i]) -44) % 26 + 65)  # 循环向左移动5位
            elif ord(ciphertext_list[i]) >= 97 and ord(ciphertext_list[i]) <= 122:  # 对小写字母复位
                ciphertext_list[i] = chr((ord(ciphertext_list[i]) -78) % 26 + 97)  # 循环向左移动7位
    counts = ciphertext_list.count('=')  # 计算“=”出现次数
    if counts == 2:
        ciphertext_list.pop(-1)  # 删除密文最后的“=”号
        ciphertext_list.pop(-1)
    else:
        ciphertext_list.append('=')  # 在密文最后添加“=”号
    ciphertext_str=''.join(ciphertext_list)  # 将密文拼接成字符串类型
    plaintext_str=b64decode(ciphertext_str.encode()).decode()  # 解码得到明文
    return plaintext_str