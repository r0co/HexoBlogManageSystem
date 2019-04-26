import re
import os
class Config(object):
    # def __init__(self):
    #     self.__get_config()
    #     self.__get_md_path()
    #     self.__get_all_md_attribute()
    def __get_config(self):
        # TODO: 获取配置文件信息
        config_arr = []
        pattern = r'([A-z]*) : (.*)'
        config_data = open("../config/config.ini").readlines()
        for line in config_data:
            key = re.search(pattern, line).group(1)
            value = re.search(pattern, line).group(2)
            config_arr.append((key, value))
        self.__conf_dict = dict(config_arr)

    def __get_md_path(self):
        # TODO: 获取指定文件夹下的.md文件的的绝对路径
        self.__files_path = []
        path = input("[!] 请输入source/_posts文件夹的绝对路径:")
        try:
            files_info = os.walk(path)
        except:
            print("路径有误")
            return
        for root, dirs, files in files_info:
            for file in files:
                if file[-3:] == '.md':
                    self.__files_path.append(file)
        if not self.__files_path:
            print("[!] 没有找到markdown文件")
        else:
            print("[√] 本次扫描到的md文件如下：")
            for i in self.__files_path:
                print(i)

    def get_md_attribute(self, file_path):
        # TODO: 获取md文件中的属性（如标签、分类）
        # params: 文件绝对路径
        self.__md_attributes_dict = []
        title = ''
        author = ''
        tags = []
        categories = []
        # 下列两项用于标记匹配到的字符属于tags还是categories。1为属于，0为不属于
        tags_status = 1
        categories_status = 1
        common_pattern = r'([A-z]*):[\s]*(.*)'
        special_pattern = r'^[\s-]*(.*)'
        md_data = open(file_path).readlines()
        # i = 1
        for line in md_data:
            # print("第{}行的内容为:\n{}\ntags={},cat={}".format(i, line[:-1], tags_status, categories_status))
            # i += 1
            if line[0:3] == '---':
                break
            try:
                first_attr = re.search(common_pattern, line).group(1)
            except:
                first_attr = ""
            try:
                second_attr = re.search(common_pattern, line).group(2)
            except:
                second_attr = ""
            # print("第一个参数为:"+first_attr)
            # print("第二个参数为："+second_attr)
            if tags_status == 1 and line[0:3] == '  -':
                tags.append(re.search(special_pattern, line).group(1))
            else:
                tags_status = 0
            if categories_status == 1 and line[0:3] == '  -':
                categories.append(re.search(special_pattern, line).group(1))
            else:
                categories_status = 0
            if first_attr == 'tags':
                tags_status = 1
            if first_attr == 'categories':
                categories_status = 1
            if first_attr == 'title':
                itle = second_attr
            if first_attr == 'author':
                author = second_attr
            # print(tags)
            # print(categories)
        self.__md_attributes_dict.append(["标题", title])
        self.__md_attributes_dict.append(["作者", author])
        self.__md_attributes_dict.append(["标签", tags])
        self.__md_attributes_dict.append(["分类", categories])
        # print("标题:" + title)
        # print("作者：" + author)
        # print("标签")
        # print(tags)
        # print("分类")
        # print(categories)


    def __get_all_md_attribute(self):
        self.__files_all_attribute = []
        for file in self.__files_path:
            self.__files_all_attribute.append(self.__get_md_attribute(file))
        print(self.__files_all_attribute)

a = Config()
a.get_md_attribute("D:\桌面图标\项目\HexoBlogManageSystem\TEST.md")
class Db(Config):
    def __init__(self):
        self.__conn = pymysql.connect(self.__conf_dict['host'], self.__conf_dict['username'], self.__conf_dict['password'],
                                      self.__conf_dict['dbname'])
        self.__conn_obj = self.__conn.cursor()

    def exec_sql(self, sentence):
        self.__conn.execute(sentence)
        return self.__conn.fetchall()

    def refresh_db_table(self):
        drop_sql = "drop table if exists hexo_manager"
        try:
            self.exec_sql(drop_sql)
            print("[*] 删除数据表hexo_manager成功")
        except:
            print("[!] 删除数据表hexo_manager失败")
        create_sql = """
            create table hexo_manager(
            id int(5) not null auto_increment,
            title varchar(20) not null,
            author varchar(10),
            tags varchar(10),
            categories varchar(20),
            primary key (id)
            )
            """
        try:
            self.exec_sql(create_sql)
            print("[*] 创建数据表hexo_manager成功")
        except:
            print("[!] 创建数据表hexo_manager失败")