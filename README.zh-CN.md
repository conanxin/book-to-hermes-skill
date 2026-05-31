# Book-to-Hermes Skill

[English](README.md) | 中文

Book-to-Hermes Skill 可以把本地书籍、长文、PDF、HTML、DOCX、EPUB 等资料转换成 Hermes 可长期调用的 book skill。

## 一句话介绍

它不是一次性摘要工具。它会把资料变成可长期使用的知识技能包，之后你可以通过 `@skill-name` 反复调用。

## 它解决什么问题

- 长文读完后难以复用
- 普通摘要容易丢上下文
- PDF / EPUB / HTML / DOCX 难以统一管理
- 个人阅读资料缺少结构化索引
- 中英资料需要术语对照
- 项目文档需要长期复盘

## 支持格式

| 格式 | 扩展名 | 状态 |
|------|--------|------|
| Markdown | .md / .markdown | 稳定 |
| 纯文本 | .txt | 稳定 |
| 文字版 PDF | .pdf | 稳定（不支持扫描版） |
| HTML | .html / .htm | 稳定 |
| DOCX | .docx | 稳定 |
| EPUB | .epub | 稳定 |

### 暂不支持

- 扫描版 / 图片版 PDF（无 OCR）
- RTF
- MOBI / AZW / AZW3
- DRM 保护的 EPUB

## 生成后的结构

```
~/.hermes/skills/books/example-book/
├── SKILL.md              # 总地图（章节索引、主题索引、使用说明）
├── chapters/             # 章节内容，按需加载
│   ├── ch01-intro.md
│   ├── ch02-chapter.md
│   └── ...
├── glossary.md           # 术语表（带定义和来源章节）
├── patterns.md           # 可复用观点 / 框架 / 模式
├── cheatsheet.md         # 快速查阅表
├── metadata.json         # 元数据
└── source_manifest.md    # 来源与安全说明
```

### 各文件用途

