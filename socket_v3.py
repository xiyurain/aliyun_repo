import pymysql
db_conn = pymysql.connect("localhost","root","hitsz180110718","test0")
cursor = db_conn.cursor()

import socket
HOST = '172.17.170.11'
#HOST = '10.249.93.167'
PORT = 7000
#PORT = 65432

while(True):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                sql = ("INSERT INTO login_info(user_name,password,ip_address)VALUES('%s','%s','%s')" % (user_name,password,ip_address))
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

            sql = ("SELECT * FROM login_info WHERE user_name='%s' AND password='%s'" %(user_name,password))
            cursor.execute(sql)
            if(cursor.rowcount):
                sock_conn.sendall(bytes('success',encoding='utf-8'))
                sql = ("UPDATE login_info SET ip_address='%s' WHERE user_name='%s'" % (ip_address,user_name))
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
            
            sql = ("INSERT INTO file_info(file_name,file_size,uploader,sharetime)VALUES('%s','%s','%s','%s')" % (file_name,file_size,uploader,sharetime))
            #数据库插入用户注册信息
            try:
                cursor.execute(sql)
                db_conn.commit()
            except:
                db_conn.rollback()
            sock_conn.sendall(bytes('uploaded',encoding='utf-8'))
            
            
            
        elif command == 'connect_close':
            work = 0
            s.close()
            sock_conn.sendall(bytes('closing',encoding='utf-8'))
            
            
        else:
            print("Error detected.")
            break