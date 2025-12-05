# # 使用 AI 翻译群星本地化文件
#
# 需要依赖
# - python
#   - openai
#   - loguru
#   - pyyaml
#
# 使用方法
# - 在环境变量中设置 `OPENAI_API_KEY`，例如 `OPENAI_API_KEY=sk-******`
# - 运行 `python main.py <localisation 文件路径> ...`
# - 翻译结果会保存在文件名后加上 `.l_simp_chinese` 的文件中
# - 默认会翻译完所有文件后进行检查，检查是否存在变量引用、资源引用等特殊格式被破坏的情况，如果存在则输出警告信息
# - 如果已经翻译过了，只需要进行检查，可以添加 `--only-check` 参数（或简写格式 `-k`），例如 `python main.py --only-check <localisation 文件路径> ...`


import os
import re
from argparse import ArgumentParser
from pathlib import Path

import yaml
from loguru import logger
from openai import OpenAI

# 配置使用 DeepSeek Reasoner ，从 env 中读取 key
API_KEY = os.environ.get("OPENAI_API_KEY")
if API_KEY is None or API_KEY == "":
    raise ValueError("在环境变量中设置 api key，例如 OPENAI_API_KEY=sk-******")

CLIENT = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",
)

SYS_PROMPT = """你是一个好用的翻译助手，接下来我将发送给你游戏《群星》（Stellaris）相关的 localisation 文件，这种文件的格式如下：

```yaml
<language_code>:
  <key>: <value>
```

请将 <value> 对应的内容翻译成中文，而 <key> 保持不变，并将 <language_code> 部分更改为 `l_simp_chinese`。
翻译时还需要注意以下要求：

1. 游戏的变量标记，这种标记的格式特征为由 `$` 符号包裹一个变量名，例如 `$variable$`，不要翻译，保持原样。
2. 游戏的格式标记，这种标记的格式特征为以 `§` 符号开头，后面跟随一个字符，例如 `§R` `§!` ，不要翻译，保持原样。
3. 游戏的图标引用标记，这种标记的格式特征为由 `£` 符号包裹一个变量名，例如 `£rare_crystals£`，不要翻译，保持原样。
4. 游戏的动态引用标记，这种标记地格式特征为由中括号 `[]` 包裹一个变量名，其中可能存在用 `.` 表示的属性访问，例如 `[This.GetName]` ，也可能不存在 `.`，例如 `[pf_planet_type]`，不要翻译，保持原样。
5. 专有名词要保证统一性，如果存在原版游戏中的专有名词，翻译方式应与原版游戏一致，例如 Psionic 应翻译成灵能。
6. 如果存在对应学科的术语，则按照学术界的翻译标准进行翻译，例如 particulates/silica 应翻译成 微粒/硅质。
7. 只需要回复翻译后的文件内容，不要提供任何解释，不要包含 ```yaml ``` 标记，不要包含任何其他内容。
8. 在不违反上述规则的前提下，尽可能将文本翻译得具有科幻风格，具有艺术气息。
"""

RE_VAR = re.compile(r"\$\S+\$")
RE_FMT = re.compile(r"§\S")
RE_ICON = re.compile(r"£\S+£")
RE_REF = re.compile(r"\[\S+\]")
RE_ALL = re.compile(r"(\$\S+\$)|(\§\S)|(\£\S+£)|(\[\S+\])")


def translate(files: list[str]):
    # 为了避免对话过长，且让AI获得充足参考，history只保留最近的 3 次翻译
    history = []

    for file in files:
        path = Path(file)
        if not path.exists():
            logger.warning(f"{path.as_posix()} 不存在，跳过")
            continue
        content = path.read_text(encoding="utf-8")
        messages = (
            [
                {"role": "system", "content": SYS_PROMPT},
            ]
            + history[:3]
            + [
                {"role": "user", "content": content},
            ]
        )
        logger.info(f"开始翻译文件: {path.as_posix()}[{len(content) / 1024:.2f}KiB]")
        response = CLIENT.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            stream=False,
            temperature=1.3,
        )
        logger.debug(f"{response.choices!r}")
        msg = response.choices[0].message
        logger.info(
            f"翻译完成: {path.as_posix()}, 翻译结果预览: {msg.content[:80]!r} ... {msg.content[-80:]!r}"
        )
        history.append(msg)
        new_path = path.with_suffix(".l_simp_chinese.yaml")
        new_path.write_text(msg.content, encoding="utf-8")


def check(files: list[str]):
    for file in files:
        path = Path(file)
        new_path = path.with_suffix(".l_simp_chinese.yaml")
        if not new_path.exists():
            logger.warning(f"{new_path.as_posix()} 不存在，跳过")
            continue
        logger.info(f"开始检查文件: {new_path.as_posix()}")
        problems = []
        with path.open(encoding="utf-8") as f:
            yaml_raw = yaml.safe_load(f)
        with new_path.open(encoding="utf-8") as f:
            try:
                yaml_new = yaml.safe_load(f)
            except yaml.error.YAMLError as e:
                logger.error(
                    f"{new_path.as_posix()} 翻译结果中含有无法被 YAML 解析的内容:\n{'\n'.join(('| ' + line) for line in str(e).splitlines())}"
                )
                continue
        # 1. 检查语言代码是否更改
        if "l_simp_chinese" not in yaml_new.keys():
            problems.append("语言代码未更改为 l_simp_chinese")
        # 2. 检查两文件含有的 key 是否一致
        _raw_keys = set(yaml_raw["l_english"].keys())
        _new_keys = set(yaml_new["l_simp_chinese"].keys())
        if _raw_keys != _new_keys:
            _missing_keys = _raw_keys.difference(_new_keys)
            _extra_keys = _new_keys.difference(_raw_keys)
            problems.append(
                f"两文件含有的 key 不一致: 缺失 {','.join(_missing_keys)}, 多余 {','.join(_extra_keys)}"
            )
        # 3. 检查翻译是否破坏特殊格式
        for key in _raw_keys:
            content = yaml_raw["l_english"][key]
            matches = [it[0] for it in RE_ALL.findall(content)]
            if matches:
                for match in matches:
                    if match not in yaml_new["l_simp_chinese"][key]:
                        problems.append(
                            f"翻译破坏了特殊格式: {key}/{match} -> {yaml_new['l_simp_chinese'][key]}"
                        )
        if problems:
            logger.error(
                f"文件 {new_path.as_posix()} 存在以下问题: {'\n'.join((f'|  {i + 1}. {problem}') for i, problem in enumerate(problems))}"
            )
        else:
            logger.success(f"文件 {new_path.as_posix()} 检查通过")


def main():
    p = ArgumentParser()
    p.add_argument("files", help="需要翻译的文件路径", nargs="+")
    p.add_argument(
        "-k",
        "--only-check",
        help="在已经翻译过的情况下，只检查翻译是否破坏特殊格式",
        action="store_true",
    )
    args = p.parse_args()
    if not args.only_check:
        translate(args.files)
    check(args.files)


if __name__ == "__main__":
    logger.level("info")
    main()
