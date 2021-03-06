import pymysql
db_conn = pymysql.connect("localhost","root","hitsz180110718","test0")
cursor = db_conn.cursor()

import socket
HOST = '172.17.170.11'
#HOST = '10.249.93.167'
#HOST = '10.250.151.171'
PORT = 7000
#PORT = 65432

def socket_verify(string, conn):
    data = conn.recv(1024)
    data = str(data, 'utf-8')
    if(data == string):
        return 1
    else:
        return 0
    
def socket_send(string, conn):
    mssg = string
    conn.sendall(bytes(mssg,encoding='utf-8'))
    return 1

def socket_receive(conn):
    data = conn.recv(1024)
    data = str(data, 'utf-8')
    return data

while(True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((HOST,PORT))
    s.listen()
    sock_conn,addr = s.accept()

    sock_conn.sendall(bytes('helloclient','utf-8'))

    work = True
    while(work):
        command = str(sock_conn.recv(1024),'utf-8')



        if command == 'signup':
            #register
            print("registering...")
            sock_conn.sendall(bytes('triggered_signup',encoding='utf-8'))
            #reg info
            user_name = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_username',encoding='utf-8'))
            password = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_password',encoding='utf-8'))
            ip_address = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_ip',encoding='utf-8'))

            sql = ("SELECT * FROM login_info WHERE user_name='%s'" %(user_name))
            cursor.execute(sql)
            if(cursor.rowcount):
                sock_conn.sendall(bytes('duplicated',encoding='utf-8'))
                continue
            else:
                sql = ("INSERT INTO login_info(user_name,password,ip_address)VALUES('%s','%s','%s')" %\
                        (user_name,password,ip_address))
                #数据库插入用户注册信息
                try:
                    cursor.execute(sql)
                    db_conn.commit()
                except:
                    db_conn.rollback()
                sock_conn.sendall(bytes('stored',encoding='utf-8'))



        elif command == 'login':
            print("logging...")
            #login
            sock_conn.sendall(bytes('triggered_login',encoding='utf-8'))
            #log_info
            user_name = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_username',encoding='utf-8'))
            password = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_password',encoding='utf-8'))
            ip_address = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_ip',encoding='utf-8'))
            print("sqling")

            sql = ("SELECT * FROM login_info WHERE user_name='%s' AND password='%s'" %\
                    (user_name,password))
            cursor.execute(sql)
            if(cursor.rowcount):
                sock_conn.sendall(bytes('success',encoding='utf-8'))
                sql = ("UPDATE login_info SET ip_address='%s' WHERE user_name='%s'" %\
                        (ip_address,user_name))
                try:
                    cursor.execute(sql)
                    db_conn.commit()
                except:
                    db_conn.rollback()
            else:
                sock_conn.sendall(bytes('wrong',encoding='utf-8'))



        elif command == 'upload':
            print("uploading...")
            #uploading the file information
            sock_conn.sendall(bytes('triggered_upload',encoding='utf-8'))
            #file_info
            file_name = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_filename',encoding='utf-8'))
            file_size = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_filesize',encoding='utf-8'))
            uploader  = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_uploader',encoding='utf-8'))
            sharetime = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_time',encoding='utf-8'))
            category  = str(sock_conn.recv(1024),'utf-8')
            sock_conn.sendall(bytes('got_category',encoding='utf8'))

            sql = ("INSERT INTO file_info\
                    (file_name,file_size,uploader,sharetime,category)\
                    VALUES('%s','%s','%s','%s','%s')" % \
                    (file_name,file_size,uploader,sharetime,category))
            print(sql)
            #数据库插入用户注册信息
            try:
                cursor.execute(sql)
                db_conn.commit()
            except:
                print('upload error')
                db_conn.rollback()
            sock_conn.sendall(bytes('uploaded',encoding='utf-8'))


        elif command == 'get_index':
            print("indexing...")
            # SQL 查询语句
            sql = "SELECT * FROM file_info;"
            try:
                # 执行SQL语句
                cursor.execute(sql)
            except:
                print("Error: unable to fetch data")
            print(cursor.rowcount)

            # 获取所有记录列表
            sock_conn.sendall(bytes(str(cursor.rowcount),encoding='utf-8'))
            results = cursor.fetchall()
            for row in results:
                # 发给客户机
                socket_verify('ready',sock_conn)
                row_str = []
                for item in row:
                    print(type(item))
                    row_str.append(str(item))
                line = '\t'.join(row_str)
                print(line)
                socket_send(line,sock_conn)


        elif command == 'get_path':
            socket_send('get_path_triggered',sock_conn)
            ID = socket_receive(sock_conn)

            sql = ("SELECT uploader FROM file_info WHERE file_id = %d" % (int(ID)))
            try:
                # 执行SQL语句
                cursor.execute(sql)
            except:
                print("Error: unable to fetch data")
            uploader = cursor.fetchone()
            print(uploader)
            uploader = uploader[0]

            sql2 = ("SELECT ip_address FROM login_info WHERE user_name='%s'" % (uploader))
            try:
                # 执行SQL语句
                cursor.execute(sql2)
            except:
                print("Error: unable to fetch data")
            path = cursor.fetchone()
            print(path)
            path = path[0]
            print(path)
            socket_send(path,sock_conn)


        elif command == 'search':
            print("Searching")
            socket_send('search_triggered',sock_conn)

            ID = socket_receive(sock_conn)
            sql = ("SELECT file_name from file_info WHERE file_id = %s" % ID)
            cursor.execute(sql)
            if(cursor.rowcount):
                file_name = cursor.fetchone()
                print(file_name)
                file_name = file_name[0]
                socket_send(file_name,sock_conn)
            else:
                socket_send('^^^',sock_conn)

        elif command == 'remove':
            print('removing')
            socket_send('remove_triggered',sock_conn)

            ID = socket_receive(sock_conn)
            sql = ("SELECT * from file_info WHERE file_id = %s" % ID)
            cursor.execute(sql)
            if(cursor.rowcount):
                sql2 = ("DELETE FROM file_info WHERE file_id = %s" % ID)
                # 执行SQL语句
                cursor.execute(sql2)
                db_conn.commit()
                socket_send('is_removed',sock_conn)
            else:
                socket_send('not_found',sock_conn)


        elif command == 'connect_close':
            work = 0
            sock_conn.sendall(bytes('closing',encoding='utf-8'))
            s.close()    

        else:
            print("Error detected.")
            break
