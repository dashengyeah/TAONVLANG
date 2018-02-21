#-*- coding:utf-8-*-
import urllib.request
import re
import tool
import os

class Spider:
    def __init__(self):
        self.siteURL='http://mm.taobao.com/json/request_top_list.htm'
        self.tool=tool.Tool()
        self.savePath='../data'

    #获取页面
    def getPage(self,pageIndex):
        url=self.siteURL + "?page=" + str(pageIndex)
        response=urllib.request.urlopen(url)
        return response.read().decode('gbk')

    #获得基本信息
    #
    # 每个人的信息格式: ('图片页URL','icon URL','姓名','年龄','地区')
    #
    def getContents(self,pageIndex):
        page=self.getPage(pageIndex)
        pattern=re.compile('<div class="list-item".*?pic-word.*?<a href=".*?".*?<img src="(.*?)".*?<a class="lady-name" href="(.*?)".*?>(.*?)</a>.*?<strong>(.*?)</strong>.*?<span>(.*?)</span>',re.S)
        items=re.findall(pattern,page) #获得基本信息
        contents=[] #存储当前页面的所有妹子信息
        for item in items:
            #print(item)
            #得到详情页面的地址
            response=urllib.request.urlopen("http:"+item[1])
            html=response.read().decode('gbk')
            ptt=re.compile('KISSY.ready.*?url:"(.*?)".*?success:',re.S)
            info=re.findall(ptt,html)
            url="http://mm.taobao.com"+info[0]
            ptt=re.compile('//mm.taobao.com/self/model_card.htm\?user_id=(.*?)$',re.S)
            info=re.findall(ptt,item[1])
            url=url+info[0]

            #得到图片页面的地址
            response=urllib.request.urlopen(url)
            html=response.read().decode('gbk')
            ptt=re.compile('</label><span>(.*?)</span>',re.S)
            info=re.findall(ptt,html)
            url="http:"+info[-1] #有些页面无法匹配到
            #print("-->url: %s"%url)
            #print("")
            contents.append([url,"http:"+item[0],item[2],item[3],item[4]])
        #print(contents)
        #print("")
        return contents

    #获取所有图片的地址
    def getAllImgs(self,page):
        pattern=re.compile('<div class="mm-aixiu-content".*?>(.*?)<!--',re.S)
        content=re.search(pattern,page)
        patternImg=re.compile('<img.*?src="(.*?)"',re.S)
        images=re.findall(patternImg,content.group(1))
        return images

    #保存所有图片
    def saveImgs(self, path, images, name):
        number=1
        print(u"-->There's %s photos of %s." % (len(images),name))
        for imgURL in images:
            splitPath=imgURL.split('.')
            fTail=splitPath.pop()
            if len(fTail)>3:
                fTail='jpg'
            fileName=path+'/'+str(number)+'.'+fTail
            self.saveImg("http:"+imgURL,fileName)
            number+=1

    #保存图标
    def saveIcon(self, path, iconURL):
        splitPath=iconURL.split('.')
        fTail=splitPath.pop()
        fileName=path+'/icon.'+fTail
        self.saveImg(iconURL,fileName)

    def saveImg(self, imgURL, fileName):
        if os.path.exists(fileName):
            print("  Photo %s already exists."%fileName)
            return
        try:
            u=urllib.request.urlopen(imgURL)
        except Exception:
            print("  -->Lost an image!")
            return
        data=u.read()
        f=open(fileName,"wb")
        f.write(data)
        print(u"  Saving her photo: %s" % fileName)
        f.close()

    #保存基本信息
    def saveInfo(self, path, item):
        fileName=path+"/"+item[2]+".txt"
        f=open(fileName,"w")
        f.write("Name: %s\nAge: %s\nLocation: %s\nPerson Page: %s\n"%(item[2],item[3],item[4],item[0]))
        f.close()

    #创建目录
    def mkdir(self,path):
        path=path.strip()
        isExists=os.path.exists(path)
        if not isExists:
            print(u"  ***New folder: %s" % path)
            os.makedirs(path)
            return True
        else:
            print(u"  ***Already exists: %s" % path)
            return False

    #保存单页
    def savePageInfo(self,pageIndex):
        contents=self.getContents(pageIndex)
        item=contents[0]
        for item in contents:
            print(u"A new beauty found! Name: %s Age: %s Location: %s" % (item[2],item[3],item[4]))
            print(u"Saving...")
            print(u"-->got her personal page at %s" % item[0])
            detailURL=item[0]
            urlptt=re.compile('^http://(.*?)$',re.S)
            if not re.findall(urlptt,detailURL):
                continue
            response=urllib.request.urlopen(detailURL)
            detailPage=response.read().decode('gbk')
            #print("-->detailPage:  %s"%detailPage)
            images=self.getAllImgs(detailPage)
            #print(images)
            if item[2]:
                name=item[2]
            else:
                splturl=item[0].split('/')
                name=splturl.pop()
            self.mkdir(self.savePath + '/' + name)
            self.saveInfo(self.savePath + '/' + name, item)
            self.saveIcon(self.savePath + '/' + name, item[1])
            self.saveImgs(self.savePath + '/' + name, images, name)

    #保存多页
    def savePagesInfo(self,start,end):
        for i in range(start,end):
            print(u"Looking for beauties on Page%s..." % str(i))
            self.savePageInfo(i)

spider=Spider()
spider.savePagesInfo(1,12) #页码范围
#spider.savePageInfo(1)
