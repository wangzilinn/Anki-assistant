import tkinter as tk
from tkinter.filedialog import *
import urllib.request
import re
import codecs  # 读写utf-8
from bs4 import BeautifulSoup
import pyexcel_xlsx


class Translator:
    """将英文单词翻译成带有翻译、例句等的字典"""
    dictionary_type_tuple = ("bing", "iciba", "youdict")
    __selected_dictionary_type = 0

    def __init__(self, word, dictonary_type):
        """初始化返回字典，选择需要使用的在线字典"""
        self.__word = ""
        self.__result_dictionary = {"word": word, "translation": "", "example_english": "", "example_chinese": "",
                                    "root": "", "vocabulary_range": "", "error": "no error"}
        # 装填字典
        self.__load_result_dictionary(dictonary_type)

    def __load_result_dictionary(self, dictionary_type):
        if self.dictionary_type_tuple[0] == dictionary_type:
            self.__bing_dictionary()
        elif self.dictionary_type_tuple[1] == dictionary_type:
            self.__iciba_dictionary()
        elif self.dictionary_type_tuple[2] == dictionary_type:
            self.__youdict_dictionary()
        else:
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
            self.__result_dictionary["vocabulary_range"] = soup.find(style="margin-bottom:6px;").text.split("\n")[
                1]  # 删除这个句子中的回车
        except AttributeError:
            self.__result_dictionary["vocabulary_range"] = "Unknown"
        # 释义:
        try:
            expresses = soup.find(id='yd-word-meaning')
            express = ""
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


class WordListProcessor:
    """解析导入的单词本,返回单词数组"""
    word_list_tuple = ("youdao", "confuesd_words")
    file_types = [("excel文件", ".xlsx"), ("txt文件", ".txt")]

    def __init__(self, file, word_list_type):
        self.__result_words_list = []
        if WordListProcessor.word_list_tuple[0] == word_list_type:
            self.__parse_youdao_words(file)
        elif WordListProcessor.word_list_tuple[1] == word_list_type:
            self.__parse_confused_words(file)
        else:
            pass

    def __parse_confused_words(self, file):
        xls_data = pyexcel_xlsx.get_data(file)
        for sheet in xls_data.keys():
            excel_list = xls_data[sheet]
            for words in excel_list:
                line_str = ""
                for word in words:
                    line_str = line_str + "-" + word
                self.__result_words_list.append(line_str[1:])
            break  # 仅返回第一个表

    def __parse_youdao_words(self, file):
        with open(file, 'r', encoding="utf-8") as f1:  # 打开文件
            txt_string = f1.read()  # 读入文件内容到str1中
        for item in txt_string.split("\n"):
            if re.match(r'\d*, ', item):  # 提取出有单词的一项（这一行第一个是数字之后接着逗号之后是一个空格）
                item = item.split(" ")[1]  # 只要每项中的单词而不要序号和音标
                self.__result_words_list.append(item)  # 装入列表

    def get_result_words_list(self):
        return self.__result_words_list


