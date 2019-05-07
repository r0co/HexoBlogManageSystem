from manager.Db import Db
import getopt


class UI(Db):
    """
    属性说明：

    方法说明：
    db_conn() : 获取配置文件并连接数据库
    usage() : 输出帮助文档
    main() : 获取用户输入，根据用户输入调用不同方法
    """
    @staticmethod
    def usage():
        # TODO: 输出帮助文档
        print("=============================================")
        print("\"属性\"即为md文件的title、tags、categories等丨")
        print("=============================================")
        print("-r,--resetdb                - 重置数据库")
        print("-l,--list                  - 匹配文件夹中包含的md文件")
        print("-s,--store                  - 将当前扫描结果存入数据库中")
        print("-a,--auto                   - 自动进行扫描、存储操作")
        print("-o,--overwrite              - 将所有md文件的属性更改为数据库中存储的属性")
        print("-h,--help                   - 显示帮助文档")

    def db_conn(self):
        self.get_config()
        self.conn()

    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv, "arlmsoh", ["list", "auto", "scan", "change", "help"])
        except getopt.GetoptError:
            print("[!] 参数错误,使用--help查看帮助")
            return
        # 如果参数冗余
        if args != []:
            print("[!] 参数错误,使用--help查看帮助")
            return
        conn_flag = False  # 默认不连接数据库
        # 遍历参数表以确定是否需要自动连接数据库
        for opt, arg in opts:
            # 如果参数中不含指定参数，则表明需自动连接数据库
            if opt not in ("-h", "--help", "-l", "--list"):
                # 无指定参数，需自动连接
                conn_flag = True
            else:
                # 有指定参数，无需连接
                conn_flag = False
        if conn_flag:
            self.db_conn()

        # 遍历参数表，执行对应操作
        for opt, arg in opts:
            # 重置数据库
            if opt in ("-r", "--resetdb"):
                self.reset_db()
            # 查看所有匹配到的md文件
            elif opt in ("-l", "--list"):
                self.get_all_md_path()
            # 存储数据
            elif opt in ("-s", "--store"):
                self.store_attribute()
            # 自动执行匹配、存储操作
            elif opt in ("-a", "--auto"):
                self.db_conn()
                self.reset_db()
                self.scan()
                self.store_attribute()
            # 执行写入数据操作
            elif opt in ("-o", "--overwrite"):
                self.change_file()
            elif opt in ("-h", "--help"):
                self.usage()
