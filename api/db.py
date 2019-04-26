import pymysql
import sys
sys.path.append('.')
from config import *


def connect_db(config_data):
    # TODO: 连接mysql数据库
    # params: 使用get_config方法获取到的数据库连接信息
    conn = pymysql.connect(config_data['host'], config_data['username'], config_data['password'], config_data['dbname'])
    conn_obj = conn.cursor()
    return conn_obj


def execute_sql(connection, sentence):
    # TODO: 执行sql语句并返回结果(结果为一元组)
    # params: 连接对象(connection)，需执行的sql语句(sentence)
    connection.execute(sentence)
    res = connection.fetchall()
    return res


def init_db_tables():
    # TODO: 初始化本系统所需的表
    # params: None
    drop_sql = "drop table if exists hexo_manager"
    try:
        execute_sql(connect_db(get_config()), drop_sql)
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
        execute_sql(connect_db(get_config()), create_sql)
        print("[*] 创建数据表hexo_manager成功")
    except:
        print("[!] 创建数据表hexo_manager失败")


