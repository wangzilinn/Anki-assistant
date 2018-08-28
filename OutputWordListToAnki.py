import tkinter as tk
from tkinter.filedialog import *
import urllib.request
import re
import codecs  # 读写utf-8
from bs4 import BeautifulSoup


def en_to_zh_bing(word):  # bing模式英译中
    try:
        url = "http://cn.bing.com/dict/search?q=" + word
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8")
        soup = BeautifulSoup(html, 'lxml')
    except:
        return "time out\n"
    return_string = ""
    # 目标词汇
    word = soup.find('div', id="headword").text
    # 释义
    express = ""
    expresses = soup.find_all('span', class_='def')
    for item in expresses:
        express = item.text + express
    # 例句
    english_example = ""
    english_examples = soup.find('div', class_='sen_en')
    for item in english_examples:
        english_example = english_example + item.text
    return_string = return_string + word + "\n" + express
    chinese_example = ""
    chinese_examples = soup.find('div', class_='sen_cn')
    for item in chinese_examples:
        chinese_example = chinese_example + item.text
    # 合并
    return_string = word + '\n' + express + '\n' + english_example + chinese_example + '\n'
    return return_string


def en_to_zh_iciba(word):  # 爱词霸模式英译中
    try:
        url = "http://www.iciba.com/" + word
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8")
        soup = BeautifulSoup(html, 'lxml')
    except:
        return "time out\n"
    # 目标词汇
    word = soup.find('h1', class_="keyword").text
    word = re.sub('\s', '', word)  # 将string中的所有空白字符删除
    # 释义
    express = ""
    expresses = soup.find_all('ul', class_='base-list switch_part')
    for item in expresses:
        express = item.text + express
    express = re.sub('\s', '', express)
    return word + '\n' + express + '\n'


def en_to_zh_youdict(word):  # youdict模式英译中
    try:
        url = "http://www.youdict.com/w/" + word
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8")
        soup = BeautifulSoup(html, 'lxml')
    except:
        return "time out\n"
    return_string = ""
    # 目标词汇
    try:
        word = soup.find('h3', id="yd-word").text
        word = re.sub('\s', '', word)  # 将string中的所有空白字符删除
    except AttributeError:
        vocabulary_label.config(text="\nNo words found")
        return ""
    # 在哪些词汇表中
    try:
        vocabulary = soup.find(style="margin-bottom:6px;").text.split("\n")[1]  # 删除这个句子中的回车
        vocabulary_label.config(text=vocabulary)
    except AttributeError:
        vocabulary_label.config(text="Unknown")
    # 释义:
    try:
        express = ""
        expresses = soup.find(id='yd-word-meaning')
        for item in expresses:
            express = item.text + express
        express = re.sub('\s', '', express)
    except AttributeError:
        express = ""
    # 例句
    try:
        english_examples = soup.find(id='yd-liju').text
        delete_number = english_examples.index("来自")  # 只需要第一个例句
        english_examples = english_examples[4:delete_number]
    except AttributeError:
        english_examples = ""
    # 词根
    root = ""
    try:
        ex = 0  # 除去第一个元素
        for item in soup.find(id='yd-ciyuan').contents:
            if ex != 0:
                root = root + item.text
            ex = ex + 1
    except AttributeError:
        root = "null"
    return word + '\n' + express + '\n' + english_examples + '\n' + root + '\n'


# 点击导出按钮之后
def output_command():
    input_str = display_result_widget.get("0.0", "end")
    input_str = input_str.replace("\n", "\t")
    input_str = input_str.replace("\t-----------------\t", "\r\n")
    fo = codecs.open("C:\\Users\\78286\\Desktop\\foo.txt", "a+", "utf-8")
    fo.write(input_str[0:-1])  # 去掉最后一个\t
    fo.close()
    display_result_widget.delete("0.0", "end")  # 清空显示区
    display_message_widget.config(text="已导出")


# 点击选择词典按钮之后
def source_choice_command():
    global select_dictionaries
    if source_choice_status.get() == 1:
        display_message_widget.config(text="select bing")
        select_dictionaries = 1
    elif source_choice_status.get() == 2:
        display_message_widget.config(text="select iciba")
        select_dictionaries = 2
    elif source_choice_status.get() == 3:
        display_message_widget.config(text="select youdict")
        select_dictionaries = 3


activate_input_youdao_word_book_feature = False


