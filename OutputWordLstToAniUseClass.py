import tkinter as tk
from enum import Enum # 使用枚举类
from tkinter.filedialog import *
import urllib.request
import re
import codecs  # 读写utf-8
from bs4 import BeautifulSoup
import pyexcel_xlsx


class Translator:
    """将英文单词翻译成带有翻译、例句等的字典"""
    __dictionary_type_dict = {"youdao": 1, "iciba": 2, "youdict": 3}
    __selected_dictionary_type = 0
    __word = ""
    __result_dictionary = {}

    def __init__(self, word, dictonary_type):
        """初始化返回字典，选择需要使用的在线字典"""
        self.__result_dictionary["word"] = word
        self.__result_dictionary["translation"] = ""
        self.__result_dictionary["example_english"] = ""
        self.__result_dictionary["example_chinese"] = ""
        self.__result_dictionary["root"] = ""
        self.__result_dictionary["vocabulary_range"] = ""
        self.__result_dictionary["error"] = "no error"
        # 装填字典
        self.__load_result_dictionary(dictonary_type)

    def __load_result_dictionary(self, dictonary_type):
        try:
            if self.__dictionary_type_dict[dictonary_type] == 1:
                self.__bing_dictionary()
            elif self.__dictionary_type_dict[dictonary_type] == 2:
                self.__iciba_dictionary()
            elif self.__dictionary_type_dict[dictonary_type] == 3:
                self.__youdict_dictionary()
        except KeyError:
            self.__result_dictionary["error"] = "No dictionary found"

    def get_result_dictionary(self):
        return self.__result_dictionary

    def __bing_dictionary(self):
        try:
            url = "http://cn.bing.com/dict/search?q=" + self.__result_dictionary["word"]
            response = urllib.request.urlopen(url)
            html = response.read().decode("utf-8")
            soup = BeautifulSoup(html, 'lxml')
        except:
            return "time out\n"
        # 目标词汇
        self.__result_dictionary["word"] = soup.find('div', id="headword").text
        # 释义
        express = ""
        expresses = soup.find_all('span', class_='def')
        for item in expresses:
            express = item.text + express
        self.__result_dictionary["translation"] = express
        # 例句
        english_example = ""
        english_examples = soup.find('div', class_='sen_en')
        for item in english_examples:
            english_example = english_example + item.text
        self.__result_dictionary["example_english"] = english_example
        chinese_example = ""
        chinese_examples = soup.find('div', class_='sen_cn')
        for item in chinese_examples:
            chinese_example = chinese_example + item.text
        self.__result_dictionary["example_chinese"] = chinese_example

    def __iciba_dictionary(self):
        try:
            url = "http://www.iciba.com/" + self.__result_dictionary["word"]
            response = urllib.request.urlopen(url)
            html = response.read().decode("utf-8")
            soup = BeautifulSoup(html, 'lxml')
        except:
            return "time out\n"
        # 目标词汇
        word = soup.find('h1', class_="keyword").text
        self.__result_dictionary["word"] = re.sub('\s', '', word)  # 将string中的所有空白字符删除
        # 释义
        express = ""
        expresses = soup.find_all('ul', class_='base-list switch_part')
        for item in expresses:
            express = item.text + express
        self.__result_dictionary["translation"] = re.sub('\s', '', express)

    def __youdict_dictionary(self):
        try:
            url = "http://www.youdict.com/w/" + self.__result_dictionary["word"]
            response = urllib.request.urlopen(url)
            html = response.read().decode("utf-8")
            soup = BeautifulSoup(html, 'lxml')
        except:
            return "time out\n"
        # 目标词汇
        try:
            word = soup.find('h3', id="yd-word").text
            self.__result_dictionary["word"] = re.sub('\s', '', word)  # 将string中的所有空白字符删除
        except AttributeError:
            self.__result_dictionary["error"] = "No words found"
        # 在哪些词汇表中
        try:
            self.__result_dictionary["vocabulary_range"] = soup.find(style="margin-bottom:6px;").text.split("\n")[1]  # 删除这个句子中的回车
        except AttributeError:
            self.__result_dictionary["vocabulary_range"] = "Unknown"
        # 释义:
        try:
            expresses = soup.find(id='yd-word-meaning')
            for item in expresses:
                express = item.text + express
            self.__result_dictionary["translation"] = re.sub('\s', '', express)
        except AttributeError:
            self.__result_dictionary["translation"] = "Parsing translation failed"
        # 例句
        try:
            example = soup.find(id='yd-liju').text
            delete_number = example.index("来自")  # 只需要第一个例句,删掉最后来自哪个字典的部分
            example = example[4:delete_number]
            for char in example:
                if Methods.is_chinese(char):
                    example_list = example.split(char, 1)
                    self.__result_dictionary["example_english"] = example_list[0]
                    self.__result_dictionary["example_chinese"] = char + example_list[1]
                    break
        except AttributeError:
            self.__result_dictionary["example_english"] = "Parsing example failed"
        # 词根
        root = ""
        try:
            ex = 0  # 除去第一个元素
            for item in soup.find(id='yd-ciyuan').contents:
                if ex != 0:
                    root = root + item.text
                ex = ex + 1
            self.__result_dictionary["root"] = root
        except AttributeError:
            self.__result_dictionary["root"] = "Parsing root failed"


class Framework(tk.Tk):
    """框架结构"""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.__configuring_panel_size()
        self.__place_widgets()

    def __configuring_panel_size(self):
        self.geometry("445x500")

    def __place_widgets(self):
        """放置各种widgets"""
        self.label_source_choice = tk.Label(text="choice source :")
        self.label_source_choice.grid(row=0, column=1)

        # 单词输入框+确认按钮
        self.label_word = tk.Label(text="word:")
        self.label_word.grid(row=0, column=3)

        self.entry_word = tk.Entry()
        self.entry_word.grid(row=1, column=3)

        # self.button_word_confirm = tk.Button(window, text="confirm", command=self.__command_button_confirm())
        self.button_word_confirm = tk.Button(text="confirm")
        self.button_word_confirm.grid(row=1, column=4)

        # 词汇表（CET4，考研等）
        self.label_vocabulary = tk.Label()
        self.label_vocabulary.grid(row=4, column=0, columnspan=4, sticky=W, padx=10)

        # 显示将要被导出的text
        self.text_show_all = tk.Text(width=60, height=24)
        self.text_show_all.grid(row=5, column=0, columnspan=6, rowspan=6, padx=10)

    def __command_button_confirm(self):
        input_word = self.entry_word.get()
        # 当没有输入时，点击无效
        if len(input_word) == 0:
            return
        self.entry_word.delete(0, len(input_word))
        # 检测输入的是混淆单词列表还是单个单词
        input_word_list = input_word.split("-")
        if len(input_word_list) == 1:
            self.__output_single_word_result_to_text_big(self, input_word)
        else:
            # output_confused_word_result_to_display_widget(input_word_list)

    def __output_single_word_result_to_text_show_all(self, word):
        translator = Translator(word, "youdao")
        word_dictionary = translator.get_result_dictionary()
        input_string = word_dictionary["word"] + "\n" + \
                       word_dictionary["translation"] + "<br/>" + word_dictionary["example_chinese"] + "\n" + \
                       word_dictionary["example_english"] + "\n" + \
                       word_dictionary["root"] + "\n"
        self.text_show_all.insert("end", input_string)
        self.text_show_all.insert("end", "-----------------\n")

window = Framework()
window.mainloop()