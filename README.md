# HexoBlogManageSystem

Hexo博客管理系统

## 功能

批量更改hexo博客标签及分类

## 使用说明

**目前仅在windows平台上测试成功**

下载本项目：

`git clone https://github.com/r0co/HexoBlogManageSystem.git`

编辑`config/config.ini`进行数据库及`source/_post`目录路径的配置

使用`python3 main.py -h`或`python3 main.py --help`获取帮助信息

参数如下：

```
-r,--resetdb                - 重置数据库
-l,--list                   - 扫描并显示配置文件中指定路径下所有的md文件
-s,--store                  - 扫描并将所有md文件的信息存入数据库中
-o,--overwrite              - 将所有md文件的属性更改为数据库中存储的属性
-h,--help                   - 显示帮助文档
```