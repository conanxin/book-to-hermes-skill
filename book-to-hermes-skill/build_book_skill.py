#!/usr/bin/env python3
"""
Build a Hermes-native book skill from a source document.

Input: source file path (Markdown / TXT / PDF)
Output: structured skill directory at <output_dir>/<slug>/

Safety:
  - No network
  - No auto-install
  - No overwrite without --allow-overwrite yes
  - No LLM API calls
  - All content is extractive (no hallucination)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXTRACT_SCRIPT = SCRIPT_DIR / "extract_text.py"


def slugify(name: str) -> str:
    """Convert a string to a URL-safe slug."""
    s = name.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def extract_text(source_path: str, mode: str) -> dict:
    """Run extract_text.py and return parsed JSON."""
    cmd = [sys.executable, str(EXTRACT_SCRIPT), source_path, "--mode", mode]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        return {"ok": False, "errors": [f"extract_text.py failed: {result.stderr}"]}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {"ok": False, "errors": [f"Invalid JSON from extract_text.py: {e}"]}


def split_into_chapters(text: str, language: str) -> list[dict]:
    """Split text into chapters/sections."""
    lines = text.splitlines()
    chapters = []
    current_lines = []
    current_title = "Introduction"
    chapter_num = 0

    chapter_patterns = [
        re.compile(r"^\s*第\s*(\d+)\s*章\s*[：:]?\s*(.*)", re.UNICODE),
        re.compile(r"^\s*第\s*([一二三四五六七八九十百千]+)\s*章\s*[：:]?\s*(.*)", re.UNICODE),
        re.compile(r"^\s*Chapter\s+(\d+)\s*[：:.]?\s*(.*)", re.IGNORECASE),
        re.compile(r"^\s*CHAPTER\s+(\d+)\s*[：:.]?\s*(.*)"),
    ]

    heading_pattern = re.compile(r"^(#{1,3})\s+(.+)")

    # Track if we've seen a real title (non-filename)
    seen_real_title = False
    first_heading = None

    for line in lines:
        matched = False
        for pat in chapter_patterns:
            m = pat.match(line)
            if m:
                if current_lines:
                    chapters.append({
                        "num": chapter_num or 1,
                        "title": current_title,
                        "text": "\n".join(current_lines),
                    })
                chapter_num = int(m.group(1)) if m.group(1).isdigit() else len(chapters) + 1
                current_title = m.group(2).strip() or f"Chapter {chapter_num}"
                current_lines = []
                matched = True
                break

        if not matched:
            hm = heading_pattern.match(line)
            if hm:
                level = len(hm.group(1))
                title = hm.group(2).strip()

                # Track first heading
                if first_heading is None:
                    first_heading = title

                # Skip filename-like first headings
                if level == 1 and not seen_real_title:
                    if _looks_like_filename(title):
                        # Don't start a new chapter for filename-like title
                        # Just update current_title but don't flush
                        current_title = title
                        seen_real_title = False
                        matched = True
                    else:
                        seen_real_title = True
                        current_title = title
                        matched = True
                elif level == 2:
                    if current_lines:
                        chapters.append({
                            "num": chapter_num or 1,
                            "title": current_title,
                            "text": "\n".join(current_lines),
                        })
                    chapter_num = len(chapters) + 1
                    current_title = title
                    current_lines = []
                    matched = True
                elif level == 1 and not current_lines:
                    current_title = title
            if not matched:
                current_lines.append(line)

    if current_lines:
        chapters.append({
            "num": chapter_num or 1,
            "title": current_title,
            "text": "\n".join(current_lines),
        })

    if len(chapters) <= 1 and len(text) > 6000:
        chunk_size = 5000
        chapters = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            chapters.append({
                "num": (i // chunk_size) + 1,
                "title": f"Part {(i // chunk_size) + 1}",
                "text": chunk,
            })

    return chapters


def _looks_like_filename(text: str) -> bool:
    """Check if text looks like a filename rather than a document title."""
    if not text:
        return True
    # Ends with file extension
    if re.search(r"\.(pdf|html|htm|docx|epub|txt|md)$", text, re.IGNORECASE):
        return True
    # Contains only filename characters (no spaces, mostly alphanumeric + _ -)
    if re.match(r"^[A-Za-z0-9_\-\.]+$", text):
        return True
    # Looks like a stem with underscores (e.g. "art_history")
    if "_" in text and " " not in text and len(text.split("_")) >= 2:
        return True
    return False


def estimate_tokens(text: str) -> int:
    words = len(text.split())
    cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if cjk_chars > words * 0.3:
        return int(words / 0.6)
    return int(words / 0.75)


# ── Extractive summary helpers ────────────────────────────────────────────

def split_sentences(text: str) -> list[str]:
    """Split text into sentences. Handles Chinese and English punctuation."""
    pattern = re.compile(r'(?<=[。！？；\.\!\?])\s+')
    raw = pattern.split(text.strip())
    sentences = [s.strip() for s in raw if s.strip()]
    return sentences


def parse_markdown_table(text: str) -> tuple[list[str], list[dict]] | None:
    """Parse a Markdown table into headers and row dicts. Returns None if not a table."""
    lines = text.splitlines()
    # Find table blocks
    table_lines = []
    in_table = False
    for line in lines:
        if "|" in line:
            table_lines.append(line)
            in_table = True
        else:
            if in_table and table_lines:
                break
    if len(table_lines) < 2:
        return None
    # First line is header
    header_line = table_lines[0]
    headers = [h.strip() for h in header_line.split("|") if h.strip()]
    if not headers:
        return None
    # Second line should be separator
    sep_line = table_lines[1]
    if not re.match(r"^\s*\|?[\s\-:]+\|", sep_line):
        return None
    # Parse rows
    rows = []
    for row_line in table_lines[2:]:
        cells = [c.strip() for c in row_line.split("|") if c.strip() or c == ""]
        # Pad or trim to match header count
        while len(cells) < len(headers):
            cells.append("")
        cells = cells[:len(headers)]
        row_dict = {headers[i]: cells[i] for i in range(len(headers))}
        rows.append(row_dict)
    return headers, rows


def table_to_bullets(text: str, max_bullets: int = 8) -> list[str]:
    """Convert Markdown table content to readable bullets."""
    result = parse_markdown_table(text)
    if not result:
        return []
    headers, rows = result
    bullets = []
    for row in rows[:max_bullets]:
        # Skip rows with too many empty cells
        non_empty = [v for v in row.values() if v.strip()]
        if len(non_empty) < 2:
            continue
        parts = []
        for h, v in row.items():
            v_clean = v.strip()
            if not v_clean:
                continue
            # Truncate long cells
            if len(v_clean) > 80:
                v_clean = v_clean[:77] + "..."
            parts.append(f"{h}: {v_clean}")
        if parts:
            bullets.append("; ".join(parts))
    return bullets


def _is_table_line(line: str) -> bool:
    """Check if a line is part of a Markdown table."""
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False
    # Separator line like |---|---|
    if re.match(r"^\s*\|?[\s\-:]+\|", stripped):
        return True
    # Normal table row
    if stripped.count("|") >= 2:
        return True
    return False


def _clean_table_from_text(text: str) -> str:
    """Remove or convert table lines from text for summary/key_points use."""
    lines = text.splitlines()
    cleaned = []
    table_buffer = []
    for line in lines:
        if _is_table_line(line):
            table_buffer.append(line)
        else:
            if table_buffer:
                bullets = table_to_bullets("\n".join(table_buffer), max_bullets=3)
                for b in bullets:
                    cleaned.append(b)
                table_buffer = []
            cleaned.append(line)
    if table_buffer:
        bullets = table_to_bullets("\n".join(table_buffer), max_bullets=3)
        for b in bullets:
            cleaned.append(b)
    return "\n".join(cleaned)


def extract_summary(text: str, max_sentences: int = 5, max_chars_per_sentence: int = 300) -> str:
    """Extractive summary: first N non-empty paragraphs, first M sentences. Handles tables."""
    # First clean tables from text
    cleaned_text = _clean_table_from_text(text)
    paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]
    sentences = []
    table_found = "|" in text and "---" in text
    for para in paragraphs[:3]:
        # Skip bullet-like lines that are actually table conversions
        if para.startswith(";") or (": " in para and para.count(";") >= 1):
            sentences.append(para)
            if len(sentences) >= max_sentences:
                break
            continue
        for sent in split_sentences(para):
            if len(sent) > max_chars_per_sentence:
                sent = sent[:max_chars_per_sentence] + "..."
            sentences.append(sent)
            if len(sentences) >= max_sentences:
                break
        if len(sentences) >= max_sentences:
            break
    summary = " ".join(sentences) if sentences else "(No summary extractable from source.)"
    if table_found:
        summary = "This section includes a Markdown table. Key rows were normalized into readable bullets. " + summary
    return summary


def extract_key_points(text: str, max_points: int = 5) -> list[str]:
    """Extract key points from list items, tables, or sentences. Filters out raw table syntax."""
    points = []
    # Try table bullets first (converted from tables)
    table_bullets = table_to_bullets(text, max_bullets=max_points)
    for b in table_bullets:
        points.append(b)
        if len(points) >= max_points:
            break
    # Markdown list items
    if len(points) < max_points:
        for line in text.splitlines():
            # Skip table lines
            if _is_table_line(line):
                continue
            m = re.match(r"^\s*[-*]\s+(.+)", line)
            if m and len(m.group(1)) > 10:
                points.append(m.group(1).strip())
            if len(points) >= max_points:
                break
    # Fallback: numbered list items
    if not points:
        for line in text.splitlines():
            if _is_table_line(line):
                continue
            m = re.match(r"^\s*\d+\.\s+(.+)", line)
            if m and len(m.group(1)) > 10:
                points.append(m.group(1).strip())
            if len(points) >= max_points:
                break
    # Fallback: first few sentences from cleaned text
    if not points:
        cleaned = _clean_table_from_text(text)
        sents = split_sentences(cleaned)
        for s in sents[:max_points]:
            if len(s) > 15 and not _is_table_line(s):
                points.append(s)
    # Final cleanup: ensure no raw table syntax remains in points
    cleaned_points = []
    for pt in points:
        # Strip any remaining table row markers
        pt_clean = pt.strip()
        if pt_clean.startswith("|") and pt_clean.endswith("|"):
            continue
        if re.match(r"^\s*\|?[\s\-:]+\|", pt_clean):
            continue
        if pt_clean.count("|") >= 2 and "---" in pt_clean:
            continue
        cleaned_points.append(pt_clean)
    return cleaned_points[:max_points]


# ── English stop words and academic concept words ─────────────────────────

_ENGLISH_STOP_WORDS = frozenset([
    "the", "and", "or", "but", "with", "without", "from", "into", "about", "for",
    "to", "of", "in", "on", "at", "by", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "shall", "this", "that", "these",
    "those", "it", "its", "they", "them", "their", "we", "our", "us", "i", "me",
    "my", "mine", "you", "your", "yours", "he", "him", "his", "she", "her", "hers",
    "a", "an", "some", "any", "all", "each", "every", "both", "either", "neither",
    "one", "two", "three", "first", "second", "last", "next", "previous", "other",
    "another", "such", "only", "own", "same", "so", "than", "too", "very", "just",
    "now", "then", "here", "there", "when", "where", "why", "how", "what", "which",
    "who", "whom", "whose", "if", "because", "since", "until", "while", "although",
    "though", "unless", "whether", "before", "after", "above", "below", "up", "down",
    "out", "off", "over", "under", "again", "further", "once", "more", "most",
    "much", "many", "few", "little", "less", "least", "several", "various",
    "chapter", "section", "page", "figure", "table", "pdf", "html", "htm", "docx",
    "epub", "file", "document", "text", "source", "output", "result", "status",
    "note", "notes", "see", "also", "et", "al", "fig", "appendix", "reference",
    "references", "bibliography", "abstract", "introduction", "conclusion",
    "acknowledgments", "acknowledgement", "statement", "overview", "summary",
])

_ENGLISH_ACADEMIC_CONCEPTS = frozenset([
    "integrity", "generativity", "colonization", "cultivation", "autonomy",
    "instrumentalization", "non-instrumentality", "aesthetics", "agency",
    "practice", "form", "meaning", "value", "tradition", "medium", "subject",
    "object", "relation", "axis", "structure", "self", "world", "art",
    "history", "theory", "framework", "model", "dimension", "layer",
    "institutional", "relational", "individual", "structural", "dynamic",
    "horizontal", "vertical", "transmission", "internalization", "recognition",
    "evaluation", "direction", "movement", "progression", "trajectory",
    "spiral", "advancement", "development", "growth", "stagnation", "unlocking",
    "pain", "catalytic", "boundary", "condition", "space", "logic", "mechanism",
    "schema", "correction", "formalist", "criticism", "technology", "market",
    "algorithmic", "exposure", "unidimensionalization", "prediction",
])

# ── Topic / Term filtering ────────────────────────────────────────────────

_STATUS_WORDS = frozenset([
    "成功", "失败", "完成", "通过", "正常", "异常", "可用", "不可用", "启用", "禁用",
    "存在", "不存在", "已完成", "未完成", "已启用", "未启用", "已通过", "未通过",
    "未安装", "未升级", "未执行", "未修改", "未创建", "未启动", "不依赖",
    "完全可行", "已被证实", "现在可行", "已经可行", "已证明", "已验证",
    "pass", "fail", "ok", "done", "true", "false", "yes", "no",
    "success", "failed", "passed", "error", "warning", "info", "debug", "trace",
])

_REPORT_PHRASES = frozenset([
    "阶段", "状态", "结论", "结果", "报告", "路径", "文件", "目录", "列表", "说明",
    "摘要", "问题", "建议", "下一步", "关键文件", "核心成果", "验证结果",
])

_LOW_QUALITY_TOPICS = frozenset([
    "无", "是", "否", "有", "空", "已", "未",
    "status", "todo", "pending",
    "start", "end", "begin", "stop", "go", "back", "next", "prev", "up", "down",
    "left", "right", "top", "bottom", "first", "last", "all", "none", "any",
    "each", "every", "some", "many", "few", "several", "various", "multiple",
    "single", "double", "triple", "one", "two", "three", "four", "five",
    "zero", "null", "nil", "na", "n/a", "tbd", "todo", "wip",
    "确认", "验证", "检查", "测试", "信息", "数据", "内容",
    "答案", "方案", "方法", "步骤", "过程", "环节",
    "部分", "全部", "整体", "局部", "细节", "总结",
    "描述", "解释", "定义", "概述", "简介", "前言",
    "正文", "附录", "参考", "来源", "出处", "链接", "地址",
    "文件夹", "文档", "记录", "日志", "输出",
    "输入", "参数", "变量", "常量", "函数", "方法", "类", "对象",
    "实例", "属性", "字段", "成员", "接口", "实现", "调用", "返回",
    "创建", "删除", "修改", "更新", "添加", "移除", "插入", "追加",
    "开始", "结束", "启动", "停止", "暂停", "继续", "重启", "关闭",
    "打开", "保存", "加载", "读取", "写入", "导出", "导入", "上传",
    "下载", "复制", "粘贴", "剪切", "撤销", "重做", "查找", "替换",
    "搜索", "过滤", "排序", "分组", "聚合", "统计", "计算", "分析",
    "比较", "对比", "匹配", "映射", "转换", "格式化", "解析", "序列化",
    "反序列化", "编码", "解码", "加密", "解密", "压缩", "解压", "打包",
    "解包", "合并", "拆分", "分割", "连接", "断开", "绑定", "解绑",
    "注册", "注销", "登录", "登出", "授权", "认证", "鉴权", "权限",
    "角色", "用户", "管理员", "访客", "客户端", "服务端", "前端", "后端",
    "数据库", "缓存", "存储", "内存", "磁盘", "网络", "服务器", "浏览器",
    "系统", "平台", "框架", "库", "工具", "插件", "扩展", "模块",
    "组件", "部件", "单元", "元素", "因子", "系数", "指数", "指标",
    "标准", "规范", "规则", "策略", "政策", "原则", "准则", "指南",
    "手册", "教程", "资料", "资源", "素材", "模板", "样例",
    "示例", "案例", "演示", "展示", "展览", "发布", "公告",
    "通知", "提醒", "警告", "错误", "异常", "故障", "问题", "缺陷",
    "漏洞", "风险", "威胁", "攻击", "防御", "保护", "安全", "隐私",
    "保密", "签名", "证书", "密钥", "令牌", "凭证", "票据",
    "会话", "连接", "通道", "管道", "队列", "栈", "堆", "池",
    "线程", "进程", "任务", "作业", "工作流", "流水线", "管道线", "链",
    "图", "表", "树", "森林", "网", "网格", "矩阵", "向量",
    "数组", "列表", "集合", "字典", "映射", "哈希",
    "堆", "优先队列", "二叉树", "平衡树", "红黑树", "B树", "B+树",
    "有向图", "无向图", "加权图", "流网络", "残差网络",
    "可行性", "正当", "理由", "明确禁止", "回滚后状态", "总输出",
])


# Chinese stop-words / filter fragments
_CHINESE_STOP_WORDS = frozenset([
    "的", "了", "和", "与", "及", "在", "是", "将", "把", "为", "对", "从", "到", "这", "那",
    "一个", "一种", "可以", "通过", "如何", "进行", "使用", "本文", "本书", "本章", "介绍",
    "说明", "包含", "包括", "我们", "你们", "他们", "它们", "以及", "或者", "但是", "因为",
    "所以", "如果", "虽然", "并且", "其中", "其他", "一些", "这些", "那些", "什么", "怎么",
    "这个", "那个", "这里", "那里", "现在", "然后", "之后", "之前", "已经", "正在", "能够",
    "需要", "应该", "必须", "可能", "一定", "非常", "特别", "比较", "更加", "最好", "很多",
    "不少", "许多", "各种", "部分", "方面", "情况", "问题", "内容", "方法", "方式", "过程",
    "结果", "目的", "意义", "作用", "影响", "关系", "结构", "形式", "类型", "特点", "优势",
    "劣势", "挑战", "机会", "发展", "变化", "趋势", "方向", "目标", "计划", "策略", "措施",
    "步骤", "阶段", "层次", "水平", "标准", "要求", "条件", "环境", "背景", "基础", "前提",
    "核心", "关键", "重点", "难点", "要点", "细节", "整体", "局部", "全局", "个体", "集体",
    "知识", "技能", "能力", "经验", "实践", "理论", "概念", "定义", "解释", "描述", "说明",
    "分析", "研究", "探讨", "讨论", "论述", "阐述", "表达", "表示", "体现", "反映", "表现",
    "显示", "表明", "证明", "验证", "确认", "确定", "决定", "选择", "判断", "评价", "评估",
    "测量", "计算", "统计", "比较", "对比", "区分", "分类", "归纳", "总结", "概括", "综合",
    "分解", "拆分", "组合", "整合", "优化", "改进", "提升", "增强", "降低", "减少", "增加",
    "扩大", "缩小", "调整", "修改", "改变", "更新", "升级", "降级", "替换", "删除", "添加",
    "建立", "搭建", "设计", "开发", "实现", "执行", "运行", "操作",
    "处理", "管理", "控制", "监控", "维护", "保护", "保存", "备份", "恢复", "重置", "初始化",
    "配置", "设置", "安装", "部署", "发布", "上线", "下线", "启动", "停止", "暂停", "继续",
    "中断", "终止", "结束", "完成", "成功", "失败", "错误", "异常", "警告", "提示", "注意",
    "谨慎", "小心", "确保", "保证", "保障", "维持", "保持", "持续", "不断", "逐步", "逐渐",
    "快速", "缓慢", "立即", "马上", "暂时", "临时", "长期", "短期", "定期", "不定期",
    "经常", "偶尔", "有时", "总是", "从不", "很少", "大多", "主要", "次要", "再次",
    "初次", "首次", "最后", "最终", "最初", "开始", "开头", "结尾", "末尾", "中间",
    "上下", "左右", "前后", "内外", "表里", "深浅", "高低", "大小", "长短", "宽窄",
    "厚薄", "轻重", "快慢", "强弱", "难易", "好坏", "优劣", "对错", "真假", "虚实",
    "正副", "主次", "先后", "早晚", "新旧", "老幼", "男女", "公私", "官民", "敌友",
    "远近", "亲疏", "冷热", "干湿", "净脏", "明暗", "清浊", "香臭", "甜苦", "酸辣",
    "咸淡", "软硬", "脆韧", "滑涩", "松紧", "稀稠", "满空", "有无", "是非", "成败",
    "得失", "利害", "祸福", "吉凶", "善恶", "美丑", "荣辱", "贵贱", "贫富", "强弱",
    "胜败", "输赢", "存亡", "生死", "动静", "开合", "聚散", "离合", "分合", "升降",
    "沉浮", "起伏", "波动", "震荡", "稳定", "平衡", "协调", "和谐", "统一", "对立",
    "矛盾", "冲突", "竞争", "合作", "互助", "共享", "共赢", "互利", "互惠", "平等",
    "公正", "公平", "公开", "透明", "诚信", "信任", "尊重", "理解", "包容", "宽容",
    "忍耐", "坚持", "努力", "奋斗", "拼搏", "进取", "创新", "创造", "发明", "发现",
    "探索", "寻求", "追求", "向往", "期望", "希望", "愿望", "梦想", "理想", "幻想",
    "想象", "联想", "思考", "思索", "考虑", "顾虑", "担忧", "担心", "害怕", "恐惧",
    "紧张", "焦虑", "压力", "负担", "责任", "义务", "权利", "权力", "利益", "好处",
    "优点", "缺点", "长处", "短处", "亮点", "暗点", "热点", "冷点", "焦点", "重点",
    "中心", "重心", "要害", "命脉", "根基", "根本", "本质",
    "实质", "性质", "属性", "特征", "特色", "特质", "品格", "品质", "品德",
    "道德", "伦理", "规范", "规则", "准则", "原则", "标准", "尺度", "界限", "范围",
    "领域", "范畴", "方面", "层面", "角度", "视角", "立场", "观点", "看法", "意见",
    "建议", "提议", "方案", "计划", "规划", "策划", "设计", "构思", "设想", "假想",
    "假定", "假设", "预测", "预计", "预料", "预期", "期望", "展望", "预见", "预知",
    "先知", "先见", "远见", "卓见", "高见", "浅见", "偏见", "成见", "主见", "己见",
    "私见", "公见", "共识", "共同", "公共", "大众", "群众", "民众", "人民", "公民",
    "国民", "居民", "村民", "市民", "职工", "员工", "人员", "成员", "分子", "份子",
    "个体", "个人", "本人", "自身", "自己", "自我", "本我", "超我", "真我", "假我",
    "大我", "小我", "旧我", "新我", "主我", "客我", "你", "我", "他", "她", "它",
    "们", "谁", "哪", "什么", "怎么", "为什么", "多少", "几", "么", "呢", "吧", "啊",
    "哦", "嗯", "哎", "哟", "嘿", "哼", "哈", "呵", "嘻", "嗤", "呸", "嘘", "吱",
    "嘎", "呱", "咚", "砰", "啪", "嗒", "嘀", "嘟", "噜", "嗦",
])


# High-quality Chinese technical suffixes — terms containing these are preserved
_HIGH_QUALITY_SUFFIXES = [
    "架构", "策略", "模式", "流程", "门禁", "回滚", "验证", "部署", "索引", "章节",
    "术语", "表格", "依赖", "安全", "构建", "静态", "配置", "优化", "测试", "集成",
    "监控", "报警", "审计", "备份", "恢复", "迁移", "升级", "降级", "发布", "上线",
    "网络", "存储", "缓存", "队列", "路由", "网关", "代理", "负载", "均衡", "集群",
    "容器", "编排", "调度", "服务", "注册", "发现", "治理", "规范", "标准", "协议",
    "接口", "模型", "算法", "引擎", "框架", "平台", "系统", "应用", "组件", "模块",
    "工具", "脚本", "命令", "参数", "选项", "标志", "版本", "分支", "标签", "提交",
    "合并", "冲突", "差异", "补丁", "代码", "源码", "二进制", "库", "包", "依赖项",
    "运行时", "编译时", "链接时", "执行时", "初始化", "配置项", "环境变量", "密钥",
    "证书", "令牌", "凭证", "权限", "角色", "策略", "规则", "过滤器", "拦截器", "中间件",
    "前端", "后端", "全栈", "客户端", "服务端", "浏览器", "服务器", "数据库", "数据",
    "文件", "目录", "路径", "链接", "符号链接", "挂载点", "分区", "卷", "快照", "镜像",
    "模板", "配置", "清单", "清单文件", "锁文件", "日志文件", "配置文件", "资源文件",
    "构建产物", "输出目录", "源目录", "工作目录", "临时目录", "缓存目录", "数据目录",
    "安装目录", "卸载", "清理", "重置", "初始化", "配置", "设置", "调整", "修改", "更新",
    "同步", "异步", "并行", "并发", "串行", "顺序", "随机", "轮询", "推送", "拉取",
    "订阅", "发布", "广播", "组播", "单播", "点对点", "端到端", "客户端", "服务端",
    "请求", "响应", "连接", "会话", "通道", "管道", "套接字", "端口", "地址", "域名",
    "主机", "实例", "节点", "集群", "分片", "副本", "主从", "读写", "冷热", "温冷",
    "压缩", "解压", "加密", "解密", "编码", "解码", "序列化", "反序列化", "转换", "映射",
    "匹配", "搜索", "查询", "过滤", "排序", "分组", "聚合", "统计", "计算", "分析",
    "比较", "对比", "评估", "评价", "评分", "排名", "排序", "分页", "分片", "分区",
    "切分", "拆分", "合并", "组合", "整合", "聚合", "汇总", "归纳", "总结", "概括",
]


# Two-character Chinese terms that are too generic or status-like to be useful glossary terms
_BAD_2CHAR_TERMS = frozenset([
    "成功", "失败", "完成", "通过", "正常", "异常", "可用", "启用", "禁用",
    "存在", "已经", "没有", "以及", "然后", "因此", "但是", "如果", "为了",
    "可以", "需要", "当前", "进行", "使用", "说明", "介绍", "包含", "包括",
    "一个", "一种", "这个", "这些", "那些", "什么", "怎么", "这里", "那里",
    "现在", "之后", "之前", "正在", "能够", "应该", "必须", "可能", "一定",
    "非常", "特别", "比较", "更加", "最好", "很多", "不少", "许多", "各种",
    "部分", "方面", "情况", "内容", "方法", "方式", "结果", "目的", "意义",
    "作用", "影响", "关系", "结构", "形式", "类型", "特点", "优势", "劣势",
    "挑战", "机会", "发展", "变化", "趋势", "方向", "目标", "计划", "措施",
    "层次", "水平", "要求", "条件", "环境", "背景", "基础", "前提", "核心",
    "关键", "重点", "难点", "要点", "细节", "整体", "局部", "全局", "个体",
    "集体", "知识", "技能", "能力", "经验", "实践", "理论", "概念", "定义",
    "分析", "研究", "探讨", "讨论", "论述", "阐述", "表达", "表示", "体现",
    "显示", "表明", "证明", "验证", "确认", "确定", "决定", "选择", "判断",
    "评价", "评估", "测量", "计算", "统计", "区分", "分类", "归纳", "总结",
    "概括", "综合", "分解", "优化", "改进", "提升", "增强", "降低", "减少",
    "增加", "扩大", "缩小", "调整", "改变", "更新", "升级", "降级", "替换",
    "删除", "添加", "建立", "搭建", "设计", "开发", "实现", "执行", "运行",
    "操作", "处理", "管理", "控制", "监控", "维护", "保护", "保存", "备份",
    "恢复", "重置", "初始化", "配置", "设置", "安装", "部署", "发布", "上线",
    "下线", "启动", "停止", "暂停", "继续", "中断", "终止", "结束", "错误",
    "警告", "提示", "注意", "谨慎", "小心", "确保", "保证", "保障", "维持",
    "保持", "持续", "不断", "逐步", "逐渐", "快速", "缓慢", "立即", "马上",
    "暂时", "临时", "长期", "短期", "定期", "经常", "偶尔", "有时", "总是",
    "从不", "很少", "大多", "主要", "次要", "再次", "初次", "首次", "最后",
    "最终", "最初", "开始", "开头", "结尾", "末尾", "中间", "上下", "左右",
    "前后", "内外", "表里", "深浅", "高低", "大小", "长短", "宽窄", "厚薄",
    "轻重", "快慢", "强弱", "难易", "好坏", "优劣", "对错", "真假", "虚实",
    "正副", "主次", "先后", "早晚", "新旧", "老幼", "男女", "公私", "官民",
    "敌友", "远近", "亲疏", "冷热", "干湿", "净脏", "明暗", "清浊", "香臭",
    "甜苦", "酸辣", "咸淡", "软硬", "脆韧", "滑涩", "松紧", "稀稠", "满空",
    "有无", "是非", "成败", "得失", "利害", "祸福", "吉凶", "善恶", "美丑",
    "荣辱", "贵贱", "贫富", "强弱", "胜败", "输赢", "存亡", "生死", "动静",
    "开合", "聚散", "离合", "分合", "升降", "沉浮", "起伏", "波动", "震荡",
    "稳定", "平衡", "协调", "和谐", "统一", "对立", "矛盾", "冲突", "竞争",
    "合作", "互助", "共享", "共赢", "互利", "互惠", "平等", "公正", "公平",
    "公开", "透明", "诚信", "信任", "尊重", "理解", "包容", "宽容", "忍耐",
    "坚持", "努力", "奋斗", "拼搏", "进取", "创新", "创造", "发明", "发现",
    "探索", "寻求", "追求", "向往", "期望", "希望", "愿望", "梦想", "理想",
    "幻想", "想象", "联想", "思考", "思索", "考虑", "顾虑", "担忧", "担心",
    "害怕", "恐惧", "紧张", "焦虑", "压力", "负担", "责任", "义务", "权利",
    "权力", "利益", "好处", "优点", "缺点", "长处", "短处", "亮点", "暗点",
    "热点", "冷点", "焦点", "重点", "中心", "重心", "要害", "命脉", "根基",
    "根本", "本质", "实质", "性质", "属性", "特征", "特色", "特质", "品格",
    "品质", "品德", "道德", "伦理", "规范", "规则", "准则", "原则", "标准",
    "尺度", "界限", "范围", "领域", "范畴", "方面", "层面", "角度", "视角",
    "立场", "观点", "看法", "意见", "建议", "提议", "方案", "计划", "规划",
    "策划", "构思", "设想", "假想", "假定", "假设", "预测", "预计", "预料",
    "预期", "展望", "预见", "预知", "先知", "先见", "远见", "卓见", "高见",
    "浅见", "偏见", "成见", "主见", "己见", "私见", "公见", "共识", "共同",
    "公共", "大众", "群众", "民众", "人民", "公民", "国民", "居民", "村民",
    "市民", "职工", "员工", "人员", "成员", "分子", "份子", "个体", "个人",
    "本人", "自身", "自己", "自我", "本我", "超我", "真我", "假我", "大我",
    "小我", "旧我", "新我", "主我", "客我", "你", "我", "他", "她", "它",
    "们", "谁", "哪", "什么", "怎么", "为什么", "多少", "几", "么", "呢",
    "吧", "啊", "哦", "嗯", "哎", "哟", "嘿", "哼", "哈", "呵", "嘻", "嗤",
    "呸", "嘘", "吱", "嘎", "呱", "咚", "砰", "啪", "嗒", "嘀", "嘟", "噜", "嗦",
    "总计", "限制", "禁止", "明确",
])


def _clean_term(t: str) -> str:
    """Clean markdown symbols and normalize whitespace from a term candidate."""
    t = re.sub(r"[*#`>\[\]()]", "", t)
    # Strip leading/trailing table syntax and punctuation
    t = re.sub(r"^[|\-\s]+", "", t)
    t = re.sub(r"[|\-\s]+$", "", t)
    # Strip leading em-dash, en-dash, bullets
    t = re.sub(r"^[—–\-•\s]+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _split_chinese_phrases(t: str) -> list[str]:
    """Split a Chinese phrase on delimiters and return valid sub-phrases."""
    delimiters = r"[的与和及或：:,，、（）()\-—/]"
    parts = re.split(delimiters, t)
    result = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        cc = re.findall(r"[\u4e00-\u9fff]", p)
        if 2 <= len(cc) <= 12:
            result.append(p)
    return result


def _has_sentence_structure(t: str) -> bool:
    """Check if a Chinese fragment has obvious sentence structure."""
    # Contains sentence-ending punctuation
    if re.search(r"[。！？；\.\!\?]", t):
        return True
    # Contains multiple verb phrases
    verb_markers = ["通过", "使用", "进行", "基于", "作为", "为了", "如果", "然后", "因此", "但是"]
    count = sum(1 for v in verb_markers if v in t)
    if count >= 2:
        return True
    return False


def _is_meaningful_chinese(t: str, source_type: str = "general") -> bool:
    """Check if a Chinese term is meaningful (not stop-word or fragment)."""
    if not t:
        return False
    if not re.search(r"[\u4e00-\u9fff]", t):
        return True

    chinese_chars = re.findall(r"[\u4e00-\u9fff]", t)
    cc_count = len(chinese_chars)

    # Length rules
    if cc_count < 2:
        return False
    if cc_count > 12:
        return False
    if 11 <= cc_count <= 12 and source_type not in ("title", "bold", "code"):
        return False

    # Filter 2-char terms that are too generic/status-like
    if cc_count == 2 and t in _BAD_2CHAR_TERMS:
        return False

    # Filter sentence structures
    if _has_sentence_structure(t):
        return False

    # Filter fragment starts
    fragment_starts = [
        "本书", "本文", "本章", "这个", "这些", "那些", "通过", "如何", "进行", "使用",
        "包括", "包含", "说明", "介绍", "可以", "需要", "当前", "已经", "没有", "以及",
        "然后", "因此", "但是", "如果", "为了", "基于", "作为", "本次", "任何", "每个",
    ]
    for fs in fragment_starts:
        if t.startswith(fs) and len(t) > len(fs) + 2:
            return False

    # Filter fragment ends
    fragment_ends = [
        "的", "了", "和", "与", "及", "或", "把", "将", "为", "对", "从", "到",
        "在", "是", "中", "上", "下", "里", "内", "外", "以及", "通过", "进行",
        "使用", "包括", "包含", "说明", "介绍", "验证报告", "可运行性验证报告",
    ]
    for fe in fragment_ends:
        if t.endswith(fe):
            prefix = t[:-len(fe)]
            prefix_cc = re.findall(r"[\u4e00-\u9fff]", prefix)
            prefix_meaningful = [c for c in prefix_cc if c not in _CHINESE_STOP_WORDS]
            if len(prefix_meaningful) < 2 or len(prefix_cc) <= 2:
                return False
            # Reject short terms that end with fragment markers
            if cc_count <= 4:
                return False

    # Mixed-term fragment check: if Chinese part starts with "未" + short, reject
    if re.search(r"[A-Za-z]", t):
        chinese_part = re.sub(r"[A-Za-z0-9\s\-_\/\.\(\)\[\]]+", "", t)
        if chinese_part.startswith("未") and len(chinese_part) <= 4:
            return False
        if chinese_part in _BAD_2CHAR_TERMS:
            return False
        # Check if any Chinese subpart is a status word and dominates the term
        for sw in _STATUS_WORDS:
            if len(sw) >= 2 and sw in chinese_part and sw != chinese_part:
                if len(sw) >= len(chinese_part) * 0.5:
                    return False

    # Meaningful char check
    meaningful_chars = [c for c in chinese_chars if c not in _CHINESE_STOP_WORDS]
    if len(meaningful_chars) < 2:
        return False

    return True


# ── Strict code / bold term filtering ─────────────────────────────────────

# Shell / command-line indicators that disqualify a term from glossary/topic
_SHELL_COMMAND_INDICATORS = [
    "$", "bash", "sh ", "zsh", "powershell", "cmd", "pnpm", "npm", "node:",
    "python", "apt", "install", "check", "build", "run", "echo", "sudo",
]

# Status symbols that disqualify a term
_STATUS_SYMBOLS = ["✅", "❌", "⚠️", "✔️", "✘", "PASS", "FAIL", "OK", "DONE"]

# State phrases that disqualify a term (exact match or strong containment)
_STATE_PHRASES = [
    "现在被证实可行", "已经验证可行", "验证通过", "可以运行", "构建成功",
    "部署成功", "测试通过", "无外部 CDN 依赖", "无外部依赖", "外部依赖", "CDN 依赖",
]

# Code-term specific low-quality Chinese words (when code term is English + these)
_CODE_LOW_QUALITY_CHINESE = frozenset([
    "支持", "服务", "管理", "控制", "处理", "操作", "运行", "执行", "实现",
    "使用", "通过", "进行", "包含", "包括", "说明", "介绍", "提供",
    "获得", "得到", "成为", "作为", "用于", "用来", "用来", "用以",
])

# Negative / state prefixes that disqualify terms containing strong suffixes
_NEGATION_PREFIXES = ["无", "未", "不", "非", "没有", "已", "当前", "现在", "可", "可以", "需要"]


def _is_shell_command_term(t: str) -> bool:
    """Check if a term looks like a shell command or CLI snippet."""
    t_lower = t.lower()
    for indicator in _SHELL_COMMAND_INDICATORS:
        if indicator in t_lower:
            return True
    return False


def _has_status_symbol(t: str) -> bool:
    """Check if a term contains status symbols like ✅ ❌ etc."""
    for sym in _STATUS_SYMBOLS:
        if sym in t:
            return True
    return False


def _is_version_or_number(t: str) -> bool:
    """Check if a term is a version number, pure number, or number+unit."""
    if re.match(r"^v?\d+(\.\d+)*\s*[✅❌✔️✘]?$", t, re.IGNORECASE):
        return True
    if re.match(r"^\d+\+?$", t):
        return True
    if re.match(r"^\d+\+?\s*[A-Za-z%]+$", t):
        return True
    if re.match(r"^\d+\s+\w+$", t):
        return True
    return False


def _is_incomplete_chinese_fragment(t: str) -> bool:
    """Check if a term is an incomplete fragment (Chinese or code)."""
    # Contains newline
    if "\n" in t:
        return True
    # Contains emoji or status symbols
    if re.search(r"[⏳✅❌⚠️✔️✘⏸️▶️⏹️⏺️⏭️⏮️⏯️⏩⏪⏫⏬⏰⏱️⏲️⌛]", t):
        return True
    # Starts with Chinese but contains state phrases
    for sp in _STATE_PHRASES:
        if sp in t:
            return True

    has_chinese = bool(re.search(r"[\u4e00-\u9fff]", t))

    if has_chinese:
        # Ends with opening bracket or delimiter
        if re.search(r"[（\(：:，、]$", t):
            return True
        # Ends with number / punctuation (like "） 2.")
        if re.search(r"[\d\.\)）]$", t):
            return True
        # Contains too many spaces (likely sentence fragment)
        if t.count(" ") >= 3:
            return True
        # Starts with conjunction/particle indicating incompleteness
        incomplete_starts = [
            "但", "而", "且", "或", "若", "如", "即", "则", "故", "因", "为", "以", "于",
            "被", "将", "把", "对", "从", "向", "与", "及", "以及", "并且", "但是", "然而",
            "因此", "所以", "如果", "即使", "虽然", "尽管", "不论", "不管", "无论", "只要",
            "只有", "除非", "除了", "除", "之外", "其中", "之间", "之前", "之后", "之上",
            "之下", "之中", "之内", "以来", "以内", "以前", "以后", "以上", "以下",
            "试图", "尝试", "打算", "准备", "计划", "考虑", "决定", "选择", "判断",
            "属性", "类型", "声明", "定义", "赋值", "取值", "调用", "返回", "传入", "传出",
        ]
        for ist in incomplete_starts:
            if t.startswith(ist) and len(t) > len(ist) + 1:
                return True
        # Code term with Chinese but no technical markers (file ext, path, config key)
        # If it's mostly Chinese and looks like a sentence fragment, reject
        if t.count(" ") >= 1:
            # Contains spaces + Chinese = likely sentence fragment in code comment
            chinese_chars = re.findall(r"[\u4e00-\u9fff]", t)
            if len(chinese_chars) >= 4 and not re.search(r"[\./\-_][a-zA-Z]+", t):
                return True
            # English + space + Chinese low-quality word
            if len(chinese_chars) <= 3:
                for lq in _CODE_LOW_QUALITY_CHINESE:
                    if t.endswith(lq) or t.endswith(" " + lq):
                        return True
    else:
        # No Chinese characters — check for pure punctuation/number garbage
        # Reject if mostly non-alphanumeric (like "） 2.")
        alnum_chars = re.findall(r"[\w]", t)
        if len(alnum_chars) <= 2:
            return True
        # Reject if it's just numbers and punctuation
        if re.match(r"^[\s\d\.\)）\(\（,，]+$", t):
            return True

    return False


def _is_quality_topic(t: str, source_type: str = "general", freq: int = 1) -> bool:
    """Check if a topic/term is high-quality enough for Topic Index."""
    if not t:
        return False
    t_clean = t.strip()
    t_lower = t_clean.lower()

    # Filter status words
    if t_clean in _STATUS_WORDS or t_lower in _STATUS_WORDS:
        return False

    # Filter low-quality single words
    if t_lower in _LOW_QUALITY_TOPICS:
        return False

    # Filter pure status words (English)
    if t_lower in ("success", "failed", "passed", "error", "warning", "info", "debug", "trace"):
        return False

    # Filter single character
    if len(t_clean) == 1:
        return False

    # Filter pure numbers
    if re.match(r"^\d+$", t_clean):
        return False

    # Filter version numbers like v22.22.0, 10.32.1
    if re.match(r"^v?\d+(\.\d+)*$", t_clean, re.IGNORECASE):
        return False

    # Filter pure symbols
    if re.match(r"^[^\w\u4e00-\u9fff]+$", t_clean):
        return False

    # ── Strict code/bold term filtering ───────────────────────────────────
    if source_type in ("code", "bold"):
        # Reject shell command snippets
        if _is_shell_command_term(t_clean):
            return False
        # Reject status symbols
        if _has_status_symbol(t_clean):
            return False
        # Reject version numbers / number units
        if _is_version_or_number(t_clean):
            return False
        # Reject incomplete Chinese fragments
        if _is_incomplete_chinese_fragment(t_clean):
            return False
        # Code length limits
        if source_type == "code":
            if len(t_clean) > 35:
                return False
            if t_clean.count(" ") >= 4:
                return False
            if "\n" in t_clean:
                return False

    # ── Strong suffix tightening ──────────────────────────────────────────
    # Strong suffixes alone should not save a term if it has negation/state prefix
    has_strong_suffix = any(suffix in t_clean for suffix in _HIGH_QUALITY_SUFFIXES)
    if has_strong_suffix:
        for prefix in _NEGATION_PREFIXES:
            if t_clean.startswith(prefix):
                # Only allow if the term is clearly a technical compound (2+ meaningful chars after prefix)
                remainder = t_clean[len(prefix):]
                remainder_cc = re.findall(r"[\u4e00-\u9fff]", remainder)
                if len(remainder_cc) < 2:
                    return False
                # Also reject if remainder is mostly stop words
                meaningful = [c for c in remainder_cc if c not in _CHINESE_STOP_WORDS]
                if len(meaningful) < 2:
                    return False
        # Reject if the term is a state phrase even with strong suffix
        for sp in _STATE_PHRASES:
            if sp in t_clean:
                return False

    # Chinese-specific checks
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", t_clean)
    if chinese_chars:
        if len(chinese_chars) < 2:
            return False
        if len(chinese_chars) > 12:
            return False
        # Must have at least 2 meaningful chars
        meaningful = [c for c in chinese_chars if c not in _CHINESE_STOP_WORDS]
        if len(meaningful) < 2:
            return False
        # Run full Chinese quality check
        if not _is_meaningful_chinese(t_clean, source_type=source_type):
            return False
        # Additional sub-status check for mixed terms
        if re.search(r"[A-Za-z]", t_clean):
            cp = re.sub(r"[A-Za-z0-9\s\-_\/\.\(\)\[\]]+", "", t_clean)
            for sw in _STATUS_WORDS:
                if len(sw) >= 2 and sw in cp and sw != cp:
                    if len(sw) >= len(cp) * 0.5:
                        return False
    else:
        # English length check
        if len(t_lower) < 3:
            return False

    # Report phrase check: filter standalone report phrases unless combined with technical terms
    has_high_quality = any(suffix in t_clean for suffix in _HIGH_QUALITY_SUFFIXES)
    if not has_high_quality:
        for rp in _REPORT_PHRASES:
            if t_clean == rp or (len(t_clean) <= len(rp) + 2 and rp in t_clean):
                return False

    # Filter code terms containing table syntax or excessive punctuation
    if source_type == "code" and ("|" in t_clean or t_clean.count("...") >= 2):
        return False

    # Filter terms that are mostly numbers/units (like "37 MB", "65+", "0.37 KB")
    if re.match(r"^\d+[\s\w]*$", t_clean) or re.match(r"^\d+\+?\s*[A-Za-z]+$", t_clean):
        return False
    if re.match(r"^\d+\.\d+\s*[A-Za-z]+$", t_clean):
        return False

    # Filter Chinese terms starting with low-quality single words if short
    if chinese_chars and len(chinese_chars) <= 4:
        low_quality_starts = ["无", "有", "是", "否", "已", "未", "不"]
        for lqs in low_quality_starts:
            if t_clean.startswith(lqs) and t_clean != lqs:
                # Allow if combined with high-quality suffix
                if not has_high_quality:
                    return False

    # Frequency check: if not from high-quality source, require at least 2 occurrences
    if source_type not in ("title", "bold", "code", "header") and freq < 2:
        return False

    return True


def _topic_quality_score(t: str, source_type: str = "general", freq: int = 1) -> int:
    """Score a topic candidate. Higher is better."""
    score = 0
    t_clean = t.strip()

    # Source type bonus
    if source_type == "title":
        score += 10
    elif source_type == "bold":
        score += 8
    elif source_type == "code":
        score += 7
    elif source_type == "header":
        score += 6
    elif source_type == "mixed":
        score += 5
    elif source_type == "chinese":
        score += 3
    else:
        score += 1

    # Frequency bonus
    if freq >= 5:
        score += 5
    elif freq >= 3:
        score += 3
    elif freq >= 2:
        score += 1

    # Length bonus (not too short, not too long)
    cc = re.findall(r"[\u4e00-\u9fff]", t_clean)
    if cc:
        if 3 <= len(cc) <= 6:
            score += 3
        elif 2 <= len(cc) <= 8:
            score += 1
    else:
        if 4 <= len(t_clean) <= 20:
            score += 2

    # High-quality suffix bonus
    for suffix in _HIGH_QUALITY_SUFFIXES:
        if suffix in t_clean:
            score += 2
            break

    # Penalty for report phrases (unless combined with technical terms)
    report_only = True
    for suffix in _HIGH_QUALITY_SUFFIXES:
        if suffix in t_clean:
            report_only = False
            break
    if report_only:
        for rp in _REPORT_PHRASES:
            if rp in t_clean and len(t_clean) <= len(rp) + 2:
                score -= 5
                break

    return score


def _is_quality_english_term(t: str, source_type: str = "general", freq: int = 1) -> bool:
    """Check if an English term is high-quality enough for glossary/topic."""
    if not t:
        return False
    t_clean = t.strip()
    t_lower = t_clean.lower()

    # Length check
    if len(t_clean) < 3 or len(t_clean) > 60:
        return False

    # Word count check (1-4 words)
    words = t_clean.split()
    if len(words) < 1 or len(words) > 4:
        return False

    # Single word: at least 5 letters, not a stop word
    if len(words) == 1:
        if len(t_clean) < 5:
            return False
        if t_lower in _ENGLISH_STOP_WORDS:
            return False
        # Must be alphabetic (no numbers/symbols)
        if not t_clean.replace("-", "").replace("_", "").isalpha():
            return False
    else:
        # Multi-word: check each word
        for w in words:
            w_lower = w.lower().strip(".,;:!?")
            if len(w_lower) < 2:
                continue
            if w_lower in _ENGLISH_STOP_WORDS and len(words) <= 2:
                # If it's a 2-word phrase and one word is a stop word, that's okay
                # if the other word is meaningful
                pass

    # Filter version numbers
    if re.match(r"^v?\d+(\.\d+)*$", t_clean, re.IGNORECASE):
        return False

    # Filter pure numbers
    if re.match(r"^\d+$", t_clean):
        return False

    # Filter pure symbols
    if re.match(r"^[^\w\-]+$", t_clean):
        return False

    # Filter shell commands
    if _is_shell_command_term(t_clean):
        return False

    # Filter status symbols
    if _has_status_symbol(t_clean):
        return False

    # Filter URL-like
    if "http" in t_lower or "www." in t_lower or ".com" in t_lower:
        return False

    # Filter file extensions
    if re.search(r"\.(pdf|html|htm|docx|epub|txt|md|py|js|json|yaml|yml)$", t_lower):
        return False

    # Academic concept bonus: if it's in our academic concept list, it's likely good
    is_academic = t_lower in _ENGLISH_ACADEMIC_CONCEPTS

    # Title Case bonus: if it looks like a proper noun or concept
    is_title_case = all(w[0].isupper() for w in words if w[0].isalpha()) and len(words) >= 2

    # Frequency check for non-academic, non-title-case terms
    if not is_academic and not is_title_case and source_type not in ("title", "bold", "code"):
        if freq < 2:
            return False

    return True


def extract_terms(text: str) -> list[dict]:
    """Extract candidate terms from source text with Chinese and English filtering."""
    terms = []
    seen = set()

    def add_term(t: str, typ: str, ctx: str) -> None:
        t = _clean_term(t)
        if not t:
            return
        key = t.lower()
        if key in seen:
            return
        if len(t) < 2 or len(t) > 60:
            return
        # Determine source type for quality check
        source_type = "general"
        if typ == "bold":
            source_type = "bold"
        elif typ == "code":
            source_type = "code"
        elif typ == "mixed":
            source_type = "mixed"
        elif typ == "chinese":
            source_type = "chinese"
        elif typ == "technical":
            source_type = "technical"
        elif typ == "english_academic":
            source_type = "english_academic"
        elif typ == "english_title":
            source_type = "english_title"

        # Check if term has Chinese characters
        has_chinese = bool(re.search(r"[\u4e00-\u9fff]", t))

        if has_chinese:
            # Apply Chinese quality filtering
            if not _is_quality_topic(t, source_type=source_type, freq=1):
                # Try splitting on delimiters for Chinese terms
                sub_phrases = _split_chinese_phrases(t)
                for sp in sub_phrases:
                    if _is_quality_topic(sp, source_type=source_type, freq=1):
                        sp_key = sp.lower()
                        if sp_key not in seen:
                            seen.add(sp_key)
                            terms.append({"term": sp, "type": typ, "context": ctx})
                return
        else:
            # Apply English quality filtering
            if not _is_quality_english_term(t, source_type=source_type, freq=1):
                return

        seen.add(key)
        terms.append({"term": t, "type": typ, "context": ctx})

    # Bold terms (both Chinese and English)
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        add_term(m.group(1), "bold", "found in source text")

    # Code terms
    for m in re.finditer(r"`([^`]+)`", text):
        add_term(m.group(1), "code", "technical term in source")

    # Technical terms with underscores/hyphens
    for m in re.finditer(r"\b([A-Za-z]+(?:[_-][A-Za-z]+)+)\b", text):
        add_term(m.group(1), "technical", "technical term in source")

    # Mixed-language terms
    for m in re.finditer(r"\b([A-Za-z]+\s+[\u4e00-\u9fff]{2,8})\b", text):
        add_term(m.group(1), "mixed", "mixed-language term in source")
    for m in re.finditer(r"\b([\u4e00-\u9fff]{2,8}\s+[A-Za-z]+)\b", text):
        add_term(m.group(1), "mixed", "mixed-language term in source")

    # Chinese terms
    for m in re.finditer(r"[\u4e00-\u9fff]{2,12}", text):
        add_term(m.group(0), "chinese", "term in source text")

    # English academic concepts: Title Case phrases (2-4 words)
    # But filter out obvious false positives from titles/sentences
    for m in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b", text):
        candidate = m.group(1)
        # Skip if it looks like part of a sentence (preceded by lowercase word)
        start_pos = m.start()
        if start_pos > 0:
            prev_char = text[start_pos - 1]
            if prev_char.islower():
                continue
        # Skip if followed by lowercase (part of sentence)
        end_pos = m.end()
        if end_pos < len(text):
            next_char = text[end_pos]
            if next_char.islower():
                continue
        # Skip common false positives
        false_positives = ["The", "This", "That", "These", "Those", "There", "Their", "They", "Then", "Than"]
        words = candidate.split()
        if words[0] in false_positives:
            continue
        # Skip if all words are common words
        common_words = {"The", "And", "For", "But", "Not", "Are", "Was", "Were", "Has", "Had", "Have", "Will", "Would", "Could", "Should", "May", "Might", "Can", "Shall"}
        if all(w in common_words for w in words):
            continue
        add_term(candidate, "english_title", "Title Case concept in source")

    # English academic concepts: hyphenated concepts
    for m in re.finditer(r"\b([a-z]+-[a-z]+(?:-[a-z]+)*)\b", text, re.IGNORECASE):
        add_term(m.group(1), "english_academic", "hyphenated concept in source")

    # English academic concepts: frequent academic words (from our list)
    for concept in _ENGLISH_ACADEMIC_CONCEPTS:
        # Count frequency
        freq = text.lower().count(concept.lower())
        if freq >= 2:
            add_term(concept, "english_academic", f"academic concept (freq={freq})")

    return terms[:40]


def usage_notes_for_mode(mode: str) -> str:
    notes = {
        "technical": "Use this chapter as a technical reference. Look for implementation details, code examples, and architectural decisions.",
        "narrative": "Use this chapter for thematic analysis, character development, and narrative structure.",
        "article": "Use this chapter for understanding arguments, evidence, and background context suitable for summarization.",
        "api-docs": "Use this chapter for interface definitions, parameter descriptions, usage examples, and known limitations.",
        "project-docs": "Use this chapter for architecture overviews, project status, decision records, and next steps.",
    }
    return notes.get(mode, "Use this chapter as a general reference.")


def generate_chapter_file(chapter: dict, slug: str, mode: str) -> str:
    """Generate a chapter markdown file with extractive content (no placeholders)."""
    text = chapter["text"]

    summary = extract_summary(text, max_sentences=5)
    key_points = extract_key_points(text)
    terms = extract_terms(text)
    usage = usage_notes_for_mode(mode)

    lines = [
        f"# {chapter['title']}",
        "",
        "## Source Section",
        f"Extracted from chapter/section: *{chapter['title']}*",
        "",
        "## Extractive Summary",
        summary,
        "",
        "## Key Points",
    ]
    for i, pt in enumerate(key_points, 1):
        lines.append(f"{i}. {pt}")
    if not key_points:
        lines.append("(No explicit key points found in source.)")

    lines.extend(["", "## Important Terms"])
    if terms:
        for t in terms[:10]:
            lines.append(f"- **{t['term']}** ({t['type']}): {t['context']}")
    else:
        lines.append("(No explicit terms identified in source.)")

    lines.extend([
        "",
        "## Usage Notes",
        usage,
        "",
        "## Connects To",
        "- Other chapters in this skill for related topics.",
        "- External project tools for hands-on implementation.",
    ])

    return "\n".join(lines)


def generate_glossary(chapters: list[dict]) -> str:
    """Generate glossary from extracted terms across all chapters."""
    all_terms = []
    seen = set()
    # Collect all text for frequency counting
    all_text = "\n".join(ch["text"] for ch in chapters)

    for ch in chapters:
        for t in extract_terms(ch["text"]):
            key = t["term"].lower()
            if key not in seen:
                seen.add(key)
                # Determine appropriate quality check based on language
                has_chinese = bool(re.search(r"[\u4e00-\u9fff]", t["term"]))
                is_quality = False
                if has_chinese:
                    is_quality = _is_quality_topic(t["term"], source_type=t.get("type", "general"), freq=1)
                else:
                    is_quality = _is_quality_english_term(t["term"], source_type=t.get("type", "general"), freq=1)

                if is_quality:
                    # Find related chapters
                    related_chapters = []
                    for other_ch in chapters:
                        if t["term"].lower() in other_ch["text"].lower():
                            related_chapters.append(other_ch["title"])
                    related_str = ", ".join(related_chapters[:3]) if related_chapters else ch["title"]

                    # Try to find an extractive explanation
                    explanation = "Appears in source; definition requires manual enrichment."
                    ch_text = ch["text"]
                    # Look for sentences containing the term
                    sentences = split_sentences(ch_text)
                    for sent in sentences:
                        if t["term"].lower() in sent.lower() and len(sent) > 20:
                            # Truncate if too long
                            if len(sent) > 200:
                                sent = sent[:197] + "..."
                            explanation = sent
                            break

                    all_terms.append({
                        **t,
                        "chapter": ch["title"],
                        "related_chapters": related_str,
                        "explanation": explanation,
                    })

    lines = ["# Glossary", ""]
    if not all_terms:
        lines.append("(No terms extracted from source. Consider manual enrichment.)")
        return "\n".join(lines)

    # Sort by quality: academic concepts first, then title case, then others
    def term_priority(t):
        t_lower = t["term"].lower()
        if t_lower in _ENGLISH_ACADEMIC_CONCEPTS:
            return 0
        if t.get("type") == "english_title":
            return 1
        if t.get("type") in ("bold", "code"):
            return 2
        return 3

    all_terms.sort(key=term_priority)

    for t in all_terms[:40]:
        lines.append(f"- **{t['term']}** ({t['type']}) — {t['explanation']}")
        lines.append(f"  _Related: {t['related_chapters']}_")
        lines.append("")
    return "\n".join(lines)


# ── Patterns extraction ───────────────────────────────────────────────────

_PATTERN_KEYWORDS = frozenset([
    "模式", "流程", "策略", "原则", "架构", "方案", "检查", "门禁", "回滚", "验证", "部署",
    "workflow", "pattern", "strategy", "policy", "architecture", "checklist", "gate",
    "rollback", "validation", "deployment", "process", "procedure", "methodology",
    "framework", "blueprint", "design", "plan", "approach", "technique", "tactic",
])


def _has_pattern_keyword(text: str) -> bool:
    """Check if text contains pattern-related keywords."""
    text_lower = text.lower()
    for kw in _PATTERN_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False


def _extract_pattern_evidence(chapter: dict) -> dict | None:
    """Try to extract real pattern evidence from a chapter. Returns None if insufficient."""
    text = chapter["text"]
    title = chapter["title"]
    lines = text.splitlines()

    # Check title for pattern keywords
    title_has_keyword = _has_pattern_keyword(title)

    # Look for explicit pattern descriptions
    evidence_lines = []
    for line in lines:
        if _has_pattern_keyword(line) and len(line) > 15:
            evidence_lines.append(line.strip())
        if len(evidence_lines) >= 3:
            break

    # Look for step-by-step procedures
    steps = []
    for line in lines:
        if re.match(r"^\s*(?:\d+\.\s+|Step\s+\d+[:：]\s+)", line, re.IGNORECASE):
            steps.append(line.strip())
        if len(steps) >= 3:
            break

    # Look for decision tables or checklists
    checklist_items = []
    for line in lines:
        if re.match(r"^\s*[-*]\s*\[[ xX]\]", line):
            checklist_items.append(line.strip())
        if len(checklist_items) >= 3:
            break

    if not (title_has_keyword or evidence_lines or steps or checklist_items):
        return None

    # Build evidence summary
    evidence_parts = []
    if title_has_keyword:
        evidence_parts.append(f"Title contains pattern keyword: '{title}'")
    if evidence_lines:
        evidence_parts.append(f"Source mentions: {evidence_lines[0][:100]}")
    if steps:
        evidence_parts.append(f"Contains {len(steps)} procedural steps")
    if checklist_items:
        evidence_parts.append(f"Contains {len(checklist_items)} checklist items")

    return {
        "name": title,
        "evidence": "; ".join(evidence_parts),
        "has_steps": len(steps) > 0,
        "has_checklist": len(checklist_items) > 0,
        "step_count": len(steps),
    }


def generate_patterns(chapters: list[dict], mode: str) -> str:
    """Generate patterns document with evidence-based extraction."""
    lines = ["# Patterns & Techniques", ""]

    patterns_found = []
    for ch in chapters:
        evidence = _extract_pattern_evidence(ch)
        if evidence:
            patterns_found.append({**evidence, "chapter": ch["title"]})

    if not patterns_found:
        lines.append("No strong reusable pattern detected from the source. Manual enrichment recommended.")
        lines.append("")
        lines.append("## Potential Pattern Areas")
        lines.append("")
        lines.append("Based on chapter titles, the following areas may contain reusable patterns:")
        lines.append("")
        for ch in chapters[:8]:
            lines.append(f"- **{ch['title']}** — see chapters/ch{ch['num']:02d}-{slugify(ch['title'])}.md")
        return "\n".join(lines)

    for p in patterns_found[:15]:
        lines.append(f"## {p['name']}")
        lines.append(f"- **Source evidence**: {p['evidence']}")
        lines.append(f"- **Problem it addresses**: Related to {p['chapter']}.")
        if p['has_steps']:
            lines.append(f"- **How it works**: Procedural pattern with {p['step_count']} steps. See source chapter for details.")
        elif p['has_checklist']:
            lines.append(f"- **How it works**: Checklist-based pattern. See source chapter for details.")
        else:
            lines.append(f"- **How it works**: Conceptual pattern. See source chapter for details.")
        lines.append(f"- **Where it appears**: chapters/ch{chapters.index(next(c for c in chapters if c['title'] == p['chapter']))+1:02d}-{slugify(p['chapter'])}.md")
        lines.append(f"- **Limitations**: Extracted from limited context; may need enrichment.")
        lines.append("")

    return "\n".join(lines)


def generate_cheatsheet(chapters: list[dict]) -> str:
    lines = [
        "# Cheatsheet",
        "",
        "| Task | Use This File | What to Look For |",
        "|------|---------------|------------------|",
        "| Understand the whole book | `SKILL.md` | Purpose, Core Map, Chapter Index, Topic Index |",
        "| Read a specific chapter | `chapters/chXX-<title>.md` | Extractive Summary, Key Points, Important Terms |",
        "| Look up definitions | `glossary.md` | Terms with type annotations and chapter references |",
        "| Find reusable methods | `patterns.md` | Named patterns with evidence and problem/solution structure |",
        "| Get quick rules | `cheatsheet.md` | This table and any decision matrices |",
    ]

    if chapters:
        lines.extend(["", "## Chapter Quick Reference", ""])
        lines.append("| Chapter | Topic | File |")
        lines.append("|---------|-------|------|")
        for ch in chapters[:10]:
            slug = slugify(ch["title"])
            lines.append(f"| ch{ch['num']:02d} | {ch['title']} | `chapters/ch{ch['num']:02d}-{slug}.md` |")

    return "\n".join(lines)


def _count_term_frequency(text: str, term: str) -> int:
    """Count how many times a term appears in text (case-insensitive)."""
    return text.lower().count(term.lower())


def generate_skill_md(slug: str, title: str, chapters: list[dict], language: str, mode: str) -> str:
    """Generate the master SKILL.md for the book skill."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Build quality topic index with scoring
    all_text = "\n".join(ch["text"] for ch in chapters)
    topic_candidates = []

    for ch in chapters:
        ch_text = ch["text"]
        ch_topics = []

        # From title (highest priority)
        title_clean = _clean_term(ch["title"])
        if _is_quality_topic(title_clean, source_type="title"):
            freq = _count_term_frequency(all_text, title_clean)
            score = _topic_quality_score(title_clean, source_type="title", freq=freq)
            ch_topics.append((title_clean, score, "title", ch["num"]))

        # From bold terms
        for line in ch_text.splitlines()[:40]:
            for m in re.finditer(r"\*\*(.+?)\*\*", line):
                t = _clean_term(m.group(1))
                if _is_quality_topic(t, source_type="bold"):
                    freq = _count_term_frequency(all_text, t)
                    score = _topic_quality_score(t, source_type="bold", freq=freq)
                    ch_topics.append((t, score, "bold", ch["num"]))

        # From code terms
        for line in ch_text.splitlines()[:40]:
            for m in re.finditer(r"`([^`]+)`", line):
                t = _clean_term(m.group(1))
                if _is_quality_topic(t, source_type="code"):
                    freq = _count_term_frequency(all_text, t)
                    score = _topic_quality_score(t, source_type="code", freq=freq)
                    ch_topics.append((t, score, "code", ch["num"]))

        # From headers (table headers, etc.)
        for line in ch_text.splitlines()[:30]:
            if "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                for p in parts:
                    t = _clean_term(p)
                    if _is_quality_topic(t, source_type="header"):
                        freq = _count_term_frequency(all_text, t)
                        score = _topic_quality_score(t, source_type="header", freq=freq)
                        ch_topics.append((t, score, "header", ch["num"]))

        # Deduplicate within chapter and limit to top 8
        seen_ch = set()
        ch_topics_sorted = []
        for t, score, src_type, num in sorted(ch_topics, key=lambda x: -x[1]):
            key = t.lower()
            if key not in seen_ch:
                seen_ch.add(key)
                ch_topics_sorted.append((t, score, src_type, num))
        topic_candidates.extend(ch_topics_sorted[:8])

    # Global deduplicate and sort by quality score
    seen_global = set()
    topic_index = []
    for t, score, src_type, num in sorted(topic_candidates, key=lambda x: -x[1]):
        key = t.lower()
        if key not in seen_global:
            seen_global.add(key)
            topic_index.append(f"- **{t}** → ch{num:02d}")

    # Limit global topic index to 60, but apply strict filtering first
    # Re-run quality check on topic index entries to catch state phrases
    _TOPIC_INDEX_REJECT = frozenset([
        "成功", "无", "是", "否", "完成", "通过", "正常", "异常",
        "PASS", "FAIL", "OK", "TRUE", "FALSE",
        "无外部 CDN 依赖", "外部 CDN 依赖", "无外部依赖", "CDN 依赖",
    ])
    filtered_topic_index = []
    for entry in topic_index:
        # entry format: "- **{t}** → ch{num:02d}"
        # Extract term from markdown bold
        term_match = re.search(r"\*\*(.+?)\*\*", entry)
        if term_match:
            topic_term = term_match.group(1)
            if topic_term in _TOPIC_INDEX_REJECT:
                continue
            if _is_shell_command_term(topic_term):
                continue
            if _has_status_symbol(topic_term):
                continue
            if _is_version_or_number(topic_term):
                continue
            if _is_incomplete_chinese_fragment(topic_term):
                continue
            # Reject pure status values
            if topic_term.lower() in ("success", "failed", "passed", "error", "warning", "info", "debug", "trace", "true", "false"):
                continue
        filtered_topic_index.append(entry)
    topic_index = filtered_topic_index[:60]

    chapter_table = []
    for ch in chapters:
        chapter_table.append(
            f"| ch{ch['num']:02d} | [{ch['title']}](chapters/ch{ch['num']:02d}-{slugify(ch['title'])}.md) | see chapter file |"
        )

    sections = [
        "---",
        f"name: {slug}",
        f'description: "Knowledge base from \\"{title}\\". Use when applying its frameworks, studying its concepts, or referencing its techniques."',
        "argument-hint: [topic, framework name, or chapter number]",
        "---",
        "",
        f"# {title}",
        f"**Generated**: {now} | **Chapters**: {len(chapters)} | **Mode**: {mode} | **Language**: {language}",
        "",
        "## Purpose",
        "",
        f"This skill provides structured access to the knowledge in *{title}*. "
        "It is designed for on-demand loading: only the core map and requested chapter are loaded into context.",
        "",
        "## How to Use This Skill",
        "",
        "- **Without arguments** — load the core map and chapter index for reference",
        "- **With a topic** — ask about a concept; the relevant chapter loads on demand",
        "- **With a chapter** — ask for `ch05` to load that specific chapter",
        "- **Browse** — ask \"what chapters do you have?\" to see the full index",
        "",
        "## Core Map",
        "",
        "Key topics covered by this skill:",
    ]
    for ch in chapters[:10]:
        sections.append(f"- {ch['title']}")
    sections.extend([
        "",
        "## Chapter Index",
        "",
        "| # | Title | Key Content |",
        "|---|-------|-------------|",
    ])
    sections.extend(chapter_table)
    sections.extend([
        "",
        "## Topic Index",
        "",
    ])
    sections.extend(topic_index[:60])  # Show top 60 in SKILL.md
    sections.extend([
        "",
        "## Loading Policy",
        "",
        "- SKILL.md (this file) is always loaded first (~400-4,000 tokens)",
        "- Individual chapter files are loaded only when referenced (~800-1,200 tokens each)",
        "- Glossary, patterns, and cheatsheet are loaded on explicit request",
        "- The full source text is never loaded into context",
        "",
        "## Safety / Limitations",
        "",
        "- This skill covers the source document only.",
        "- For hands-on implementation, combine with project-specific tools.",
        "- All summaries are extractive (directly from source text) without LLM enhancement.",
        "- Some definitions may be incomplete; verify against original document when precision matters.",
        "",
        "## Supporting Files",
        "",
        "- [glossary.md](glossary.md) — key terms and definitions",
        "- [patterns.md](patterns.md) — techniques and design patterns",
        "- [cheatsheet.md](cheatsheet.md) — quick reference and decision tables",
    ])
    return "\n".join(sections)


