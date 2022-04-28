import codecs  # 读写utf-8
import re
import tkinter as tk
import urllib.request
from tkinter.filedialog import *

import pyexcel_xlsx
from bs4 import BeautifulSoup


class Methods:
    """各种小的方法函数"""

    @staticmethod
    def is_chinese(uchar):  # 找到中文UTF-8编码
        if '\u4e00' <= uchar <= '\u9fff':
            return True
        else:
            return False


class Translator:
    """将英文单词翻译成带有翻译、例句等的字典"""
    dictionary_type_tuple = ("bing", "iciba", "youdict")
    query_time_out = 30  # 在线字典访问超时时间
    __selected_dictionary_type = 0

    def __init__(self, word, dictonary_type):
        """初始化返回字典，选择需要使用的在线字典"""
        self.__word = ""
        self.__result_dictionary = {"word": word, "translation": "", "example_english": "", "example_chinese": "",
                                    "root": "", "vocabulary_range": ""}
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
        url = "http://cn.bing.com/dict/search?q=" + self.__result_dictionary["word"]
        response = urllib.request.urlopen(url, timeout=Translator.query_time_out)
        html = response.read().decode("utf-8")
        soup = BeautifulSoup(html, 'lxml')
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
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/100.0.4896.127 Safari/537.36"}
        url = "http://www.iciba.com/word?w=" + self.__result_dictionary["word"]
        req = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode("utf-8")
        soup = BeautifulSoup(html, 'lxml')
        # 目标词汇
        word = soup.find('h1', class_="Mean_word__hwr_g").text
        self.__result_dictionary["word"] = re.sub('\s', '', word)  # 将string中的所有空白字符删除
        # 在哪些词汇表中
        try:
            self.__result_dictionary["vocabulary_range"] = soup.find("p", class_="Mean_tag__K_C8K").text
        except AttributeError:
            self.__result_dictionary["vocabulary_range"] = "Unknown"
        # 释义
        express = ""
        expresses = soup.find_all('ul', class_='Mean_part__UI9M6')
        for item in expresses:
            express = item.text + express
        self.__result_dictionary["translation"] = re.sub('\s', '', express)
        # 词根
        root = ""
        try:
            for cnt, item in enumerate(soup.find(class_='Affix_affix__iiL_9').findAll("p")):
                root += item.text + " "
                if cnt == 2:
                    break
            self.__result_dictionary["root"] = root
        except AttributeError:
            self.__result_dictionary["root"] = "Unknown"
        # 例句：
        self.__result_dictionary["example_english"] = soup.find(class_="NormalSentence_sentence__Jr9aj").find(
            class_="NormalSentence_en__BKdCu").text
        self.__result_dictionary["example_chinese"] = soup.find(class_="NormalSentence_sentence__Jr9aj").find(
            class_="NormalSentence_cn__gyUtC").text

    def __youdict_dictionary(self):
        url = "http://www.youdict.com/w/" + self.__result_dictionary["word"]
        response = urllib.request.urlopen(url, timeout=Translator.query_time_out)
        html = response.read().decode("utf-8")
        soup = BeautifulSoup(html, 'lxml')
        # 目标词汇
        try:
            word = soup.find('h3', id="yd-word").text
            self.__result_dictionary["word"] = re.sub('\s', '', word)  # 将string中的所有空白字符删除
        except AttributeError:
            self.__result_dictionary["word"] = "No words found"
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
    word_list_type_dict = {'youdao': dict(file_type=[("txt文件", ".txt")], function=0),
                           'confused_words': dict(file_type=[("excel文件", ".xlsx")], function=1),
                           'eduic': dict(file_type=[("txt文件", ".txt")], function=2)}

    def __init__(self, file, word_list_type):
        self.__result_words_list = []

        if WordListProcessor.word_list_type_dict[word_list_type]["function"] == 0:
            self.__parse_youdao_words(file)
        elif WordListProcessor.word_list_type_dict[word_list_type]["function"] == 1:
            self.__parse_confused_words(file)
        elif WordListProcessor.word_list_type_dict[word_list_type]["function"] == 2:
            self.__parse_eudic_words(file)
        # 若增加解析器就加一个elif
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
        # with open(file, 'r', encoding="utf-8") as f1:  # 打开文件
        #     txt_string = f1.read()  # 读入文件内容到str1中
        f1 = open(file, 'r', encoding="utf-8")
        txt_string = f1.read()  # 读入文件内容到str1中
        for item in txt_string.split("\n"):
            if re.match(r'\d*, ', item):  # 提取出有单词的一项（这一行第一个是数字之后接着逗号之后是一个空格）
                item = item.split(" ")[1]  # 只要每项中的单词而不要序号和音标
                self.__result_words_list.append(item)  # 装入列表

    def __parse_eudic_words(self, file):
        with open(file, 'r', encoding="utf-8") as f1:  # 打开文件
            txt_string = f1.read()  # 读入文件内容到str1中
        for item in txt_string.split("\n"):
            if re.match(r'\d+@', item):
                item = item.split("@")[1]
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

        def place_message():
            # 信息输出框：
            self.message = tk.Message(text="Waiting for input", width=100)
            self.message.grid(row=1, column=3, columnspan=2, rowspan=2, sticky="N")

        def place_word_input_part():
            # 单词输入框+确认按钮
            self.entry_word = tk.Entry()
            self.entry_word.grid(row=0, column=2, columnspan=2, padx=0)

            self.button_word_confirm = tk.Button(text="Confirm", command=self.__command_button_word_confirm)
            self.button_word_confirm.grid(row=0, column=4)

        def place_label_vocabulary():
            # 词汇表（CET4，考研等）
            self.label_vocabulary = tk.Label(text="Vocabulary range")
            self.label_vocabulary.grid(row=2, column=0, columnspan=4, sticky="W", padx=10)

        def place_text_show_all():
            # 显示将要被导出的text
            self.text_show_all = tk.Text(width=60, height=28)
            self.text_show_all.grid(row=5, column=0, columnspan=6, rowspan=6, padx=10)

        def place_button_output_part():
            # 将text控件中的文档按单词本格式输出的按钮
            self.button_output_confirm = tk.Button(text="Output", command=self.__command_button_output_confirm)
            self.button_output_confirm.grid(row=12, column=3, columnspan=2)
            # 保存路径字符串
            self.output_path = tk.StringVar(self)
            # 路径选择label
            self.label_select_output_path = tk.Label(text="Select output path:")
            self.label_select_output_path.grid(row=12, column=0, padx=10)
            # 路径选择框
            self.entry_output_path = tk.Entry(self, textvariable=self.output_path)
            self.entry_output_path.grid(row=12, column=1)
            # 打开路径选择的按钮
            self.button_select_output_path = tk.Button(text="Select", command=self.__command_button_select_output_path)
            self.button_select_output_path.grid(row=12, column=2, sticky="W")

        def place_select_dictionary_part():
            # 选择词典控件
            self.label_source_choice = tk.Label(text="choice source :")
            self.label_source_choice.grid(row=0, column=0, sticky="W", padx=10)
            self.__selected_dictionary_type = tk.StringVar(self)
            self.__selected_dictionary_type.set(Translator.dictionary_type_tuple[1])  # default value
            self.option_menu_select_online_dictionary = tk.OptionMenu(self, self.__selected_dictionary_type,
                                                                      *Translator.dictionary_type_tuple,
                                                                      command=self.__command_option_menu_changed)
            self.option_menu_select_online_dictionary.grid(row=0, column=1, sticky="W")

        def place_input_word_book_part():
            # 导入单词本控件
            self.__activate_input_word_feature = False  # 是否启动导入单词功能标志位
            self.label_choice_word_book = tk.Label(text="choice word book :")
            self.label_choice_word_book.grid(row=1, column=0, sticky="W", padx=10)
            self.__selected_input_word_book_type = tk.StringVar(self)
            self.__selected_input_word_book_type.set("null")  # default value
            self.option_menu_select_input_word_book_type = tk.OptionMenu(self, self.__selected_input_word_book_type,
                                                                         *WordListProcessor.word_list_type_dict,
                                                                         command=self.__command_option_menu_changed)
            self.option_menu_select_input_word_book_type.grid(row=1, column=1, sticky="W")
            self.button_input_word_book_confirm = tk.Button(text="Off",
                                                            command=self.__command_button_input_word_book_confirm)
            self.button_input_word_book_confirm.grid(row=1, column=2, sticky="W")
            # 以下是隐藏的控件，当导入单词本时被.grid
            self.list_box_words_list = tk.Listbox(self, height=23)
            self.button_parse_list_box_words = tk.Button(text="confirm",
                                                         command=self.__command_button_parse_list_box_words)

        place_message()
        place_word_input_part()
        place_label_vocabulary()
        place_text_show_all()
        place_button_output_part()
        place_select_dictionary_part()
        place_input_word_book_part()

    def __output_query_result_to_text_show_all(self, query_string):
        def output_single_word_result_to_text_show_all(word):
            # 如果查询发生错误，直接返回
            try:
                translator = Translator(word, self.__selected_dictionary_type.get())
                word_dictionary = translator.get_result_dictionary()
            except Exception as e:
                self.message.config(text=str(e))
                raise e
                return
            input_string = "{0}\n{1}<br/>{2}\n{3}\n{4}\n".format(word_dictionary["word"],
                                                                 word_dictionary["translation"],
                                                                 word_dictionary["example_chinese"],
                                                                 word_dictionary["example_english"],
                                                                 word_dictionary["root"])
            self.text_show_all.insert("end", input_string)
            self.text_show_all.insert("end", "-----------------\n")
            self.label_vocabulary.config(text=word_dictionary["vocabulary_range"])

        def output_confused_words_list_result_to_text_show_all(word_list):
            word_dictionaries_list = []
            # 如果查询发生错误，直接返回
            try:
                for word in word_list:
                    translator = Translator(word, self.__selected_dictionary_type.get())
                    word_dictionaries_list.append(translator.get_result_dictionary())
            except Exception as e:
                self.message.config(text=str(e))
                return
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
            self.message.config(text="No input word detected")
            return
        # 当没有选择在线字典时，点击无效
        if self.__selected_dictionary_type.get() == "null":
            self.message.config(text="The online dictionary type has not been selected")
            return
        self.entry_word.delete(0, len(input_word))  # 清空输入框
        self.__output_query_result_to_text_show_all(input_word)

    # 点击导出按钮之后
    def __command_button_output_confirm(self):
        # 先检测路径是否存在
        if self.output_path.get() == "":
            self.message.config(text="No output path selected yet")
            return
        # 整理显示框中的字符串
        input_str = self.text_show_all.get("0.0", "end")
        input_str = input_str.replace("\n", "\t")
        input_str = input_str.replace("\t-----------------\t", "\r\n")
        input_str = input_str[0:-1]  # 去掉最后一个\t
        # 追加写入
        fo = codecs.open(self.output_path.get() + "/Anki_words.txt", "a+", "utf-8")
        fo.write(input_str)
        fo.close()
        self.message.config(text="Output completed")
        self.text_show_all.delete("0.0", "end")  # 清空显示区

    def __command_button_input_word_book_confirm(self):
        if self.__activate_input_word_feature is False:
            # 当没有选择导入方式时，操作无效
            if self.__selected_input_word_book_type.get() == "null":
                self.message.config(text="The word book type has not been selected")
                return
            self.__activate_input_word_feature = True
            self.button_input_word_book_confirm.config(text="On")
            self.__configuring_panel_size("large")
            self.list_box_words_list.grid(row=5, column=6)  # 放置列表控件
            self.button_parse_list_box_words.grid(row=12, column=6)  # 放置确认导入按钮
            # 当原来的列表为空时再次打开文件选择框，否则不重新选择文件
            if self.list_box_words_list.size() == 0:
                # 打开文件选择框
                try:
                    file = askopenfilename(
                        filetypes=WordListProcessor.word_list_type_dict
                        [self.__selected_input_word_book_type.get()]['file_type'])
                    word_list_processor = WordListProcessor(file, self.__selected_input_word_book_type.get())
                    query_list = word_list_processor.get_result_words_list()
                    for words in query_list:
                        self.list_box_words_list.insert('end', words)  # 装入列表
                except Exception as e:
                    self.message.config(text=str(e))
                    self.__command_button_input_word_book_confirm()
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
                self.message.config(text="The word book type has not been selected")
                return
            list_item = self.list_box_words_list.get(0)
            self.list_box_words_list.delete(0)  # 删除第一个位置的字符
            self.__output_query_result_to_text_show_all(list_item)

    def __command_option_menu_changed(self, event):
        """改变字典选择项之后"""
        self.message.config(text="select " + event)

    def __command_button_select_output_path(self):
        """点击选择输出路径之后"""
        self.output_path.set(askdirectory())


window = Framework()
window.title("Anki assistant")
window.mainloop()
