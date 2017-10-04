# -*- coding=utf-8 -*-
from bs4 import BeautifulSoup
import mysql.connector
import requests
import xlwt
import os


#获得某一个月的天气数据
def getListByUrl(url):
    i = 0
    res = requests.get(url,timeout=10)
    while(res.status_code!=200 and i<3):
        res = requests.get(url,timeout=10)
        i += 1
    if(res.status_code==200):
        soup = BeautifulSoup(res.text,"html.parser")
        weathers = soup.select("#tool_site")
        title = weathers[1].select("h3")[0].text
        weatherInfors = weathers[1].select("ul")
        weatherList = list()
        for weatherInfor in weatherInfors:
            singleWeather = list()
            for li in weatherInfor.select('li'):
                singleWeather.append(li.text)
            weatherList.append(singleWeather)
        print(title)
        return weatherList,title
    else:
        return None,None

#@par:addressUrl 获得某地区的数据
#@par:excelSavePath  数据的保存地址
def getListByAddress(addressUrl,excelSavePath):
    # url = "http://lishi.tianqi.com/beijing/index.html"
    url = addressUrl
    i = 0
    res = requests.get(url,timeout=10)
    while(res.status_code!=200 and i<3):
        res = requests.get(url,timeout=10)
        i += 1
    if(res.status_code==200):
        soup = BeautifulSoup(res.text,"html.parser")
        dates = soup.select(".tqtongji1 ul li a")
        workbook = xlwt.Workbook(encoding='utf-8')
        for d in dates:
            weatherList,title = getListByUrl(d["href"])
            if(weatherList!=None):
                booksheet = workbook.add_sheet(title,cell_overwrite_ok=True)
                for i,row in enumerate(weatherList):
                    for j,col in enumerate(row):
                        booksheet.write(i,j,col)
        workbook.save(excelSavePath)
    else:
        return None

# Jiang 获取指定城市的月份列表
def getmonthlist(addressUrl):
    url = addressUrl
    i = 0
    res = requests.get(url,timeout=10)
    while(res.status_code!=200 and i<3):
        res = requests.get(url,timeout=10)
        i += 1
    if(res.status_code==200):
        soup = BeautifulSoup(res.text, "html.parser")
        #获取月份列表
        dates = soup.select(".tqtongji1 ul li a")
        return dates
    else:
        return None


# Jiang 获取指定月份的天气列表
def getweatherlist(url):
    i = 0
    res = requests.get(url,timeout=10)
    while(res.status_code!=200 and i<3):
        res = requests.get(url,timeout=10)
        i += 1
    if (res.status_code == 200):
        soup = BeautifulSoup(res.text, "html.parser")
        weathers = soup.select("#tool_site")
        title = weathers[1].select("h3")[0].text
        weatherInfors = weathers[1].select("ul")
        weatherList = list()
        for weatherInfor in weatherInfors:
            singleWeather = list()
            for li in weatherInfor.select('li'):
                singleWeather.append(li.text)
            weatherList.append(singleWeather)
        print(title)
        return weatherList, title
    else:
        return None

# Jiang 创建数据库
def createtable(conn):
    cursor = conn.cursor()
    str = 'create table history_weather(' \
          'id int primary key not null auto_increment,' \
          'city char(10),' \
          'date date,' \
          'Tmax int,' \
          'Tmin int,' \
          'weather char(10),' \
          'Wdirection char(10),' \
          'Wpower char(10))'
    try:
        cursor.execute(str)
        conn.commit()
    except:
        print('')
    finally:
        cursor.close()

# Jiang 每月天气数据写入数据库
def inserttomysql(city,weatherlist,conn):
    cursor = conn.cursor()
    sql = 'INSERT INTO history_weather values(%s,%s,%s,%s,%s,%s,%s,%s)'
    param = []
    for i  in range(1,len(weatherlist)):
        tmp = weatherlist[i]
        tmp.insert(0,city)
        tmp.insert(0,'')
        param.append(tmp)
    cursor.executemany(sql,param)
    conn.commit()
    cursor.close

# jiang 存储到数据库
def SavetoMysql(host, port, user, passwd,db):
    # 建立数据库连接
    conn = mysql.connector.connect(host=host,port=port,user=user,passwd=passwd,db=db)
    createtable(conn)
    # 遍历所有城市
    add = BeautifulSoup(requests.get('http://lishi.tianqi.com/').text, "html.parser")
    bcity = add.select('[class=bcity]')
    cityAddr = []
    for i in range(len(bcity)):
        cityAddr.extend(bcity[i].find_all('a', target='_blank'))

    for i in range(len(cityAddr)):
        date = getmonthlist(cityAddr[i]['href'])
        city = cityAddr[i].text
        if(date!=None):
            for j in range(len(date)):
                weatherlist, title = getweatherlist(date[j]['href'])
                if(weatherlist!=None):
                    inserttomysql(city, weatherlist, conn)

    # 关闭数据库连接
    conn.close()

#jiang 历史天气保存到excel
def SavetoExcel(addressName="all"):
    addresses = BeautifulSoup(requests.get('http://lishi.tianqi.com/').text, "html.parser")
    if(addressName=="all"):
        bcity = addresses.select('[class=bcity]')
        cityAddr = []
        for i in range(len(bcity)):
            cityAddr.extend(bcity[i].find_all('a', target='_blank'))
        savePath = input("请输入即将保存天气数据的路径（如若不输入，将默认保存到c:/weather/下）\n")
        for i in range(len(cityAddr)):
            q = cityAddr[i]
            city = cityAddr[i].text
            if not savePath.strip():
                savePath = 'c:/weather/'
            if not os.path.exists(savePath):
                os.makedirs(savePath)
            filePath = savePath + city + ".xls"
            getListByAddress(q["href"], filePath)
            print(u"已保存"+city+u"的天气:" + filePath)
    else:
        queryAddress = addresses.find_all('a', text=addressName)
        city = addressName
        if len(queryAddress):
            savePath = input("检测到有该城市数据，请输入即将保存天气数据的路径（如若不输入，将默认保存到c:/weather/" + addressName + ".xls）:\n")
            if not savePath.strip():
                savePath = 'c:/weather/'
            if not os.path.exists(savePath):
                os.makedirs(savePath)
            filePath = savePath + city + ".xls"
            for q in queryAddress:
                getListByAddress(q["href"], filePath)
                print(u"已经天气数据保存到:" + filePath)
        else:
            print("不存在该城市的数据")


def main():
    print('选择数据存储到：\n')
    print ('1.存储到mysql\n')
    print ('2.存储到Excel\n')
    choice = input("请输入编号:")
    if(choice=='1'):
        host = input("输入数据库主机地址:")
        port = input("输入数据库端口:")
        user = input("输入用户名：")
        passwd = input("输入密码：")
        db = input("输入数据库名：")
        if(host=='' and port=='' and user=='' and passwd=='' and db==''):
            SavetoMysql()
        else:
            SavetoMysql(host,port,user,passwd,db)
    elif(choice=='2'):
        addressName = input("请输入即将获取天气的城市(输入all表示所有城市):")
        SavetoExcel(addressName)
    else:
        print ('输入错误，按任意键退出。')
        a = input("")

if __name__ == "__main__":
    main()





