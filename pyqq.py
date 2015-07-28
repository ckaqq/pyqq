# -*- coding: UTF-8 -*-
import urllib
import urllib2
import cookielib
import re
import json, sys, os
import random,time,datetime
import threading
#解决写入中文报错问题
reload(sys)
sys.setdefaultencoding('utf-8')

class RedirctHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        global new_location
        new_location=headers['location']
        pass
    def http_error_302(self, req, fp, code, msg, headers):
        global new_location
        new_location=headers['location']
        pass

class PyQQ(threading.Thread):
    ExploereHEADERS = {
        "Accept":"*/*",
        "Accept-Encoding":"gzip,deflate,sdch",
        "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
        "Content-type": "application/x-www-form-urlencoded",
        'Accept-Language':'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Referer":"http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2",
    }
    
    #设置cookie
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    # 安装cookie
    urllib2.install_opener(opener)

    global_uintoQQ_Dict = {}
    global_uintoNick_Dict = {}
    
    def __init__(self, qqnum = None, pwd = None, encrypyUrl = 'http://127.0.0.1:23333/'):
        threading.Thread.__init__(self, name=qqnum)
        self.thread_stop = False
        self.encrypyUrl = encrypyUrl
        print "Begin!"
        if not os.path.exists("msg"):
            os.mkdir("msg")
        if qqnum and pwd:
            result = self.login(qqnum, pwd)
            if result == 0 :
                print "Login success"
            else :
                print "Login fail -- " + result.decode('utf-8')
                sys.exit(1)

    def login(self, qqnum, pwd):
        if type(qqnum) == type(0):
            qqnum = str(qqnum)
        url = 'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=5&mibao_css=m_webqq&appid=1003903&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20150211001'
        html = self.getWeb(url, hasHeader = False)
        g_login_sig = re.compile("g_login_sig=encodeURIComponent\\(\"(.*?)\"\\);").findall(html)[0]
        web = self.getWeb('https://ssl.ptlogin2.qq.com/check?pt_tea=1&uin=' + qqnum + '&appid=1003903&js_ver=10116&js_type=0&login_sig=' + g_login_sig + '&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.27641687798313797')
        if web=='':
            return '网络异常'
        arr = re.compile("'(.*?)'").findall(web)
        state = arr[0]
        self.verifycode = arr[1]
        uin = arr[2]
        verifysession = arr[3]
        self.uin = qqnum
        self.pwd = pwd
        #需要验证码
        if state == '1':
            url = 'https://ssl.captcha.qq.com/getimage?aid=1003903&r=0.5486779811326414&uin=' + self.uin + '&cap_cd=' + self.verifycode
            gif = self.getWeb(url)
            file = open(os.getcwd()+'/qq' + qqnum +'code.bmp','w+b')
            file.write(gif)
            file.close()
            self.verifycode = raw_input('[' + qqnum + "] Please inpit the verifycode:")
            for cookie in self.cj :
                if cookie.name == "verifysession" :
                    verifysession = cookie.value
                    break
        parameter = urllib.urlencode({'pwd': self.pwd, 'uin': uin, 'vcode': self.verifycode})
        try :
            url = self.encrypyUrl + '?' + parameter
            p = self.getWeb(url, hasHeader = False)
        except :
            return 'Please run encrypt.js FIRST!!'

        #step one:第一次登陆
        loginURL = 'https://ssl.ptlogin2.qq.com/login?u=' + self.uin + '&p=' + p + '&verifycode=' + self.verifycode + '&webqq_type=10&remember_uin=1&login2qq=1&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=2-10-4498&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10116&login_sig='+ g_login_sig +'&pt_uistyle=5&pt_randsalt=0&pt_vcode_v1=0&pt_verifysession_v1=' + verifysession

        login = self.getWeb(loginURL)
        info = re.compile("'(.*?)'").findall(login)
        print 'User:[(' + self.uin + ')]'
        if info[0] != '0':
            return "登陆失败"
        #回调地址
        loginURLback = info[2]
        #step two:访问回调地址更新cookie
        info = self.getWeb(loginURLback)
        for cookie in self.cj:
            if cookie.name == 'ptwebqq':
                self.ptwebqq = cookie.value
                break
        self.clientid = '51167527'
        data = 'r=%7B%22ptwebqq%22%3A%22'+self.ptwebqq+'%22%2C%22clientid%22%3A51167527%2C%22psessionid%22%3A%22%22%2C%22 \
                status%22%3A%22online%22%7D'
        #step three:二次登陆
        #{"retcode":103,"errmsg":""} {"retcode":121,"t":"0"} {"retcode":100006,"errmsg":""}
        # 返回103、121，代表连接不成功，需要重新登录；
        # 返回102，代表连接正常，此时服务器暂无信息；
        # 返回0，代表服务器有信息传递过来：包括群信、群成员给你的发信，QQ好友给你的发信。
        try :
            login2 = self.getWeb('http://d.web2.qq.com/channel/login2', 'post', data)
        except :
            login2 = ''
        if login2 == '' :
            return "网络异常"
        dic = eval(login2)
        self.vfwebqq = dic['result']['vfwebqq']
        self.psessionid = dic['result']['psessionid']
        return 0

    #获取好友列表
    def getFriendList(self):
        url = self.encrypyUrl + '?uin=' + self.uin + '&ptwebqq=' + self.ptwebqq
        hash = self.getWeb(url, hasHeader = False)
        getUserFriend = 'http://s.web2.qq.com/api/get_user_friends2'
        data = 'r=%7B%22h%22%3A%22hello%22%2C%22hash%22%3A%22' + hash + '%22%2C%22vfwebqq%22%3A%22' + self.vfwebqq + '%22%7D'
        userfriend = self.getWeb(getUserFriend,'post', data)
        self.friends = json.loads(userfriend)['result']['info']
        #根据uin 和  vfwebqq,得到真正的扣扣号account
        for friend in self.friends:
            uin = friend['uin']
            data_get_account = 'http://s.web2.qq.com/api/get_friend_uin2?tuin='+str(uin)+'&type=1&vfwebqq='+self.vfwebqq+'&t=1405872226955'
            friend_info = self.getWeb(data_get_account)
            friend_info = json.loads(friend_info)
            account = friend_info['result']['account']
            friend['account'] = account
        self.saveFriend()
        print 'Get Friends list success!'

    #缓存好友信息，用于子类重写
    def saveFriend(self) : 
        return False

    def getGroupList(self):
        self.groups = []
        codes = self.getSimpleGroup()
        for code in codes :
            group = self.getOneGroup(code['code'])
            self.groups.append(group)
        self.saveGroup()

    #得到简单的群组信息
    def getSimpleGroup(self) :
        url = self.encrypyUrl + '?uin=' + self.uin + '&ptwebqq=' + self.ptwebqq
        hash = self.getWeb(url, hasHeader = False)
        getGroup = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        data = 'r=%7B%22vfwebqq%22%3A%22' + self.vfwebqq + '%22%2C%22hash%22%3A%22' + hash + '%22%7D'
        usergroup = self.getWeb(getGroup, 'post', data)
        try :
            groups = json.loads(usergroup)['result']['gnamelist']
        except :
            groups = []
        return groups

    #得到一个群的详细信息（包括成员）
    def getOneGroup(self, code) :
        group = {}
        group["code"] = code

        #由群信息获取真实群号
        url = 'http://s.web2.qq.com/api/get_friend_uin2?tuin=' + str(group["code"]) + '&verifysession=&type=4&code=&vfwebqq=' + self.vfwebqq + '&t=1475202994632'
        try :
            group['account'] = json.loads(self.getWeb(url))['result']['account']
        except :
            return []

        #由群信息获取群成员信息
        url = 'http://s.web2.qq.com/api/get_group_info_ext2?gcode=' + str(group["code"]) + '&vfwebqq=' + self.vfwebqq + '&t=1406197323657'
        try :
            result = json.loads(self.getWeb(url))['result']
        except :
            return []

        group['name'] = result['ginfo']['name']
        group['gid']  = result['ginfo']['gid']
        try:
            members = result['minfo']
            #获取群名片
            try :
                cards = result['cards']
            except :
                cards = []
            for member in members :
                member['card'] = ''
                for card in cards :
                    if card['muin'] == member['uin'] :
                        member['card'] = card['card']
                        break
        except:
            #超级大群结构不同
            members = result['ginfo']['members']
            for member in members:
                member['uin'] = member['muin']
                member['nick'] = 'Null'
                del member['muin']
        group['members'] = members
        return group

    #缓存QQ群，用于子类重写
    def saveGroup(self) : 
        return False

    def analysisMsg(self, msg, count=0):
        if msg['poll_type'] == 'group_message':
            gcode      = msg['value']['group_code']          #gcode
            gp_account = msg['value']['info_seq']            #real gp num
            user_uin   = str(msg['value']['send_uin'])       #real send uin
            try:
                user_account = self.global_uintoQQ_Dict[user_uin]
                nick         = self.global_uintoNick_Dict[user_uin]
            except:
                user_account ='0' 
            flag = 0
            for gp in self.groups:
                if gp['code'] == gcode:
                    flag = 1
                    gp_name = gp['name']                #real qp name
                    if user_account == '0':
                        user_account, nick = self.getMemberQQ(user_uin, gp['members'])
                        self.global_uintoQQ_Dict[user_uin]   = user_account
                        self.global_uintoNick_Dict[user_uin] = nick
            if flag == 0:
                if count < 5:
                    self.getGroupList()
                    return self.analysisMsg(msg, count+1)
                else:
                    print 'Analysis Fail!'
                    sys.exit(1)
            else:
                return str(gp_account),gp_name,str(user_account),nick.encode('gbk','ignore').decode("gbk")
    
        elif msg['poll_type'] == 'message':
            gp_account = '0'
            gp_name = '0'
            user_uin = msg['value']['from_uin']
            flag = 0
            for friend in self.friends:
                if friend['uin'] == user_uin:
                    flag = 1
                    user_account = friend['account']
                    nick = friend['nick']
            if flag == 0:
                if count < 5:
                    self.getFriendList()
                    return self.analysisMsg(msg, count+1)
                else:
                    print 'Analysis Fail!'
                    sys.exit(1)
            return str(gp_account),gp_name,str(user_account),nick

    def getMemberQQ(self, user_uin, members):
        for member in members:
            if str(member['uin']) == str(user_uin):
                uin = member['uin']
                uin_get_account = 'http://s.web2.qq.com/api/get_friend_uin2?tuin='+str(uin)+'&type=1&vfwebqq='+self.vfwebqq+'&t=1405872226955'
                account = json.loads(self.getWeb(uin_get_account))['result']['account']
                member['account'] = str(account)
                return str(account), member['nick']
    # webQQ发送时不稳定不可靠的
    # 消息发送不出去的常见原因：
    #1、发送之后直接返回错误页面，说明参数，转码，COOKIES不对！
    #2、返回0，一开始能发送出去，后来却又发送不去了，原因可能是程序采用单线程运作，
    #   这种现象经常会出现，在我们发送消息的时候，需要一个线程去获取消息，即POLL。
    #   简单来说，发送消息和接收消息需要两个独立的线程单独完成，不可将其合成一个线程里面。
    #   再有就是"msg_id":23500002,看看是否累加1，前面的数字是随机数，后面的数字需要累加，
    #   第1条消息就是1，第二条消息就是2。。。
    def sendMessage(self, qqnum, content, method = "uin"):
        if type(qqnum) in (type(u''), type('')):
            qqnum = int(qqnum)
        user=False
        #通过发送到QQ号的方式发送消息
        if method != 'uin':
            for users in self.friends:
                if users['account'] == qqnum:
                    user = users
                    break
        else :
            for users in self.friends:
                if users['uin'] == qqnum:
                    user = users
                    break
        if not user:
            print 'Failed to send message'
            return
        if user.get('msgID') == None:
            user['msgID'] = str(random.randint(10000000,99999999));
        else :
            msgID = int(user['msgID'])
            msgID = msgID + 1
            user['msgID'] = str(msgID)
        msg = urllib.quote((str(content)).replace("\n","\\\\n").replace("\r","\\\\r"))
        data ='r=%7B%22to%22%3A'+str(user['uin'])+'%2C%22content%22%3A%22%5B%5C%22'+msg+'%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A10%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22face%22%3A'+str(user['face'])+'%2C%22clientid%22%3A'+self.clientid+'%2C%22msg_id%22%3A'+user['msgID']+'%2C%22psessionid%22%3A%22'+self.psessionid+'%22%7D'
        sendURL = 'http://d.web2.qq.com/channel/send_buddy_msg2'
        #print data
        try:
            send = self.getWeb(sendURL, 'post', data)
            print "Message send over!"
        except:
            print 'I can say nothing!'
            pass 
        
    def sendGroupMessage(self, gid, content, method = "uin"):
        if type(gid) in (type(u''), type('')):
            gid = int(gid)
        user = {}
        #通过发送到QQ群号的方式发送消息
        if method != 'uin':
            for gps in self.groups:
                if gps['account'] == gid:
                    user = gps
                    break
        else :
            for gps in self.groups:
                if gps['gid'] == gid:
                    user = gps
                    break
        if not user:
            return
        if user.get('msgID') == None:
            user['msgID'] = str(random.randint(10000000,99999999));
        else :
            msgID = int(user['msgID'])
            msgID = msgID + 1
            user['msgID'] = str(msgID)
        msg = urllib.quote((str(content)).replace("\n","\\\\n").replace("\r","\\\\r"))
        data = 'r=%7B%22group_uin%22%3A'+str(user['gid'])+'%2C%22content%22%3A%22%5B%5C%22'+msg+'%5C%22%2C%5B%5C%22font%5C%22%2C%7B%5C%22name%5C%22%3A%5C%22%E5%AE%8B%E4%BD%93%5C%22%2C%5C%22size%5C%22%3A10%2C%5C%22style%5C%22%3A%5B0%2C0%2C0%5D%2C%5C%22color%5C%22%3A%5C%22000000%5C%22%7D%5D%5D%22%2C%22faceface%22%3A0%2C%22clientid%22%3A'+self.clientid+'%2C%22msg_id%22%3A'+user['msgID']+'%2C%22psessionid%22%3A%22'+self.psessionid+'%22%7D'
        sendURL = 'http://d.web2.qq.com/channel/send_qun_msg2'
        try:
            send = self.getWeb(sendURL, 'post', data)
            print "Group Message send over!"
        except:
            print 'I can say nothing...' 
            pass
    
    def getMessage(self):
        data = 'r=%7B%22ptwebqq%22%3A%22'+self.ptwebqq+'%22%2C%22clientid%22%3A'+self.clientid+'%2C%22psessionid%22%3A%22'+self.psessionid+'%22%2C%22key%22%3A%22%22%7D'
        rollURL = 'http://d.web2.qq.com/channel/poll2'
        roll = self.getWeb(rollURL,'post', data)
        print self.getTime()
        #print roll
        retcode = json.loads(roll)['retcode']
        if retcode == 103 or retcode == 121:
            this.login(self.uin, self.pwd)
            return []
        try:
            message = json.loads(roll)['result']
        except:
            return []
        #可以一次接收多条消息，result是一个List
        for msg in message:
            #正常消息
            if msg['poll_type'] == u'message' or msg['poll_type'] == u'group_message':
                del msg['value']['content'][0]
                msg['msgdata']=u""
                for m in msg['value']['content']:
                    msg['msgdata']=msg['msgdata'] + self.dealMessage(m,msg)
                msg['msgdata']=msg['msgdata'].strip()
            #系统消息
            else:
                if msg['poll_type'] == u'buddies_status_change':
                    print msg['value']["uin"],msg['value']["status"]
                elif msg['poll_type'] == u'shake_message':
                    print msg['value']["from_uin"],"shake"
                elif msg['poll_type'] == u"system_message":
                    rollURL = "http://s.web2.qq.com/api/allow_and_add2"
                    data = "r=%7b%22account%22%3a" + str(msg["value"]["account"]) + "%2c%22gid%22%3a0%2c%22mname%22%3a%22%22%2c%22vfwebqq%22%3a%22"+self.vfwebqq+"%22%7d"
                    roll = self.getWeb(rollURL, 'post', data)
                    print "add friend : " + str(msg["value"]["account"])
                elif msg['poll_type'] == u"buddylist_change":
                    self.getFriendList()
                    print "update friends"
                elif msg['poll_type'] == u"sys_g_msg":
                    print msg["value"]["type"]
                else:
                    print self.getTime()
                    print roll
                    print "Other and System Message!"
                message.remove(msg)
        return message

    def dealMessage(self, m, msg):
        if type(m)==type(u'') or type(m)==type(''):
            return m
        if type(m)==type([]):
            if m[0]==u'face':
                return "![img]( http://pub.idqqimg.com/lib/qqface/" + str(m[1]) + ".gif )"
            elif m[0]==u'offpic':
                rollURL = 'http://d.web2.qq.com/channel/get_offpic2?'+'file_path='+urllib.quote((str(m[1]['file_path'])))+'&f_uin='+str(msg['value']['from_uin'])+'&clientid='+self.clientid+'&psessionid='+self.psessionid
                url = self.getImage(rollURL)
                return "![img]( " + url + " )"
            elif m[0] == u'cface':
                rollURL="http://web2.qq.com/cgi-bin/get_group_pic?type=0&gid="+str(msg['value']["group_code"])+"&uin="+str(msg['value']["send_uin"])+"&rip="+m[1]["server"].split(":")[0]+"&rport="+m[1]["server"].split(":")[1]+"&fid="+str(m[1]["file_id"])+"&pic="+m[1]["name"]+"&vfwebqq="+self.vfwebqq
                url = self.getImage(rollURL)
                return "![img]( " + url + " )"
        print m
        return ""
    
    def getImage(self,rollURL):
        print "get image begin"
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj),RedirctHandler)
        urllib2.install_opener(opener)
        self.getWeb(rollURL)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(opener)
        global new_location
        return new_location

    #获取网页
    def getWeb(self, url, method = 'get', values = '', hasHeader = True):
        if hasHeader == True :
            header = self.ExploereHEADERS
        else :
            header = {}
        if method == 'get':
            req = urllib2.Request(url, headers = header)
        else:
            req = urllib2.Request(url,values,headers = header)
        try:
            response = urllib2.urlopen(req)
            the_page = response.read()
            response.close()
        except:
            the_page=''
        return the_page

    #获取当前时间
    def getTime(self):
        now = time.localtime(time.time())
        s   = time.strftime('%Y-%m-%d %H:%M:%S',now)
        return s

    def run(self) :
        while True:
            time.sleep(0.2)
            if self.thread_stop:
                continue
            try:
                msgs = self.getMessage()
            except:
                continue
            for msg in msgs:
                try :
                    gp_account,gp_name,user_account,nick = self.analysisMsg(msg, 0)
                except:
                    print msg
                    print "Something Wrong in analysisMsg,try again!"
                    continue
                try :
                    msgdata = msg['msgdata']
                except :
                    msgdata = ''
                content = {
                    "gp_account" : gp_account,
                    "gp_name" : gp_name,
                    "user_account" : user_account,
                    "nick" : nick,
                    "msgdata" : msgdata,
                    "time" : datetime.datetime.now(),
                }
                self.saveLogs(content)
                if gp_account!='0':
                    f = open(u'msg/qun'+'-'+gp_account+'.txt','a')
                else:
                    f = open('msg/'+user_account+'.txt','a')
                a = self.getTime() + ' ' + nick.encode('gbk','ignore').decode("gbk") + '(' + user_account + ")"
                b = msg['msgdata']
                f.write(a+'\n'+b+'\n\n')
                f.close()

    #处理消息并将消息记录下来，用于子类重写
    def saveLogs(self, content) : 
        return False

    #停止获取消息
    def stop(self):
         self.thread_stop = True

    #重新开始获取消息
    def restart(self):
        self.thread_stop = False


if __name__ == '__main__':
    account = raw_input('Please input QQ account :')
    pwd= raw_input('Password:')
    qq = PyQQ(account, pwd)
    qq.getFriendList()
    qq.getGroupList()
    qq.start()
    print "Begin to get Messages!!!!!!!!!!!!!!!!!!!!"