from manager.Config import Config
import pymysql
import re
import shutil


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
    reset_db() : 重置程序相关数据表
    store_attribute() : 存储读取到的md文件属性信息
    get_current_data() : 读取当前数据库中的文章信息
    get_conn() : 获取数据库连接
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
        """
        :param sentence: 需执行的sql语句
        :param prompt: 为True则输出提示，否则不输出提示
        :return:
        """
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
        """
        :param sentence: 需执行的sql语句
        :param prompt: 为True则输出提示，否则不输出提示
        :return:
        """
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

    def reset_db(self):
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
        if md_attribute_items != []:
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
            insert_into_article = """
            insert into articles(title,author) 
            values(
            '{title}','{author}'
            )
            """.format(title=title, author=author)
            print("[*] 正在向articles表中插入第{item_count}个文件的信息....".format(item_count=item_count))
            self.need_commit_sql(insert_into_article)
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
                self.need_commit_sql(insert_into_tags)
            print("[*] 正在向categories表中插入第{item_count}个文件的信息....".format(item_count=item_count))
            for category in categories:
                insert_into_categories = """
                insert into categories(category_name,belong_to)
                values(
                '{category_name}','{belong_to}'
                )
                """.format(category_name=category, belong_to=article_id)
                self.need_commit_sql(insert_into_categories)
            print("[√] 第{}个文件的内容已全部存入数据库".format(item_count))
            file_count += 1
        print("[SUCCESS] 完成数据存储任务，本次共存储{}个文件的信息".format(file_count))

    def get_current_data(self):
        # TODO: 读取当前数据库中的文章信息
        print("[*] 正在获取数据库中存储的信息....")
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
            self.__current_db_info_list.append(total_info)
            if self.__current_db_info_list != []:
                print("[√] 获取信息成功")
                return True
            else:
                print("[×] 获取信息失败")
                return False

    def change_file(self):
        # TODO: 将md文件的属性修改为数据库中记录的属性
        title_pattern = r"(^title:\s)(.*)"
        other_pattern = r"(.*):\s(.*)"  # 用于获取可能出现的标签
        commen_list = ['title', 'author', 'tags', 'categories']  # 设置普通标签
        other_dict = {}  # 存放不存在于commen_list中的标签
        changed_file_data = ""  # 存放更改后的文件内容
        all_files_path = self.get_all_md_path()
        if all_files_path == []:
            print('[×] 未检测到文件路径信息')
            return
        # 如果数据库信息获取失败则退出
        if self.get_current_data() is False:
            print("[×] 获取数据库信息失败")
            return
        print("[*] 正在备份原文件....")
        file_count = 0
        for md_file in all_files_path:
            try:
                shutil.copy(md_file, md_file+".bak")
                print("[√] 备份{}成功！".format(md_file))
                file_count += 1
            except:
                print("[×] 备份{}失败".format(md_file))
                return False
        print("[√] 文件备份已完成，本次共备份{}个文件".format(file_count))
        print("[*] 开始修改文件")
        for md_file in all_files_path:
            print("[*] 开始执行对{}的操作".format(md_file))
            try:
                # 只读模式打开备份文件,为防止修改失败时损坏源文件，源文件将在后边打开
                bak_file = open(md_file+'.bak', 'r', encoding='utf8')
            except:
                print("[×] 打开{}失败".format(md_file+".bak"))
                return False
            # 获取文章标题
            try:
                title = re.search(title_pattern, bak_file.readline()).group(2)
            except:
                print("[×] 未找到{}的title字段，自动跳过该文件".format(md_file))
                continue
            title_exist = False  # 标志该文件中的title是否存在于数据库中
            # 遍历存储当前数据库文章信息的数组并将所有内容存储在changed_file_data中(只存储title,author,tags,categories)
            for article_info in self.__current_db_info_list:
                # 如果文章中存在此title，则进行下一步操作，否则跳出该次循环
                title_exist = True
                if article_info['title'] == title:
                    # 添加title
                    changed_file_data += "title: {}\n".format(article_info['title'])
                    # 添加author
                    changed_file_data += "author: {}\n".format((article_info['author']))
                    # 添加tags
                    changed_file_data += "tags:\n"
                    for tag in article_info['tags']:
                        changed_file_data += "  - {}\n".format(tag[0])
                    # 添加categories
                    changed_file_data += "categories:\n"
                    for category in article_info['categories']:
                        changed_file_data += "  - {}\n".format(category[0])
            origin_attribute_end = False  # 标志源文件属性部分是否结束，默认未结束
            store_other_attribute = False  # 标志源文件其他属性部分是否已存储，默认未存储
            # 遍历备份文件中的内容，获取其他标签
            for line in bak_file:
                # 判断属性部分是否结束
                if origin_attribute_end is False:
                    if line[0:3] == "---":
                        origin_attribute_end = True
                # 如果属性部分未结束
                if origin_attribute_end is False:
                    try:
                        key = re.search(other_pattern, line).group(1)
                    except:
                        key = ""
                    try:
                        value = re.search(other_pattern, line).group(2)
                    except:
                        value = ""
                    # 若匹配到其他标签，则将其标签和值存到字典中
                    if key not in commen_list and key != "":
                        other_dict[key] = value
                    # 结束本次循环以方便其他标签的收集
                    continue
                # 若还未存储其他标签
                if store_other_attribute is False:
                    store_other_attribute = True
                    for key, value in other_dict.items():
                        changed_file_data += "{}: {}\n".format(key, value)
                # 存储剩余所有内容
                changed_file_data += line
            # 关闭备份文件
            bak_file.close()
            # 打开源文件
            try:
                origin_file = open(md_file, 'w', encoding='utf8')
            except:
                print("[×] 打开{}失败".format(md_file))
                return False
            # 写入内容
            try:
                origin_file.write(changed_file_data)
            except:
                print("[×] 更改{}失败".format(md_file))
            origin_file.close()
            print('[√] 已完成对{}的更改'.format(md_file))
            if not title_exist:
                print("[×] 在数据库中没有找到该文章的相关信息")
        print("[SUCCESS] 所有文件均已处理完毕")
