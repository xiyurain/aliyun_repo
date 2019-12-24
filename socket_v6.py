import threading
import pymysql
#db_conn = pymysql.connect("localhost","root","rxy0191","test0")
#cursor = db_conn.cursor()

import socket
HOST = '172.17.170.11'
#HOST = '10.249.93.167'
#HOST = '10.250.151.171'
PORT = 7000
#PORT = 65432

def hash_encoding(filename):
    hsh = 0
    x = 0
    for char in filename:
        hsh = (hsh<<4) + ord(char)
        x = hsh&0xf0000000
        if(x != 0):
            hsh = hsh^(x>>24)
            hsh = hsh & ~x  
    return (hsh & 0x7fffffff)

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

class queue:
    lst = []
    def push(self,e):
        self.lst.append(e)
    def pop(self):
        element = self.lst[0]
        self.lst.pop([0])
        return element
    def empty(self):
        if(len(self.lst)):
            return 0
        else:
            return 1
    
#Queue = queue()

class client_connection:
    s = 0
    port = 0
    sock_conn = 0
    addr = 0
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    #s.bind((HOST,PORT))
    #s.listen()
    #sock_conn,addr = s.accept()

    #sock_conn.sendall(bytes('helloclient','utf-8'))

    def __init__(self,order):
        self.port = PORT + order
        self.db_conn = pymysql.connect("localhost","root","hitsz180110718","test0")
        self.cursor = self.db_conn.cursor()
        
    def set_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        print(HOST,self.port)
        self.s.bind((HOST,self.port))
        self.s.listen()
        self.sock_conn, self.addr = self.s.accept()
        self.sock_conn.sendall(bytes('helloclient','utf-8'))
        
        self.work = True
        while(self.work):
            self.command = str(self.sock_conn.recv(1024),'utf-8')
            if len(self.command) == 0:
                break


            if self.command == 'signup':
                #register
                print("registering...")
                self.sock_conn.sendall(bytes('triggered_signup',encoding='utf-8'))
                #reg info
                self.user_name = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.user_name) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_username',encoding='utf-8'))
                self.password = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.password) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_password',encoding='utf-8'))
                self.ip_address = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.ip_address) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_ip',encoding='utf-8'))

                self.sql = ("SELECT * FROM login_info WHERE user_name='%s'" %(self.user_name))
                self.cursor.execute(self.sql)
                if(self.cursor.rowcount):
                    self.sock_conn.sendall(bytes('duplicated',encoding='utf-8'))
                    continue
                else:
                    self.sql = ("INSERT INTO login_info(user_name,password,ip_address)VALUES('%s','%s','%s')" %\
                            (self.user_name,self.password,self.ip_address))
                    #数据库插入用户注册信息
                    try:
                        self.cursor.execute(self.sql)
                        self.db_conn.commit()
                    except:
                        self.db_conn.rollback()
                    self.sock_conn.sendall(bytes('stored',encoding='utf-8'))



            elif self.command == 'login':
                print("logging...")
                #login
                self.sock_conn.sendall(bytes('triggered_login',encoding='utf-8'))
                #log_info
                self.user_name = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.user_name) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_username',encoding='utf-8'))
                self.password = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.password) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_password',encoding='utf-8'))
                self.ip_address = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.ip_address) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_ip',encoding='utf-8'))
                print("sqling")

                self.sql = ("SELECT * FROM login_info WHERE user_name='%s' AND password='%s'" %\
                        (self.user_name,self.password))
                self.cursor.execute(self.sql)
                if(self.cursor.rowcount):
                    self.sock_conn.sendall(bytes('success',encoding='utf-8'))
                    self.sql = ("UPDATE login_info SET ip_address='%s' WHERE user_name='%s'" %\
                            (self.ip_address,self.user_name))
                    try:
                        self.cursor.execute(self.sql)
                        self.db_conn.commit()
                    except:
                        self.db_conn.rollback()
                else:
                    self.sock_conn.sendall(bytes('wrong',encoding='utf-8'))



            elif self.command == 'upload':
                print("uploading...")
                #uploading the file information
                self.sock_conn.sendall(bytes('triggered_upload',encoding='utf-8'))
                #file_info
                self.file_name = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.ip_address) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_filename',encoding='utf-8'))
                self.file_size = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.ip_address) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_filesize',encoding='utf-8'))
                self.uploader  = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.ip_address) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_uploader',encoding='utf-8'))
                self.sharetime = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.ip_address) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_time',encoding='utf-8'))
                self.category  = str(self.sock_conn.recv(1024),'utf-8')
                #if len(self.ip_address) == 0:
                #    break
                self.sock_conn.sendall(bytes('got_category',encoding='utf8'))
                self.file_id = str(hash_encoding(self.file_name))
                
                self.sql = ("INSERT INTO file_info\
                        (file_id,file_name,file_size,uploader,sharetime,category)\
                        VALUES(%s,'%s','%s','%s','%s','%s')" % \
                        (self.file_id,self.file_name,self.file_size,self.uploader,self.sharetime,self.category))
                print(self.sql)
                #数据库插入用户注册信息
                try:
                    self.cursor.execute(self.sql)
                    self.db_conn.commit()
                except:
                    print('upload error')
                    self.db_conn.rollback()
                self.sock_conn.sendall(bytes('uploaded',encoding='utf-8'))


            elif self.command == 'get_index':
                print("indexing...")
                # SQL 查询语句
                self.sql = "SELECT * FROM file_info;"
                try:
                    # 执行SQL语句
                    self.cursor.execute(self.sql)
                except:
                    print("Error: unable to fetch data")
                print(self.cursor.rowcount)

                # 获取所有记录列表
                self.sock_conn.sendall(bytes(str(self.cursor.rowcount),encoding='utf-8'))
                self.results = self.cursor.fetchall()
                for row in self.results:
                    # 发给客户机
                    socket_verify('ready',self.sock_conn)
                    row_str = []
                    for item in row:
                        print(type(item))
                        row_str.append(str(item))
                    line = '\t'.join(row_str)
                    print(line)
                    socket_send(line,self.sock_conn)


            elif self.command == 'get_path':
                socket_send('get_path_triggered',self.sock_conn)
                self.ID = socket_receive(self.sock_conn)

                self.sql = ("SELECT uploader FROM file_info WHERE file_id = %d" % (int(self.ID)))
                try:
                    # 执行SQL语句
                    self.cursor.execute(self.sql)
                except:
                    print("Error: unable to fetch data")
                
                if(self.cursor.rowcount):
                    self.uploader = self.cursor.fetchone()
                    print(self.uploader)
                    self.uploader = self.uploader[0]

                    self.sql2 = ("SELECT ip_address FROM login_info WHERE user_name='%s'" % (self.uploader))
                    try:
                        # 执行SQL语句
                        self.cursor.execute(self.sql2)
                    except:
                        print("Error: unable to fetch data")
                    self.path = self.cursor.fetchone()
                    print(self.path)
                    self.path = self.path[0]
                    print(self.path)
                    socket_send(self.path,self.sock_conn)
                else:
                    socket_send('^no file^',self.sock_conn)


            elif self.command == 'search':
                print("Searching")
                socket_send('search_triggered',self.sock_conn)

                self.ID = socket_receive(self.sock_conn)
                self.sql = ("SELECT file_name from file_info WHERE file_id = %s" % self.ID)
                self.cursor.execute(self.sql)
                if(self.cursor.rowcount):
                    self.file_name = self.cursor.fetchone()
                    print(self.file_name)
                    self.file_name = self.file_name[0]
                    socket_send(self.file_name,self.sock_conn)
                else:
                    socket_send('^^^',self.sock_conn)

            elif self.command == 'remove':
                print('removing')
                socket_send('remove_triggered',self.sock_conn)

                self.ID = socket_receive(self.sock_conn)
                self.sql = ("SELECT * from file_info WHERE file_id = %s" % self.ID)
                self.cursor.execute(self.sql)
                if(self.cursor.rowcount):
                    self.sql2 = ("DELETE FROM file_info WHERE file_id = %s" % self.ID)
                    # 执行SQL语句
                    self.cursor.execute(self.sql2)
                    self.db_conn.commit()
                    socket_send('is_removed',self.sock_conn)
                else:
                    socket_send('not_found',self.sock_conn)


            elif self.command == 'connect_close':
                self.work = 0
                self.sock_conn.sendall(bytes('closing',encoding='utf-8'))
                self.s.close()    

            else:
                print("Error detected.")
                break


Cli_Conn0 = client_connection(0)
Cli_Conn1 = client_connection(1)
Cli_Conn2 = client_connection(2)
#Cli_Conn0.set_connection()
#threading.Thread(target=Cli_Conn0.set_connection,args=()).start()


#exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, cli_conn):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.cli_conn = cli_conn
    def run(self):
        print ("开始线程：" + self.name)
        while True:
            self.cli_conn.set_connection()
        print ("退出线程：" + self.name)


# 创建新线程
thread1 = myThread(1, "Thread-1", 1, Cli_Conn0)
thread2 = myThread(2, "Thread-2", 2, Cli_Conn1)
thread3 = myThread(3, "Thread-3", 3, Cli_Conn2)

# 开启新线程
thread1.start()
thread2.start()
thread3.start()
thread1.join()
thread2.join()
thread3.join()
print ("退出主线程")