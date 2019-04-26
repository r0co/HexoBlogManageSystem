# coding=utf-8
import re
import pymysql


def get_config():
    # TODO: 获取配置信息
    # params: None

    config_arr = []
    pattern = r'([A-z]*) : (.*)'
    config_data = open("../config/config.ini").readlines()
    for line in config_data:
        key = re.search(pattern, line).group(1)
        value = re.search(pattern, line).group(2)
        config_arr.append((key, value))
    config_dict = dict(config_arr)
    return config_dict


def store_md_attribute(file_path, ):
    # TODO: 获取md文件中的属性（如标签、分类）并将它们存入数据库中
    # params: 文件绝对路径

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
            title = second_attr
        if first_attr == 'author':
            author = second_attr
        # print(tags)
        # print(categories)
    # print("标题:" + title)
    # print("作者：" + author)
    # print("标签")
    # print(tags)
    # print("分类")
    # print(categories)


# def scan_file():
#     # TODO: 获取目标目录下的
#

store_md_attribute("../TEST.md")