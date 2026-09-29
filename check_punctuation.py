"""
检查/修复 content/*.md 里"该用全角但用了半角"的标点(，、；：()),按 build.py
文档里"正文标点一律用全角"那条规则来。

用法:
    python check_punctuation.py         只检查,列出每处疑似问题的位置和上下文
    python check_punctuation.py --fix   实际把这些半角标点替换成全角,原地改写文件

排除范围(跟 build.py 里正文标点规则的排除范围一致,--fix 也遵守同样的排除):
- frontmatter 里 key 本身的冒号(title: / summary: 这些),但 value 部分照样处理
- {{...}} 语法行、![...] 图片行、<img ...> 原始HTML图片行(路径/图题不受全角规则约束)
- 逗号/分号/冒号:只转换两侧至少一边紧挨着中文字符的情况,纯英文/数字之间的半角标点
  (比如引用的英文原句、型号编号、URL 内部)不会被动到——URL 本身是纯 ASCII,
  两侧挨不到中文字符,天然不会被误伤,所以不需要额外整行跳过含 URL 的行
  (早期版本整行跳过反而漏掉了同一行里 URL 之外的正文标点,已经去掉这条)
- 括号:不看两侧是不是中文,只要在非跳过行里出现半角 ( ) 就统一转全角(（）),
  哪怕括号里全是英文引用/型号(比如 (Tri-plane,EG3D,CVPR 2022)) 也转,
  这是用户明确要求的规则,和逗号/分号/冒号的"CJK 邻接"判定不是一回事
- 但 markdown 链接语法 [文字](目标) 里,紧跟在 ] 后面的那一对圆括号是
  链接目标(路径/URL),属于语法本身,不受这条括号规则约束,会被保护起来
  不转全角(转了会导致 markdown 解析不出链接)
"""
import glob
import os
import re
import sys

# Windows 终端默认代码页(GBK)打不出某些字符,输出强制走 UTF-8,否则脚本会在
# print 中文的时候直接崩溃(UnicodeEncodeError)。
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(ROOT, "content")

CJK = r"一-鿿"
# 半角逗号/分号/冒号,前后至少一边挨着中文字符,就当作疑似问题
HALFWIDTH_RE = re.compile(
    rf"[{CJK}][,:;]|[,:;][{CJK}]"
)
# --fix 用的替换版本:零宽断言,只替换标点本身,不吃掉两边的中文字符
FIX_RE = re.compile(rf"(?<=[{CJK}])[,:;]|[,:;](?=[{CJK}])")
# 括号不做 CJK 邻接判断,出现就算疑似问题/直接替换
PAREN_RE = re.compile(r"[()]")
# markdown 链接 ](目标) 的目标部分(含左右括号)不当作正文括号处理
LINK_TARGET_RE = re.compile(r"\]\([^()]*\)")
FULLWIDTH_MAP = {",": "，", ";": "；", ":": "：", "(": "（", ")": "）"}
FRONTMATTER_KEYS = (
    "title:", "topic:", "group:", "date:", "location:", "summary:",
    "cover:", "cover_fit:", "show_cover_in_article:", "unlisted:",
    "photo:", "email:", "phone:", "basic:", "intro:",
)


def strip_frontmatter_key(line):
    """去掉 'key: ' 这个前缀本身(它的冒号必须是半角,不受检查),只留 value 部分。"""
    for key in FRONTMATTER_KEYS:
        if line.startswith(key):
            return line[len(key):]
    return line


def matched_key(line):
    for key in FRONTMATTER_KEYS:
        if line.startswith(key):
            return key
    return None


def should_skip(line):
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("{{") or stripped.startswith("![") or stripped.startswith("<img"):
        return True
    return False


def protected_ranges(text):
    """markdown 链接 ](目标) 里目标部分的左右括号,不当作正文括号处理。"""
    return [(m.start() + 1, m.end()) for m in LINK_TARGET_RE.finditer(text)]


def in_ranges(pos, ranges):
    return any(start <= pos < end for start, end in ranges)


def fix_line(line):
    """把一行里该转全角的半角标点转掉,跳过 frontmatter key 本身的冒号和链接目标括号。"""
    key = matched_key(line)
    prefix, value = (key, line[len(key):]) if key is not None else ("", line)
    protected = protected_ranges(value)

    def convert(m):
        if in_ranges(m.start(), protected):
            return m.group(0)
        return FULLWIDTH_MAP[m.group(0)]

    value = FIX_RE.sub(convert, value)
    value = PAREN_RE.sub(convert, value)
    return prefix + value


def main():
    fix = "--fix" in sys.argv
    total = 0
    files_changed = 0
    for path in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.md"))):
        fname = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        file_hits = []
        new_lines = list(lines)
        for i, line in enumerate(lines, 1):
            if should_skip(line):
                continue
            checked = strip_frontmatter_key(line)
            protected = protected_ranges(checked)
            hits_here = [m for m in HALFWIDTH_RE.finditer(checked) if not in_ranges(m.start(), protected)]
            hits_here += [m for m in PAREN_RE.finditer(checked) if not in_ranges(m.start(), protected)]
            hits_here.sort(key=lambda m: m.start())
            if not hits_here:
                continue
            for m in hits_here:
                start = max(0, m.start() - 8)
                end = min(len(checked), m.end() + 8)
                snippet = checked[start:end].replace("\n", "")
                file_hits.append(f"  行{i}: ...{snippet}...")
                total += 1
            if fix:
                new_lines[i - 1] = fix_line(line)
        if file_hits:
            print(f"\n{fname} ({len(file_hits)} 处)")
            for hit in file_hits:
                print(hit)
            if fix:
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                files_changed += 1
    verb = "已改" if fix else "疑似"
    print(f"\n共 {total} 处{verb}半角标点" + (f",涉及 {files_changed} 个文件。" if fix else "。"))


if __name__ == "__main__":
    main()
