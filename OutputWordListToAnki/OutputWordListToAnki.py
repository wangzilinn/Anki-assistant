import tkinter as tk
import json
import urllib.request
import hashlib
import re 
import codecs #读写utf-8
from selenium import webdriver
from bs4 import BeautifulSoup

def en_to_zh_bing(word):#英译中
    url = "http://cn.bing.com/dict/search?q=" + word
    responce = urllib.request.urlopen(url)
    html = responce.read().decode("utf-8")
    soup = BeautifulSoup(html, 'lxml')
    returnString = ""
    #目标词汇
    word = soup.find('div', id="headword").text 
    #释义
    express = ""
    expresses = soup.find_all('span', class_='def')
    for item in expresses:
        express = item.text + express
    #例句
    englishExample = ""
    englishExamples = soup.find('div', class_='sen_en')
    for item in englishExamples:
        englishExample = englishExample + item.text
    returnString = returnString + word + "\n" + express
    chineseExample = ""
    chineseExamples = soup.find('div', class_ = 'sen_cn')
    for item in chineseExamples:
        chineseExample = chineseExample + item.text
    #合并
    returnString = word + '\n' + express + '\n' + englishExample + chineseExample + '\n'
    return returnString
def en_to_zh_iciba(word):
    url = "http://www.iciba.com/" + word
    responce = urllib.request.urlopen(url)
    html = responce.read().decode("utf-8")
    soup = BeautifulSoup(html, 'lxml')
    returnString = ""
    #目标词汇
    word = soup.find('h1', class_="keyword").text
    word = re.sub('\s','',word)#将string中的所有空白字符删除
    #释义
    express = ""
    expresses = soup.find_all('ul', class_='base-list switch_part')
    for item in expresses:
        express = item.text + express
    express = re.sub('\s','',express)
    #例句
    #englishExample = soup.find_all('h1', class_='word-root family-chinese size-english')
    #chineseExample = ""
    #chineseExamples = soup.find('div', class_ = 'sen_cn')
    #for item in chineseExamples:
    #    chineseExample = chineseExample + item.text
    #合并
    #returnString = word + '\n' + express + '\n' + englishExample + chineseExample + '\n'
    #return returnString
    return word + '\n' + express + '\n'
#点击导出按钮之后
def outputCommand():
    inputStr = displayResultWidget.get("0.0", "end")  
    inputStr = inputStr.replace("\n", "\t")
    inputStr = inputStr.replace("\t-----------------\t", "\r\n")
    fo = codecs.open("C:\\Users\\78286\\Desktop\\foo.txt", "a+", "utf-8")
    fo.write(inputStr[0:-1])#去掉最后一个\t
    fo.close()
    displayResultWidget.delete("0.0", "end")#清空显示区
    displayMessageWidget.config(text = "已导出")
#点击选择词典按钮之后
def sourceChoiceCommand():
    global selectDict
    if (sourceChoiceStatus.get() == 1):
        displayMessageWidget.config(text = "select bing")
        selectDict = 1
    else:
        displayMessageWidget.config(text = "select iciba")
        selectDict = 2
selectDict = 0     
window = tk.Tk()
sourceChoiceStatus = tk.IntVar()
window.title("生成anki单词本")
#点击确认按钮之后
def confirmButtonCommand():
    temp = wordEntryWidget.get()
    wordEntryWidget.delete(0, len(temp))
    global selectDict
    if (selectDict == 1):
        displayResultWidget.insert("end", en_to_zh_bing(temp))
    elif(selectDict == 2):
        displayResultWidget.insert("end", en_to_zh_iciba(temp))
    displayResultWidget.insert("end", "-----------------\n")
    displayMessageWidget.config(text = "已添加新单词")
#选择词典控件
sourceChoiceWidget1 = tk.Radiobutton(window, text='bing',
                                     variable=sourceChoiceStatus, value=1,
                                     command=sourceChoiceCommand)
sourceChoiceWidget2 = tk.Radiobutton(window, text='iciba',
                                     variable=sourceChoiceStatus, value=2,
                                     command=sourceChoiceCommand)
sourceChoiceWidget1.select()
sourceChoiceWidget1.place(x=20, y=18, anchor='nw')
sourceChoiceWidget2.place(x=80, y=18, anchor='nw')
#输入控件
wordEntryWidget = tk.Entry(window)
wordEntryWidget.pack()
#单词确认按钮
confirmButton = tk.Button(window, 
                          text = "confirm", 
                          command = confirmButtonCommand)
confirmButton.pack()
#显示结果控件
displayResultWidget = tk.Text(window)
displayResultWidget.pack()
#导出确认按钮
outputControlButton = tk.Button(window, 
                                text = "output", 
                                command = outputCommand)
outputControlButton.pack()
#显示状态
displayMessageWidget = tk.Message(window,
                                  text = "未开始")
displayMessageWidget.pack()
#各种label:
sourceChoiceLable = tk.Label(text = "choice source :")
sourceChoiceLable.place(x=20, y=2, anchor='nw')

wordLable = tk.Label(text = "word:")
wordLable.pack()
#开始执行
sourceChoiceCommand()#初始化选择的默认状态
window.mainloop()
