# 使用 AI 翻译群星本地化文件

需要依赖
- python
  - openai
  - loguru
  - pyyaml

使用方法
- 在环境变量中设置 `OPENAI_API_KEY`，例如 `OPENAI_API_KEY=sk-******`
- 运行 `python main.py <localisation 文件路径> ...`
- 翻译结果会保存在文件名后加上 `.l_simp_chinese` 的文件中
- 默认会翻译完所有文件后进行检查，检查是否存在变量引用、资源引用等特殊格式被破坏的情况，如果存在则输出警告信息
- 如果已经翻译过了，只需要进行检查，可以添加 `--only-check` 参数（或简写格式 `-k`），例如 `python main.py --only-check <localisation 文件路径> ...`