- **SKILL.md** — 总地图，先加载（约 400–4,000 tokens）。含章节索引、主题索引、使用说明。
- **chapters/** — 按需加载（每章约 800–1,200 tokens）。含摘要、要点、原文。
- **glossary.md** — 从原文抽取的术语，带定义、类型、章节引用。
- **patterns.md** — 原文中反复出现的结构（非模板，证据驱动）。
- **cheatsheet.md** — 常用查询命令速查。
- **metadata.json** — 机器可读元数据（标题、slug、语言、模式、章节数等）。
- **source_manifest.md** — 来源路径、格式、已知限制。

## 安装方式

把工具目录复制到 Hermes skills 目录：

```bash
cp -r book-to-hermes-skill/ ~/.hermes/skills/knowledge/book-to-hermes-skill/
```

可选：创建独立 venv：

```bash
python3 -m venv ~/.hermes/venvs/book-to-hermes-skill
source ~/.hermes/venvs/book-to-hermes-skill/bin/activate
pip install python-docx ebooklib beautifulsoup4 lxml
```

**重要**：工具不会自动安装依赖。如需 DOCX / EPUB 支持，用户必须显式安装。工具不会修改 Hermes 配置。

## 快速开始

### 生成 book skill

```bash
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/build_book_skill.py \
  --source ~/Documents/example.md \
  --slug example-book \
  --title "Example Book" \
  --language zh \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 验证生成的 skill

```bash
python ~/.hermes/skills/knowledge/book-to-hermes-skill/scripts/validate_book_skill.py \
  --skill-dir ~/.hermes/skills/books/example-book/
```

## 常见转换示例

### 1. 转换 Markdown 长文

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/essay.md \
  --slug my-essay \
  --title "My Essay" \
  --language zh \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 2. 转换 TXT

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/notes.txt \
  --slug my-notes \
  --title "My Notes" \
  --language zh \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 3. 转换文字 PDF

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/paper.pdf \
  --slug research-paper \
  --title "Research Paper" \
  --language zh \
  --mode technical \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 4. 转换本地 HTML 文章

```bash
python scripts/build_book_skill.py \
  --source ~/Downloads/article.html \
  --slug web-article \
  --title "Web Article" \
  --language zh \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 5. 转换 DOCX 报告

```bash
python scripts/build_book_skill.py \
  --source ~/Documents/report.docx \
  --slug annual-report \
  --title "Annual Report" \
  --language zh \
  --mode article \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

### 6. 转换 EPUB 电子书

```bash
python scripts/build_book_skill.py \
  --source ~/Books/novel.epub \
  --slug my-novel \
  --title "My Novel" \
  --language zh \
  --mode book \
  --output-dir ~/.hermes/skills/books \
  --allow-overwrite no
```

## 在 Hermes 中如何使用

生成并验证 skill 后，在 Hermes 中加载：

```
skill_view(name='example-book')
```

然后查询：

```
@example-book 这篇文章讲什么？
@example-book 有哪些关键概念？
@example-book 总结第三章
@example-book 帮我整理成中文读书笔记
```

也可以查看单个章节：

```
skill_view(name='example-book', file_path='chapters/ch03-example.md')
```

## 适合的使用场景

- 长文阅读资料库
- 电子书阅读笔记
- 学术论文整理
- 技术报告 / 项目文档沉淀
- API 文档整理
- 中英双语术语对照
- 写作素材库
- 个人 Reading Memex

## 双语术语表工作流

如果有英文版和中文版，可以：

1. 分别生成英文 skill 和中文 skill
2. 生成 bilingual glossary（规则对齐）
3. 生成人工审校包
4. 用户确认术语
5. 只把确认后的术语写回 glossary

**案例**：`the-artist-is-dead-en` + `the-artist-is-dead-zh`

- 4 个用户审校术语已写回两个 glossary
- Bilingual glossary v3：50 高置信 / 25 中置信 / 14 低置信 / 14 缺失
- 工作流模板已包含在本项目中

**注意**：工作流不自动翻译，只对齐两个语言版本中已有的术语。不使用 LLM 翻译或 enrichment。

### 术语示例

| English | 中文 |
|---------|------|
| Zombie Formalism | 僵尸形式主义 |
| Debt Aesthetics | 债务美学 |
| Duty Free Art | 免税艺术 |
| AI art | AI 艺术 |
| Wabi-sabi | 侘寂 |
| Artistic autonomy | 艺术自主性 |

## 安全模型

- 不自动安装依赖
- 不联网抓取内容
- 不调用 LLM
- 不上传源文档
- 不读取 secret 文件
- 不执行 HTML / EPUB 脚本
- 不执行 DOCX 宏
- 不修改 Hermes 配置
- 不重启 gateway
- 不处理 DRM
- 不做 OCR
- 不默认覆盖已有 skill

## 已知限制

- 不支持扫描版 PDF
- 不支持 RTF
- 不支持 MOBI / AZW / AZW3
- 不支持 DRM EPUB
- glossary 是规则抽取，可能需要人工审校
- HTML / EPUB 效果依赖源文件结构
- 不是完整 RAG 系统
- 不能替代人工阅读

## 推荐日常工作流

1. 选择本地文档
2. 运行 build
3. 运行 validate
4. 检查 SKILL.md / glossary / chapters
5. 用 `@skill-name` 调用
6. 如果是双语文档，运行 bilingual glossary review
7. 积累 5–10 个正式 book skills 后，再做 Personal Reading Memex Index

## 下一步规划

### 短期

- 继续日常使用
- 积累 5–10 个真实 book skills
- 改善人工 glossary 审校
- 更多双语资料对照

### 中期

- Personal Reading Memex Index
- 跨文档主题索引
- 人物 / 概念图谱
- 写作素材包
- 翻译对照工作流

### 可选未来功能

- RTF 支持
- MOBI / AZW 支持
- 可选 LLM enrichment
- 段落级 chapter alignment
- public 示例数据集

### 暂不计划

- OCR
- DRM EPUB
- 自动联网抓取
- 默认自动 LLM enrichment
- 自动安装依赖

## License

MIT License. 详见 [LICENSE](LICENSE)。

## 致谢

为 Hermes agent 生态构建。本地优先，隐私优先的文档管理工具。
