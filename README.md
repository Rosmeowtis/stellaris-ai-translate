# Paradox Mod Translator

本项目是一个基于语言大模型（LLM）的 Paradox 本地化文件翻译工具。

+ 通过 OpenAI 兼容 API 调用 LLM 对文本进行翻译。API Key 需要用户自行配置。
+ 通过 task.toml 文件配置翻译任务，配置项可参考 [task.template.toml](./task.template.toml)
+ 通过术语表对相关游戏术语进行规范化，项目自带术语表可查看 [glossary](./data/glossary/) 文件夹内容，另外，用户还可在数据目录 `/data/glossary_custom` 中以相同的格式添加自定义术语。

## 使用方法

将要翻译的yml文件放进 localisation/ 中，例如 `localisation/english/something_l_english.yml`。

随后编辑配置文件 `task.toml`，例如：

```toml
# 任务模板示例，具体内容根据情况编写。

# 大模型客户端设置（可选，使用默认值）
[client_settings]
# API基础URL（OpenAI兼容格式，默认：https://api.deepseek.com）
api_base = "https://api.deepseek.com"
# 模型名称（默认：deepseek-reasoner）
model = "deepseek-chat" # 用 chat 模型会更快一些
# 温度参数（0.0-2.0，默认：0.7）
temperature = 0.7
# 请求超时时间（秒，默认：600）
timeout_secs = 600
# 最大重试次数（默认：3）
max_retries = 3
# 最大切片token数（注释以使用默认值，若要填写数值则需查看模型支持的最大上下文，取约 1/3 以免超出）
# 每次请求的最大文本长度（字符数，用于切片，默认：10000）
# deepseek-reasoner 支持最大 32K 上下文
# deepseek-chat 支持 8k，因本配置使用 chat 模型，因此设为 2500
max_chunk_tokens = 2500

# 并发请求数（默认：2），使用命令行选项 --concurrent 以启用并发模式，
# 否则该配置会被忽略
concurrency = 2

[[task]]
source_lang = "english"
# 可用的语言代码列表见 https://stellaris.paradoxwikis.com/Localisation_modding
target_langs = [
    "simp_chinese",
    # ...
]
# glossary 以及 glossary_custom 中的文件名（忽略 json 后缀名）
glossaries = [
    "stellaris",
]
# 源语言文件所在目录，会自动读取 {localisation_dir}/{source_lang} 下的所有 yml 文件，并将其写入
# localisation_dir/{source_lang}/replace 中的同名 yml 文件中（将文件名中的 l_{source_lang} 替换为 l_{target_lang}）
# 需要为绝对路径或相对于 task.toml 的相对路径
localisation_dir = "./localisation"
```

配置完成后，运行指令如下指令即开始翻译。控制台会显示简要日志，详细日志保存在 ./paradox-mod-translator.log 中。

```sh
pmt translate task.toml
```

如果 API 服务商允许并发，可添加命令行选项 `--concurrent` 以启用并发模式，默认双协程并发，可通过配置文件中的 `concurrency` 参数调整，
注意合理使用。