def generate_metadata(slug: str, title: str, source_path: str, language: str, mode: str,
                      char_count: int, chapter_count: int, extraction_method: str) -> dict:
    return {
        "title": title,
        "slug": slug,
        "language": language,
        "mode": mode,
        "source_path": str(Path(source_path).resolve()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "char_count": char_count,
        "chapter_count": chapter_count,
        "generator": "book-to-hermes-skill",
        "phase": "0-f",
        "extraction_method": extraction_method,
    }


def generate_source_manifest(source_path: str, method: str, format_type: str, limitations: list[str]) -> str:
    now = datetime.now(timezone.utc).isoformat()
    lim_lines = "\n".join(f"- {l}" for l in limitations)
    return f"""# Source Manifest

- **Source file**: `{source_path}`
- **Detected format**: {format_type}
- **Extraction method**: {method}
- **Generated at**: {now}
- **Tool**: book-to-hermes-skill

## Supported Formats

- Markdown (.md, .markdown)
- Plain text (.txt)
- Text PDF (.pdf)
- HTML (.html, .htm)
- DOCX (.docx)
- EPUB (.epub)

## Limitations

{lim_lines}

## Safety Notes

- HTML/EPUB extraction: scripts, styles, and interactive elements are removed before processing.
- DOCX extraction: macros and embedded objects are not executed.
- No network requests are made during extraction or generation.
- No LLM APIs are called during generation.

## Verification

To verify the source matches this skill, compare the file checksum:

```bash
sha256sum "{source_path}"
```
"""


def scan_for_secrets(text: str) -> list[str]:
    findings = []
    patterns = [
        (r"(?i)(api[_-]?key\s*[:=]\s*)['\"]?[a-z0-9_\-]{20,}['\"]?", "possible API key"),
        (r"(?i)(token\s*[:=]\s*)['\"]?[a-z0-9_\-]{20,}['\"]?", "possible token"),
        (r"(?i)(password\s*[:=]\s*)['\"]?[^\s\"']{8,}['\"]?", "possible password"),
        (r"(?i)(secret\s*[:=]\s*)['\"]?[a-z0-9_\-]{16,}['\"]?", "possible secret"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub personal access token"),
        (r"sk-[a-zA-Z0-9]{48}", "OpenAI-style API key"),
    ]
    for pat, label in patterns:
        if re.search(pat, text):
            findings.append(label)
    return findings


def main():
    parser = argparse.ArgumentParser(description="Build a Hermes book skill from a source document")
    parser.add_argument("--source", required=True, help="Path to source document")
    parser.add_argument("--slug", required=True, help="Skill directory name")
    parser.add_argument("--title", default="", help="Book title")
    parser.add_argument("--language", default="auto", help="zh / en / zh-en / auto")
    parser.add_argument("--mode", default="auto", help="technical / narrative / article / api-docs / project-docs")
    parser.add_argument("--output-dir", default=str(Path.home() / ".hermes" / "skills" / "books"), help="Output root directory")
    parser.add_argument("--allow-overwrite", default="no", help="yes to overwrite existing skill directory")
    args = parser.parse_args()

    mode = args.mode if args.mode != "auto" else "narrative"

    extraction = extract_text(args.source, mode)
    if not extraction.get("ok"):
        print(json.dumps({"ok": False, "errors": extraction.get("errors", ["Extraction failed"])}))
        sys.exit(1)

    source_path = extraction["source_path"]
    text = extraction["text"]
    method = extraction.get("extraction_method", "unknown")
    format_type = extraction.get("format", "unknown")

    title = args.title or extraction.get("title_guess", "Untitled")
    slug = slugify(args.slug or title)

    language = args.language
    if language == "auto":
        cjk_ratio = len(re.findall(r"[\u4e00-\u9fff]", text)) / max(len(text), 1)
        language = "zh" if cjk_ratio > 0.05 else "en"

    output_dir = Path(args.output_dir) / slug
    if output_dir.exists() and args.allow_overwrite.lower() != "yes":
        print(json.dumps({
            "ok": False,
            "errors": [f"Skill directory already exists: {output_dir}. Use --allow-overwrite yes to overwrite."]
        }))
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    chapters_dir = output_dir / "chapters"
    chapters_dir.mkdir(exist_ok=True)

    chapters = split_into_chapters(text, language)

    for ch in chapters:
        ch_file = chapters_dir / f"ch{ch['num']:02d}-{slugify(ch['title'])}.md"
        content = generate_chapter_file(ch, slug, mode)
        ch_file.write_text(content, encoding="utf-8")

    (output_dir / "glossary.md").write_text(generate_glossary(chapters), encoding="utf-8")
    (output_dir / "patterns.md").write_text(generate_patterns(chapters, mode), encoding="utf-8")
    (output_dir / "cheatsheet.md").write_text(generate_cheatsheet(chapters), encoding="utf-8")

    metadata = generate_metadata(slug, title, source_path, language, mode,
                                 len(text), len(chapters), method)
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    limitations = [
        "Phase 1-b: extractive summaries with table normalization, Chinese term filtering, and English academic concept extraction.",
        "Supported formats: Markdown, TXT, text PDF, HTML, DOCX, EPUB.",
        "Not supported: OCR PDF, DRM EPUB, RTF, MOBI/AZW/AZW3.",
        "HTML/EPUB extraction does not execute scripts.",
        "DOCX extraction does not execute macros or embedded objects.",
        "No LLM API was called during generation.",
        "No network requests were made during generation.",
    ]
    (output_dir / "source_manifest.md").write_text(
        generate_source_manifest(source_path, method, format_type, limitations),
        encoding="utf-8"
    )

    skill_md = generate_skill_md(slug, title, chapters, language, mode)
    (output_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    all_text = skill_md + "\n" + "\n".join(ch["text"] for ch in chapters)
    secrets = scan_for_secrets(all_text)
    if secrets:
        print(json.dumps({"ok": False, "warnings": [f"Potential secrets detected: {secrets}"]}), file=sys.stderr)

    result = {
        "ok": True,
        "slug": slug,
        "title": title,
        "output_dir": str(output_dir),
        "chapters": len(chapters),
        "char_count": len(text),
        "files_generated": [
            "SKILL.md",
            "metadata.json",
            "source_manifest.md",
            "glossary.md",
            "patterns.md",
            "cheatsheet.md",
            f"chapters/ ({len(chapters)} files)",
        ],
        "warnings": secrets,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
