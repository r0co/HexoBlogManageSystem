# coding=utf-8
import re
import os
import pymysql


class Config(object):
    def __init__(self):
        # TODO:初始化所需属性
        self.__conf_dict = {}
        self.__files_path_list = []
        self.__md_attributes_dict = {}
        self.__files_all_attribute_list = []
        self.__match_config()

    def scan(self):
        # TODO: 整合所有用来扫描的方法，最后返回扫描结果
        self.__match_md_path()
        self.__collect_all_md_attribute()

    def __match_config(self):
        # TODO: 获取配置文件信息
        print("[*] 获取配置文件中....")
        config_list = []
        pattern = r'([A-z_]*) : (.*)'
        config_data = open("../config/config.ini").readlines()
        for line in config_data:
            key = re.search(pattern, line).group(1)
            value = re.search(pattern, line).group(2)
            config_list.append((key, value))
        self.__conf_dict = dict(config_list)
        if self.__conf_dict is not []:
            print("[√] 获取配置文件成功")
        else:
            print("[×] 获取配置文件异常")

    def __match_md_path(self):
        # TODO: 获取指定文件夹下所有.md文件的的绝对路径
        path = self.__conf_dict['dir_path']
        print("[*] 正在扫描{}中含有的markdown文件....".format(path))
        files_info = os.walk(path)
        # try:
        #     files_info = os.walk(path)
        # except:
        #     print("路径有误")
        #     return
        # for root, dirs, files in files_info:
        for root, dirs, files in files_info:
            # print(root)
            # print(dirs)
            # print(files)
            # print("============")
            for file in files:
                if file[-3:] == '.md':
                    self.__files_path_list.append(root + '\\' + file)
        if self.__files_path_list is not []:
            print("[√] 已完成对{}下全部markdown文件的扫描，扫描结果如下:".format(self.__conf_dict['dir_path']))
            for i in self.__files_path_list:
                print("======> {}".format(i))
        else:
            print("[×] {}目录下markdown文件扫描异常".format(self.__conf_dict['dir_path']))

    def __match_md_attribute(self, file_path):
        # TODO: 获取md文件中的属性（如标签、分类）
        # params: 文件绝对路径
        md_attributes_list = []
        title = ''
        author = ''
        tags = []
        categories = []
        # 下列两项用于标记匹配到的字符属于tags还是categories。1为属于，0为不属于
        tags_status = 1
        categories_status = 1
        common_pattern = r'([A-z]*):[\s]*(.*)'
        special_pattern = r'^[\s-]*(.*)'
        md_data_bin = open(file_path, "rb").readlines()
        for line_bin in md_data_bin:
            line = line_bin.decode('utf8')
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
                title = second_attr
            if first_attr == 'author':
                author = second_attr
            # print(tags)
            # print(categories)
        if title is not "":
            md_attributes_list.append(["title", title])
            md_attributes_list.append(["author", author])
            md_attributes_list.append(["tags", tags])
            md_attributes_list.append(["categories", categories])
            md_attributes_dict = dict(md_attributes_list)
            if md_attributes_dict is not {}:
                print("[√] 扫描{}文件成功".format(file_path))
                return md_attributes_dict
            else:
                print("[×] 扫描{}出现异常".format(file_path))
        else:
            print("[!] 文件{}无title字段，自动跳过".format(file_path))

    def __collect_all_md_attribute(self):
        # TODO: 通过遍历每个md文件来获取md文件中的属性
        for file_path in self.__files_path_list:
            print("[*] 正在扫描{}".format(file_path))
            md_attribute_res = self.__match_md_attribute(file_path)
            if md_attribute_res is not None:
                self.__files_all_attribute_list.append(md_attribute_res)

    def get_config(self):
        # TODO: 为子类提供配置信息
        return self.__conf_dict

    # def get_all_md_attribute(self):
    #     # TODO: 为子类提供source/_post下所有.md文件的属性信息
    #     return self.__files_all_attribute_list

    def get_all_md_path(self):
        # TODO: 为子类提供source/_post下所有.md文件的路径信息
        return self.__files_path_list

    def get_all_md_attribute(self):
        return self.__files_all_attribute_list


