import re
import pymysql
import shutil
import os


class Config(object):
    """
    属性说明：
    __conf_dict : 存储config.ini中的配置信息
    __files_path_list : 存储被扫描到的md文件的绝对路径
    __md_attributes_dict : 存储扫描到的单个md文件的属性
    __files_all_attribute_list : 存储所有md文件的属性

    方法说明：
    __init__() : 初始化Config类的属性并获取配置文件信息
    scan() : 给Config类的属性赋值
    __match_config() : 获取配置文件信息
    __match_md_path() : 获取指定文件夹下md文件的绝对路径
    __match_md_attribute() : 获取md文件的属性（title、tags等）
    __collect_all_md_attribute() : 获取全部md文件的属性
    get_config() : 返回__conf_list
    get_all_md_path() : 返回__files_path_list
    get_all_md_attribute() : 获取__files_all_attribute_list
    """
    def __init__(self):
        # TODO:初始化所需属性
        self.__conf_dict = {}  # 存储config.ini中的配置信息
        self.__files_path_list = []  # 存储扫描到的md文件绝对路径
        self.__md_attributes_dict = {}  # 存储扫描到的单个md文件的属性
        self.__files_all_attribute_list = []  # 存储所有md文件的属性
        self.__match_config()

    def scan(self):
        # TODO: 整合所有用来扫描的方法，目的是给Config类的属性赋值
        self.__match_md_path()
        self.__collect_all_md_attribute()

    def __match_config(self):
        # TODO: 获取配置文件信息
        print("[*] 获取配置文件中....")
        config_list = []
        pattern = r'([A-z_]*) : (.*)'
        try:
            config_data = open("./config/config.ini").readlines()
        except:
            print("[×] 打开配置文件失败")
            return
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
        for root, dirs, files in files_info:
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
    """
    属性说明：
    __conn : 数据库连接对象
    __conn_cursor : 数据库操作游标
    __current_db_info_list : 存储当前数据库中的文章信息。每个文章均为列表中的一个元素，其属性均以字典形式存储

    方法说明：
    conn() : 连接数据库
    no_need_commit_sql() : 执行无需调用commit方法的sql语句，例如创建、查询
    need_commit_sql() : 执行需调用commit方法的sql语句，例如插入、更新、删除
    reset_db_table() : 重置程序相关数据表
    store_attribute() : 存储读取到的md文件属性信息
    get_current_data() : 读取当前数据库中的文章信息
    change_file() : 将md文件的属性更改为数据库中记录的属性
    """

    def conn(self):
        # TODO: 创建数据库连接__conn_obj
        config = self.get_config()
        print("[*] 正在建立数据库连接....")
        try:
            self.__conn = pymysql.connect(config['host'], config['username'], config['password'], config['dbname'])
        except:
            print("[×] 数据库连接失败")
            return False
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

    def get_current_data(self):
        # TODO: 读取当前数据库中的文章信息
        self.__current_db_info_list = []  # 存储当前数据库中的文章信息。每个文章的属性均以字典形式存储
        tags_info_list = []
        categories_info_list = []
        get_articles = "select id,title,author from articles"
        articles_data = self.no_need_commit_sql(get_articles, False)
        for article in articles_data:
            article = list(article)
            article_id = article[0]
            get_tags = "select tag_name from tags where belong_to = {}".format(article_id)
            tags = self.no_need_commit_sql(get_tags, False)
            for tag in tags:
                tags_info_list.append(list(tag))
            get_categories = "select category_name from categories where belong_to = {}".format(article_id)
            categories = self.no_need_commit_sql(get_categories, False)
            for category in categories:
                categories_info_list.append(list(category))
            total_info = {}  # 记录每个文章所有的属性
            total_info['title'] = article[1]
            total_info['author'] = article[2]
            total_info['tags'] = tags_info_list
            total_info['categories'] = categories_info_list
            print("查看当前状态:")
            print(total_info)
            self.__current_db_info_list.append(total_info)

    def change_file(self):
        # TODO: 将md文件的属性修改为数据库中记录的属性
        title_pattern = r"(^title:\s)(.*)"
        author_pattern = r"^(^author:\s)(.*)"
        tags_pattern = r"^tags:"
        categories_pattern = r"^categories:"
        child_pattern = r"\s\s-\s"  # 用于匹配tags和categories的子目录
        changed_file_data = ""  # 存放更改后的文件内容
        if self.get_all_md_path() == []:
            print('[×] 未检测到文件路径信息，请扫描后再进行修改操作')
            return False
        print("[*] 正在备份原文件....")
        file_count = 0
        for md_file in self.get_all_md_path():
            try:
                shutil.copy(md_file, md_file+".bak")
                print("[√] 备份{}成功！".format(md_file))
                file_count += 1
            except:
                print("[×] 备份{}失败".format(md_file))
                return False
        print("[√] 文件备份已完成，本次共备份{}个文件".format(file_count))
        print("[*] 开始修改文件")
        for md_file in self.get_all_md_path():
            print("[*] 开始执行对{}的操作".format(md_file))
            try:
                file = open(md_file, 'r', encoding='utf8')
            except:
                print("[×] 打开{}失败".format(md_file))
                return False
            ending_flag = False  # 用于判断md文件的属性部分是否结束。结束为True，反之为False
            # 获取文章标题
            title = re.search(title_pattern, file.readline())
            title_exist = False  # 标志该文件中的title是否存在于数据库中
            # 遍历存储当前数据库文章信息的数组
            for article_info in self.__current_db_info_list:
                # 如果文章中存在此title，则进行下一步操作，否则跳出该次循环
                if article_info['title'] == title:
                    title_exist = True
                    # 遍历该文件的每一行
                    for line in file.readlines():
                        # 如果还未遍历完文件的所有属性，则继续
                        if not ending_flag:
                            # 如果该行控制title
                            if re.match(title_pattern, line)[1] == 'title: ':
                                # 将‘title: ’后的字段替换为数据库中存放的title，后面的都一样，我就不啰嗦了
                                changed_file_data += line.replace(re.match(title_pattern, line)[2], article_info['title'])
                            elif re.match(author_pattern, line)[1] == 'author: ':
                                changed_file_data += line.replace(re.match(author_pattern, line)[2], article_info['author'])
                            # 如果匹配到tags，则遍历数据库中tags字段信息并进行插入
                            elif re.match(tags_pattern, line) == 'tags:':
                                changed_file_data += line
                                for child_tag in article_info['tags']:
                                    changed_file_data += '  - ' + child_tag + '\n'
                            # 如果匹配到categories，则遍历数据库中categories字段信息并进行插入
                            elif re.match(categories_pattern, line) == 'categories:':
                                changed_file_data += line
                                for child_category in article_info['categories']:
                                    changed_file_data += '  - ' + child_category + '\n'
                            # 如果扫描到"---"，则说明文件属性部分已结束，停止扫描
                            elif line[0:3] == '---':
                                ending_flag = True
                        # 已遍历完文件属性，接下来将所有行加入changed_file_data即可
                        else:
                            changed_file_data += line
                        # 将改动写入该文件中
                        file.write(changed_file_data)
                        file.close()
                        print('[√] 已完成对{}的更改'.format(md_file))
             # 如果数据库记录中不存在该文件的title则报错并退出
            if not title_exist:
                print("[×] 在数据库中没有找到该文章的相关信息")
                return False
        print("[SUCCESS] 所有文件均已处理完毕")

