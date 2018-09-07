# Anki assistant
从在线必应词典/爱词霸/youdict爬取信息生成Anki可用的单词本
### 第五版界面：
#### 初始界面:
![image](https://github.com/wangzilinn/Anki-assisent/blob/master/example%20pictures/%E5%88%9D%E5%A7%8B%E7%95%8C%E9%9D%A2.png)
#### 查询单个词
![image](https://github.com/wangzilinn/Anki-assisent/blob/master/example%20pictures/%E6%9F%A5%E8%AF%A2%E5%8D%95%E4%B8%AA%E8%AF%8D.png)
#### 查询混淆词
![image](https://github.com/wangzilinn/Anki-assisent/blob/master/example%20pictures/%E6%9F%A5%E8%AF%A2%E6%B7%B7%E6%B7%86%E8%AF%8D.png)
#### 导入混淆词
![image](https://github.com/wangzilinn/Anki-assisent/blob/master/example%20pictures/%E8%A7%A3%E6%9E%90%E5%AF%BC%E5%85%A5%E7%9A%84%E6%B7%B7%E6%B7%86%E8%AF%8D.png)
#### 解析导入的混淆词
![image](https://github.com/wangzilinn/Anki-assisent/blob/master/example%20pictures/%E5%AF%BC%E5%85%A5%E6%B7%B7%E6%B7%86%E8%AF%8Dexcel.png)
### 第五版功能：
1. 导入有道单词本
2. 导入混淆词excel(示例文件在库中test.xlsx)
3. 从在线词典youdao，iciba，youdict中查询或输入导入的单词
4. 输出为Anki单词本

### 之前版本的记录：
#### 最近这几天每天都在背单词，发现了按照记忆曲线复习的单词本anki，觉得简直是神器，几天下来背单词的效率提高了不少。
#### 但是每天把单词添加到单词本要花费不少时间，其典型过程是：
1. 找到要背的单词
2. 去百度/谷歌/必应搜索释义、例句等
3. 把搜索到的东西粘贴到单词本上
为了加深印象，很多步骤都是手打，而不是直接复制（后来发现并没有什么卵用）

### 为了节省时间，又拿起了许久不用的python写了个带图形界面的脚本，界面很简单，包括：
1. 单词查询控件
2. 确认按钮
3. 查询结果区
4. 生成单词本按钮

### 操作方法：
1. 将要添加的单词或单词本导入
2. confirm
3. 所有单词添加完毕后，output

### 程序流程：
1. 获取用户单词或单词本
2. 去在线词典网站爬取该单词的释义与例句
3. 格式化爬取数据
4. 输出到文件

### 修改源码时注意：
1. 源码已经放上了，需要一些不是自带的的库
2. 输出位置默认放到桌面
3. 未使用百度和google翻译的原因是他们网站都做了处理（混淆和ajax），图省事用了bing
4. anki输出需要utf-8格式的输出，所以普通的打开文件操作是不行滴，要使用import codecs库

### 随笔
从产生需求到第二版,这两天一边写一边谷歌扫盲,花了大概5个小时,这种隔一年半载再拿起一种语言的感觉很奇妙,写惯了c/c++再写python有种带着学步车走路的感觉.
代码都是起床没睡醒和晚上睡不着的时候写的,命名,单词拼写,程序结构难免有不合理的地方,本着能用就行,适当拓展的原则(自用软件,给老板干活另说),这个库就先这样吧,以后除非网站都挂掉,不会再更新了
上面的FLAG说倒就倒，在实际使用中发现了在很多中情况下的闪退现象，已经修复
添加了查看该单词属于那个考试范围的label
2018年9月6日：使用面向对象整体重构了软件，增加了不少新功能，对python的常见特性已经比较熟悉了
