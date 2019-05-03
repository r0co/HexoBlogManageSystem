# HexoBlogManageSystem
Hexo博客管理系统

## 功能

提取hexo博客系统中所使用md文件的tag、categories。

练手作品，大佬们莫笑


## 开发进程

**完成了**：

> Config类
>
> > 获取配置信息
> >
> > 获取指定文件夹下所有md绝对路径的功能
> >
> > 获取md文件中的属性
> >
> > 获取所有md文件中的属性

> Db类
>
> > 执行SQL语句
> >
> > 重置hexo_manager表
> >
> > 将在Config中获取到的所有信息（即存在__files_all_attribute_list中的信息）存入数据库中
> >
> > 返回当前数据库信息（列表形式）

**待开发**：

> Config类：
>
> > 将当前配置写入文件中