# 点击激活导入有道单词本功能之后
def display_input_interface_command():
    global activate_input_youdao_word_book_feature
    if activate_input_youdao_word_book_feature:
        activate_input_youdao_word_book_feature = False
        input_youdao_word_book_button.config(text="Off")
        youdao_word_list_widget.grid_forget()  # 隐藏单词列表控件
        import_word_button.grid_forget()  # 隐藏确认导入按钮
        # import_word_button.place_forget()  # 隐藏确认导入按钮
        window.geometry("445x500")  # 恢复原来的窗口大小
    else:
        activate_input_youdao_word_book_feature = True
        input_youdao_word_book_button.config(text="On")
        window.geometry("605x500")  # 扩大窗口以显示列表控件
        youdao_word_list_widget.grid(row=5, column=6)  # 放置列表控件
        import_word_button.grid(row=12, column=6)  # 放置确认导入按钮
        if youdao_word_list_widget.size() == 0:  # 当原来列表不为空时再导入文件
            try:
                file = tk.filedialog.askopenfilename(filetypes=[("单词本文件", ".txt")])
                with open(file, 'r', encoding="utf-8") as f1:  # 打开文件
                    txt_string = f1.read()  # 读入文件内容到str1中
                for item in txt_string.split("\n"):
                    if re.match(r'\d*, ', item):  # 提取出有单词的一项（这一行第一个是数字之后接着逗号之后是一个空格）
                        item = item.split(" ")[1]  # 只要每项中的单词而不要序号和音标
                        youdao_word_list_widget.insert('end', item)  # 装入列表
            except:
                display_message_widget.config(text="解析文件时发生意外，检查单词本是否为UTF8编码")
                display_input_interface_command()  # 如果发生意外再次调用该函数关掉该功能


select_dictionaries = 0
window = tk.Tk()
window.geometry("445x500")
source_choice_status = tk.IntVar()  # 点击词典选择按钮后，将按钮值赋给该变量
window.title("生成anki单词本")


# 点击单词确认按钮之后
def confirm_button_command(event=None):
    temp = word_entry_widget.get()
    # 当没有输入时，点击无效
    if len(temp) == 0:
        return
    word_entry_widget.delete(0, len(temp))
    output_to_result_widget(temp)


# 点击确认从有道单词本输出之后
def import_youdao_word_command():
    if youdao_word_list_widget.size() > 0:
        word = youdao_word_list_widget.get(0)
        youdao_word_list_widget.delete(0)  # 删除第一个位置的字符
        output_to_result_widget(word)


def output_to_result_widget(word):  # 将单词输出到显示的文本框
    global select_dictionaries
    # 选择使用哪个字典输出到文本框
    if select_dictionaries == 1:
        display_result_widget.insert("end", en_to_zh_bing(word))
    elif select_dictionaries == 2:
        display_result_widget.insert("end", en_to_zh_iciba(word))
    elif select_dictionaries == 3:
        display_result_widget.insert("end", en_to_zh_youdict(word))
    display_result_widget.insert("end", "-----------------\n")
    display_message_widget.config(text="已添加新单词")


# 选择词典控件
source_choice_widget1 = tk.Radiobutton(window, text='bing',
                                       variable=source_choice_status, value=1,
                                       command=source_choice_command)
source_choice_widget2 = tk.Radiobutton(window, text='iciba',
                                       variable=source_choice_status, value=2,
                                       command=source_choice_command)
source_choice_widget3 = tk.Radiobutton(window, text='youdict',
                                       variable=source_choice_status, value=3,
                                       command=source_choice_command)
source_choice_widget3.select()
source_choice_widget1.grid(row=1, column=0)
source_choice_widget2.grid(row=1, column=1)
source_choice_widget3.grid(row=1, column=2)
# 输入控件
word_label = tk.Label(text="word:")
word_label.grid(row=0, column=3)
word_entry_widget = tk.Entry(window)
word_entry_widget.bind('<Enter>', confirm_button_command)
word_entry_widget.grid(row=1, column=3)
# 单词确认按钮
confirm_button = tk.Button(window,
                           text="confirm",
                           command=confirm_button_command
                           )
confirm_button.grid(row=1, column=4)
# 显示结果控件
display_result_widget = tk.Text(window, width=60, height=24)
display_result_widget.grid(row=5, column=0, columnspan=6, rowspan=6, padx=10)
# 导出确认按钮
output_control_button = tk.Button(window,
                                  text="output",
                                  command=output_command)
output_control_button.grid(row=12, column=2, pady=10)
# 显示状态
display_message_widget = tk.Label(window,
                                    text="未开始")
display_message_widget.grid(row=13, column=0, padx=10, columnspan=6, rowspan=2, sticky=W)
# 导入有道单词本控件
input_youdao_word_book_label = tk.Label(text="Import youdao word book：")
input_youdao_word_book_button = tk.Button(window, text="Off",
                                          command=display_input_interface_command)
input_youdao_word_book_label.grid(row=2, column=0, columnspan=3)
input_youdao_word_book_button.grid(row=2, column=3, sticky=W)
# 导入易混淆词控件
input_confusing_words_book_label = tk.Label(text="Import confusing words book：")
input_confusing_words_button = tk.Button(window, text="Off",
                                          command=display_input_interface_command)
input_confusing_words_book_label.grid(row=3, column=0, columnspan=3)
input_confusing_words_button.grid(row=3, column=3, sticky=W)
# 导入有道单词本的单词列表
youdao_word_list_widget = tk.Listbox(window, height=19)
# 将分析好的有道单词进行加工的按钮
import_word_button = tk.Button(window, text="confirm",
                               command=import_youdao_word_command)
# 各种label:
source_choice_label = tk.Label(text="choice source :")
source_choice_label.grid(row=0, column=1)
vocabulary_label = tk.Label()  # 词汇表（CET4，考研等）
vocabulary_label.grid(row=4, column=0, columnspan=4, sticky=W,padx=10)
# 开始执行
source_choice_command()  # 初始化选择的默认状态
window.mainloop()