class Db(Config):
    # def __init__(self):
    #     self.conn()
    def conn(self):
        # TODO: 创建数据库连接__conn_obj
        print("[*] 正在建立数据库连接....")
        config = self.get_config()
        self.__conn = pymysql.connect(config['host'], config['username'], config['password'], config['dbname'])
        # 生成操作游标
        self.__conn_cursor = self.__conn.cursor()
        if self.__conn_cursor is not None:
            print("[√] 数据库连接成功")

    def no_need_commit_sql(self, sentence, prompt=True):
        # TODO: 执行无需调用commit方法的sql语句
        try:
            self.__conn_cursor.execute(sentence)
            if prompt:
                print("[√] 执行成功")
        except:
            print("[×] 执行失败")
        # 若有回显则返回回显，否则直接返回
        try:
            res = self.__conn_cursor.fetchall()
            return res
        except:
            return None

    def need_commit_sql(self, sentence, prompt=True):
        # TODO: 执行需要调用commit方法的sql语句
        try:
            self.__conn_cursor.execute(sentence)
            self.__conn.commit()
            if prompt:
                print("[√] 执行成功")
        except:
            # 执行失败则回滚
            self.__conn.rollback()
            print("[×] 执行失败")

    def reset_db_table(self):
        # TODO: 重置articles、tags、categories表
        drop_articles = "drop table if exists articles"
        drop_tags = "drop table if exists tags"
        drop_categories = "drop table if exists categories"
        try:
            print("[*] 正在删除数据表articles....")
            self.need_commit_sql(drop_articles)
        except:
            print("[×] 删除数据表article失败")
        try:
            print("[*] 正在删除数据表tags....")
            self.need_commit_sql(drop_tags)
        except:
            print("[×] 删除数据表tags失败")
        try:
            print("[*] 正在删除数据表categories....")
            self.need_commit_sql(drop_categories)
        except:
            print("[×] 删除数据表categories失败")
        create_articles = """
        create table articles(
        id int(5) not null auto_increment,
        title varchar(20) not null,
        author varchar(10),
        primary key (id)
        )
        """
        create_tags = """
        create table tags(
        id int(5) not null auto_increment,
        tag_name varchar(20) not null,
        belong_to int(5) not null,
        primary key (id)
        )
        """
        create_categories = """
        create table categories(
        id int(5) not null auto_increment,
        category_name varchar(20) not null,
        belong_to int(5) not null,
        primary key (id)
        )
         """
        try:
            print("[*] 正在创建数据表articles....")
            self.no_need_commit_sql(create_articles)
        except:
            print("[×] 创建数据表articles失败")
        try:
            print("[*] 正在创建数据表tags....")
            self.no_need_commit_sql(create_tags)
        except:
            print("[×] 创建数据表tags失败")
        try:
            print("[*] 正在创建数据表categories....")
            self.no_need_commit_sql(create_categories)
        except:
            print("[×] 创建数据表categories失败")

    def test(self):
        print(self.get_all_md_path())

    def store_attribute(self):
        # TODO: 存储读取到的md文件属性信息
        md_attribute_items = self.get_all_md_attribute()
        if md_attribute_items is not []:
            print("[√] 文件扫描已完成")
        else:
            print("[×] 文件扫描出现异常，无法获取markdown文件信息")
            return
        file_count = 0
        item_count = 1  # 用于显示插入文件的进度
        for each_item in md_attribute_items:
            title = each_item['title']
            author = each_item['author']
            tags = each_item['tags']
            categories = each_item['categories']
            insert_into_aritcle = """
            insert into articles(title,author) 
            values(
            '{title}','{author}'
            )
            """.format(title=title, author=author)
            print("[*] 正在向articles表中插入第{item_count}个文件的信息....".format(item_count=item_count))
            self.need_commit_sql(insert_into_aritcle)
            query_article_id = "select id from articles where title = '{title}'".format(title=title)
            article_id_tuple = self.no_need_commit_sql(query_article_id, False)
            try:
                assert len(article_id_tuple) == 1
                article_id = article_id_tuple[0][0]
            except:
                print("[FAILURE] 数据错误，请检查是否有重复的title字段")
                return
            print("[*] 正在向tags表中插入第{item_count}个文件的信息....".format(item_count=item_count))
            for tag in tags:
                insert_into_tags = """
                insert into tags(tag_name,belong_to)
                values(
                '{tag_name}','{belong_to}'
                )
                """.format(tag_name=tag, belong_to=article_id)
                self.need_commit_sql(insert_into_tags, False)
            print("[*] 正在向categories表中插入第{item_count}个文件的信息....".format(item_count=item_count))
            for category in categories:
                insert_into_categories = """
                insert into categories(category_name,belong_to)
                values(
                '{category_name}','{belong_to}'
                )
                """.format(category_name=category, belong_to=article_id)
                self.need_commit_sql(insert_into_categories, False)
            print("[√] 第{}个文件的内容已全部存入数据库".format(item_count))
            file_count += 1
        print("[SUCCESS] 完成数据存储任务，本次共存储{}个文件的信息".format(file_count))

# # 存储文件数据测试
# a = Db()
# a.conn()
# a.scan()
# a.reset_db_table()
# a.store_attribute()
