import tkinter as tk
import json
import urllib.request
import hashlib
import re 
import codecs #读写utf-8
from bs4 import BeautifulSoup

def en_to_zh(word):#英译中
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
    
     
window = tk.Tk()
window.title("生成anki单词本")
#点击确认按钮之后
def confirmButtonCommand():
    temp = wordEntryWidget.get()
    wordEntryWidget.delete(0, len(temp))
    displayResultWidget.insert("end", en_to_zh(temp))
    displayResultWidget.insert("end", "-----------------\n")
    displayMessageWidget.config(text = "已添加新单词")

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
window.mainloop()