class Framework(tk.Tk):
    """框架结构"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.__configuring_panel_size("normal")
        self.__place_widgets()

    def __configuring_panel_size(self, mode="normal"):
        if mode == "large":
            self.geometry("605x500")  # 扩大窗口以显示列表控件
        elif mode == "normal":
            self.geometry("445x500")
        else:
            pass

    def __place_widgets(self):
        """放置各种widgets"""

        # 单词输入框+确认按钮
        self.entry_word = tk.Entry()
        self.entry_word.grid(row=0, column=2)

        self.button_word_confirm = tk.Button(text="confirm", command=self.__command_button_word_confirm)
        self.button_word_confirm.grid(row=0, column=3)

        # 词汇表（CET4，考研等）
        self.label_vocabulary = tk.Label()
        self.label_vocabulary.grid(row=4, column=0, columnspan=4, sticky=W, padx=10)

        # 显示将要被导出的text
        self.text_show_all = tk.Text(width=60, height=24)
        self.text_show_all.grid(row=5, column=0, columnspan=6, rowspan=6, padx=10)

        # 将text控件中的文档按单词本格式输出
        self.button_output_confirm = tk.Button(text="output", command=self.__command_button_output_confirm)
        self.button_output_confirm.grid(row=12, column=2, pady=10)

        # 选择词典控件
        self.label_source_choice = tk.Label(text="choice source :")
        self.label_source_choice.grid(row=0, column=0)
        self.__selected_dictionary_type = tk.StringVar(self)
        self.__selected_dictionary_type.set("null")  # default value
        self.option_menu_select_online_dictionary = tk.OptionMenu(self, self.__selected_dictionary_type,
                                                                  *Translator.dictionary_type_tuple)
        self.option_menu_select_online_dictionary.grid(row=0, column=1)

        # 导入单词本控件
        self.__activate_input_word_feature = False  # 是否启动导入单词功能标志位
        self.label_choice_word_book = tk.Label(text="choice word book :")
        self.label_choice_word_book.grid(row=1, column=0)
        self.__selected_input_word_book_type = tk.StringVar(self)
        self.__selected_input_word_book_type.set("null")  # default value
        self.option_menu_select_input_word_book_type = tk.OptionMenu(self, self.__selected_input_word_book_type,
                                                                     *WordListProcessor.word_list_tuple)
        self.option_menu_select_input_word_book_type.grid(row=1, column=1)
        self.button_input_word_book_confirm = tk.Button(text="Off",
                                                        command=self.__command_button_input_word_book_confirm)
        self.button_input_word_book_confirm.grid(row=1, column=3)
        # 以下是隐藏的控件，当导入单词本时被.grid
        self.list_box_words_list = tk.Listbox(self, height=19)
        self.button_parse_list_box_words = tk.Button(text="confirm",
                                                     command=self.__command_button_parse_list_box_words)

    def __output_query_result_to_text_show_all(self, query_string):
        def output_single_word_result_to_text_show_all(word):
            translator = Translator(word, self.__selected_dictionary_type.get())
            word_dictionary = translator.get_result_dictionary()
            input_string = word_dictionary["word"] + "\n" + \
                           word_dictionary["translation"] + "<br/>" + word_dictionary["example_chinese"] + "\n" + \
                           word_dictionary["example_english"] + "\n" + \
                           word_dictionary["root"] + "\n"
            self.text_show_all.insert("end", input_string)
            self.text_show_all.insert("end", "-----------------\n")

            self.label_vocabulary.config(text=word_dictionary["vocabulary_range"])

        def output_confused_words_list_result_to_text_show_all(word_list):
            word_dictionaries_list = []
            for word in word_list:
                translator = Translator(word, self.__selected_dictionary_type.get())
                word_dictionaries_list.append(translator.get_result_dictionary())
            input_string = ""
            # words:
            for word_dictionary in word_dictionaries_list:
                input_string = input_string + word_dictionary["word"] + "<---->"
            input_string = input_string[:-6] + "\n"
            # translation:
            for word_dictionary in word_dictionaries_list:
                input_string = input_string + word_dictionary["translation"] + "<br/>" + \
                               word_dictionary["example_chinese"] + "<br/><----><br/>"
            input_string = input_string[:-16] + "\n"
            # example:
            for word_dictionary in word_dictionaries_list:
                input_string = input_string + word_dictionary["example_english"] + "<br/><----><br/>"
            input_string = input_string[:-16] + "\n"
            # root:
            for word_dictionary in word_dictionaries_list:
                input_string = input_string + word_dictionary["root"] + "<br/><----><br/>"
            input_string = input_string[:-16] + "\n"
            self.text_show_all.insert("end", input_string)
            self.text_show_all.insert("end", "-----------------\n")
        input_words_list = query_string.split("-")
        if len(input_words_list) == 1:
            output_single_word_result_to_text_show_all(input_words_list[0])
        else:
            output_confused_words_list_result_to_text_show_all(input_words_list)

    def __command_button_word_confirm(self):
        input_word = self.entry_word.get()
        # 当没有输入时，点击无效
        if len(input_word) == 0:
            return
        # 当没有选择在线字典时，点击无效
        if self.__selected_dictionary_type.get() == "null":
            return
        self.entry_word.delete(0, len(input_word))  # 清空输入框
        self.__output_query_result_to_text_show_all(input_word)


    # 点击导出按钮之后
    def __command_button_output_confirm(self):
        input_str = self.text_show_all.get("0.0", "end")
        input_str = input_str.replace("\n", "\t")
        input_str = input_str.replace("\t-----------------\t", "\r\n")
        fo = codecs.open("C:\\Users\\78286\\Desktop\\foo.txt", "a+", "utf-8")
        fo.write(input_str[0:-1])  # 去掉最后一个\t
        fo.close()
        self.text_show_all.delete("0.0", "end")  # 清空显示区

    def __command_button_input_word_book_confirm(self):
        if self.__activate_input_word_feature is False:
            # 当没有选择导入方式时，操作无效
            if self.__selected_input_word_book_type.get() == "null":
                return
            self.__activate_input_word_feature = True
            self.button_input_word_book_confirm.config(text="On")
            self.__configuring_panel_size("large")
            self.list_box_words_list.grid(row=5, column=6)  # 放置列表控件
            self.button_parse_list_box_words.grid(row=12, column=6)  # 放置确认导入按钮
            file = askopenfilename(filetypes=WordListProcessor.file_types)
            word_list_processor = WordListProcessor(file, self.__selected_input_word_book_type.get())
            query_list = word_list_processor.get_result_words_list()
            for words in query_list:
                self.list_box_words_list.insert('end', words)  # 装入列表
        else:
            self.__activate_input_word_feature = False
            self.__configuring_panel_size("normal")
            self.list_box_words_list.grid_forget()  # 隐藏确认导入按钮
            self.button_parse_list_box_words.grid_forget()
            self.button_input_word_book_confirm.config(text="Off")

    def __command_button_parse_list_box_words(self):
        """当点击listbox下边的确认按钮之后"""
        if self.list_box_words_list.size() > 0:
            # 当没有选择字典时，不进行操作
            if self.__selected_dictionary_type.get() == "null":
                return
            list_item = self.list_box_words_list.get(0)
            self.list_box_words_list.delete(0)  # 删除第一个位置的字符
            self.__output_query_result_to_text_show_all(list_item)







window = Framework()
window.mainloop()
