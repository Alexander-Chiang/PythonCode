#!/usr/bin/env python
#-*- coding:utf8 -*-
#coding=utf-8
#Author: Yayu.Jiang

import os
import ConfigParser
import requests
import platform
import ctypes

import time

configure = u'config.ini'
url = "http://portal.njnu.edu.cn/portal_io/login"
MessageBox = ctypes.windll.user32.MessageBoxW
title = u"NJNU Auto Login"


class NJNU_Auto_Login():
    username = None
    password = None
    ok_msg = True
    faile_msg = False
    reconn = True
    reconn_time = 30

    def __init__(self):
        if os.path.exists(configure):
            cf = ConfigParser.ConfigParser()
            cf.read(configure)
            try:
                self.username = cf.get("user","username")
                self.password = cf.get("user","password")
                self.ok_msg = cf.getboolean("setting","ok_msg")
                self.faile_msg = cf.getboolean("setting","faile_msg")
                self.reconn = cf.getboolean("setting","reconn")
                self.reconn_time = cf.getint("setting","reconn_time")
                self.reconn_max_num = cf.getint("setting", "reconn_max_num")
                self.keep_online = cf.getboolean("setting", "keep_online")
                self.keep_intvl = cf.getint("setting", "keep_intvl")
            except Exception as e:
                if(platform.system() == "Windows"):
                    MessageBox(None, "[Configure Error] "+ unicode(e.message), title, 0)
                else:
                    print(u'配置文件错误:'+ e.message)
        else:
            msg = u"[Error] " + u"Configure File Not Found"
            if (platform.system() == "Windows"):
                MessageBox(None, msg, title, 0)
            else:
                print(msg)
            exit()


    def login(self):
        if(self.username=="" or self.password==""):
            if (platform.system() == "Windows"):
                MessageBox(None, "[Error] "+ unicode("username or password is blank !"), title, 0)
            else:
                print(u"Error:username or password is blank! ")
            return None
        try:
            res = requests.post(url, data={"username": self.username, "password": self.password})
        except Exception as e: # 连接异常终止程序
            msg = "[Error]"+unicode("Connection aborted.")
            if (platform.system() == "Windows"):
                MessageBox(None, msg, title, 0)
            else:
                print(msg)
            return None
        result = res.json()

        if(result['reply_code']==1 and self.ok_msg):
            msg = "[Success] "+ unicode(result['reply_msg'])
            if (platform.system() == "Windows"):
                MessageBox(None, msg, title, 0)
            else:
                print(msg)
        if (result['reply_code'] == 6 and self.ok_msg):
            msg = "[Success] " + unicode(result['reply_msg'])
            if (platform.system() == "Windows"):
                MessageBox(None, msg, title, 0)
            else:
                print(msg)
        if(result['reply_code'] != 1 and result['reply_code'] != 6 and self.faile_msg):
            msg = "[Faile Code "+ unicode(result['reply_code'])+"]"+ unicode(result['reply_msg'])
            if (platform.system() == "Windows"):
                MessageBox(None, msg, title, 0)
            else:
                print(msg)

        return result

    # 监测是否已连接到网络
    def isOnline(self):
        try:
            res = requests.get("http://www.baidu.com",timeout=5)
            if res.status_code==200:
                return True
            else:
                return False
        except Exception as e:
            return  False

if __name__ == '__main__':

    autologin = NJNU_Auto_Login()

    # 后台保持在线模式
    while(True):

        # 定时发送心跳监测是否正常联网
        if (autologin.isOnline()):
            if (not autologin.keep_online): break
            else:
                time.sleep(autologin.keep_intvl)
                continue

        count = 0
        while(count < autologin.reconn_max_num):
            result = autologin.login()
            if(result==None): break
            if(not autologin.reconn): break
            if(result['reply_code'] == 1 or result['reply_code'] == 6): break
            count += 1
            time.sleep(autologin.reconn_time)
        # 后台保持在线模式关闭，则直接退出
        if(not autologin.keep_online): break
        time.sleep(autologin.keep_intvl)

    exit()




