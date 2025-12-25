# 数据目录

程序在翻译时需要读取的提示词模板、术语表文件分别存储在数据目录的这些路径下：

+ 提示词模板 `$DATADIR/prompts` ，在此目录下存储了 `.txt` 后缀名的文本文件，其内容为会用到的提示词模板。
+ 用户术语表文件 `$DATADIR/glossary_custom`，在此目录下存储了 `.json` 后缀名的文本文件，其内容为术语表，是由用户自行添加的。
+ 自带术语表文件 `$DATADIR/glossary`，在此目录下存储了 `.json` 后缀名的文本文件，其内容为术语表，是开发者提供的，随程序可执行文件一同发布。

`$DATADIR` 则按照以下顺序进行确定：

1. 当前目录下的 `./data`
2. 用户数据目录
    + Windows 为 `%APPDATA%/pmt/data`
    + Linux/Unix 为 `~/.local/share/pmt/data`
