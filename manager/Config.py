import re
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

    # def scan(self):
    #     # TODO: 整合所有用来扫描的方法，目的是给Config类的属性赋值
    #     self.__match_config()
    #     self.__match_md_path()
    #     self.__collect_all_md_attribute()

    def __match_config(self):
        # TODO: 获取配置文件信息
        print("[*] 获取配置文件中....")
        config_list = []
        pattern = r'([A-z_]*) : (.*)'
        try:
            config_data = open("./config/config.ini").readlines()
        except :
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
        self.__match_config()
        return self.__conf_dict

    def get_all_md_path(self):
        # TODO: 为子类提供配置文件指定路径下所有.md文件的路径信息
        self.get_config()
        self.__match_md_path()
        return self.__files_path_list

    def get_all_md_attribute(self):
        return self.__files_all_attribute_list
