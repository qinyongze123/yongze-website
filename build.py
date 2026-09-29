"""
Builds the static site from content/*.md into public/.

How to add an article (this is the format you'll use later):

    title: 标题
    topic: 主题名字(比如 "项目")
    group: 主题所属的分组(比如 "技术相关" 或 "个人生活",侧边栏用来把主题分两组显示)
    date: 2026-03-15
    location: 北京
    summary: 列表页显示的一句话简介,不超过57字左右(参照"给一个项目设计打印了
        一个连接件,借这个机会体验了一下拓竹X1 Carbon这台消费级3D打印机,顺带
        记录一点感想。"这句的长度定的上限,再长会在卡片里显得太挤)
    cover: 相对于"个人网页素材/"的图片路径,比如 项目A/cover.jpg
    cover_fit: 可选。默认是 cover(裁满整个缩略图框,居中裁剪,适合大多数照片)。
        值为 top 时,裁满缩略图框但只从底边裁剪、顶边不裁(图片主体偏上、
        下方是多余留白/空间时用)。值为 contain 时完全不裁、整图显示、
        左右留白填充——会在缩略图上留出明显白边,尽量少用,优先考虑 top 或者
        干脆换一张长宽比更接近 16:10 的图做封面。
    show_cover_in_article: 可选,默认 yes,文章页标题下方会自动放一张封面大图。
        如果正文里马上又要放同一张图(比如当结构图/示意图),写 show_cover_in_article: no
        跳过文章页那次自动展示,避免紧挨着重复一遍;封面图仍然照常用于列表页卡片缩略图,
        不受这个字段影响。
    unlisted: 可选,默认不设。写 unlisted: yes 的文章不出现在侧边栏/主题列表页里
        (如果这个主题下所有文章都 unlisted,这个主题本身也不会出现在侧边栏,对应的
        主题列表页也不生成)。文章页本身照常生成,拿到直接链接还是能正常打开——
        用于想先把某篇文章从公开导航里撤下来,但保留链接自己看或者分享给个别人的场景。

    正文写在这一空行之后,普通 Markdown 语法。
    图片: ![说明文字](相对于"个人网页素材/"的路径)
    视频(自己托管,文件压缩到 25MB 以内): {{video: 相对于"个人网页素材/"的路径}}
    视频(B站嵌入,不限大小,国内访问快,推荐用于稍长/高清视频): {{bilibili: BV号 或 B站视频链接}}
    视频(B站嵌入,带图题): {{bilibili: BV号 或 B站视频链接 | 图题文字}}
    视频(B站嵌入,竖屏/手机拍的竖版视频用这个,嵌入框是窄的竖版比例,不会被压扁成
        横版、两边留黑边): {{bilibili-v: BV号 或 B站视频链接}},带图题同上加 | 图题文字
    两张图片并排放(比如两张竖图放一起,不想一张一张往下排太长): {{row: 路径1 | 路径2}}
    两张图片并排放,各带图题(按各自比例显示,不裁剪,贴着排): {{row: 路径1 :: 图题1 | 路径2 :: 图题2}}
    两张图片并排放,强制一样高(比例差很多的图片,比如不同形状的装备照片,居中显示留白): {{rowfit: 路径1 :: 图题1 | 路径2 :: 图题2}}
    两张图片并排放,强制一样高但按各自比例缩放、不居中留白(宽度各自适应,不要求
        两张图各占一半、分界线不一定在正中间): {{rowh: 路径1 :: 图题1 | 路径2 :: 图题2}}

规则:
- 每个主题都会生成列表页(哪怕只有一篇文章),侧边栏点主题先看到卡片列表。
- 每篇文章都应该有 cover 图片,不然列表页的卡片会缺图。
- date 字段:项目/经历类文章写到"结束月份"(格式 YYYY-MM,不用精确到日);观点/描述类
  文章(没有单一具体事件的)写"写作当日"(格式 YYYY-MM-DD,精确到日)。
- location 字段格式固定为"国家 · 城市",用 · 分隔,不写省份/街道这类更细的行政区划。
- {{row:}}/{{rowfit:}} 并排图片的标准横向间距是 18px(参照攀岩那篇文章定的),
  对应 static/css/style.css 里 .img-row 的 gap 值,不要单独改某一处的间距。
- 正文标点一律用全角(，；：等),半角逗号在网站字体下会显示得过窄。协议里的
  {{...}} 语法、素材路径、英文专有名词/网址不受此规则约束,不要把它们里面的符号转成全角。
- 草稿管理:每篇文章正文在"个人网页素材/"对应文件夹里存一份 `正文.md`(内容和
  content/ 里发布的版本保持一致),方便用户直接在素材文件夹里编辑草稿。用户自己
  编辑过的 `正文.md` 未经用户明确要求,不要主动改动或覆盖;只有用户说"我改了草稿,
  同步一下"这类明确指示时才依据草稿更新 content/ 里的正式文章。
- 标题字体(h1/h2/h3):中英文统一用 Noto Serif SC 一个字体,不要拆成"西文一个
  字体 + 中文一个字体"这种搭配方案,哪怕看着更有设计感也不要,统一字体的字重/
  字号天然匹配,不用额外写补偿代码(之前试过 Roboto Slab + Noto Serif SC 的
  搭配,西文比中文明显偏小、贴太近,得靠 span 包裹 + CSS 单独放大字号才能解决,
  用户比较后明确选择了不搭配、直接统一用 Noto Serif SC 这个更简单的方案)。
- 正文里的文件路径、字段名、代码标识符这类技术性字符串,用反引号包起来写成
  行内代码(比如 `~/.claude/projects`、`isMeta`),不要用中文引号或者裸写。
  对应 static/css/style.css 里的 `.article-body code` 规则,字体是单独一套等宽
  字体栈(ui-monospace/SF Mono/Consolas/...),不跟正文共用 Open Sans + Microsoft
  YaHei 那套——正文用的是比例字体,字符宽度不统一,拿来写路径/变量名对不齐、
  容易看混(比如 l/1/I);等宽字体才保证每个字符等宽,这是代码类文本的硬需求,
  不是审美选择。字号定的是 0.9em 而不是跟正文一样的 1em,因为等宽字体在同样
  字号下视觉上比比例字体显得更大更粗,行内混排时不缩一点会显得代码"鼓出来"、
  跟正文不协调,GitHub/Stack Overflow 这类技术网站的行内代码普遍也是缩到
  正文的 85%~90% 左右。

Run: python build.py
"""
import datetime
import hashlib
import os
import re
import shutil

import markdown
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(ROOT, "content")
# 本地写作时素材放在仓库外层的"个人网页素材/"草稿目录(体积大、图很多、不进 git)。
# 部署环境(比如 EdgeOne 跑 build 的时候)只有这个仓库本身,没有那个外层目录,这时
# 退回到仓库内自带的 assets_src/ ——它只装了真正被文章引用到的图(用 public/assets/
# 里已经筛过的那份拷贝过来的),体积小很多,可以放进 git 跟着仓库一起部署。
_EXTERNAL_ASSETS_SRC_DIR = os.path.join(os.path.dirname(ROOT), "个人网页素材")
_BUNDLED_ASSETS_SRC_DIR = os.path.join(ROOT, "assets_src")
ASSETS_SRC_DIR = (
    _EXTERNAL_ASSETS_SRC_DIR
    if os.path.isdir(_EXTERNAL_ASSETS_SRC_DIR)
    else _BUNDLED_ASSETS_SRC_DIR
)
PUBLIC_DIR = os.path.join(ROOT, "public")
STATIC_DIR = os.path.join(ROOT, "static")

SITE_NAME = "秦永泽的网站"  # 网站名/首页 logo 文字 - 之后想改就改这一个地方


def _asset_version(rel_path):
    """给 static/ 下的文件算一个基于内容的短哈希,拼在引用它的 <link>/<script>
    标签 URL 后面当查询参数(比如 style.css?v=a1b2c3d4)。这样每次内容真的变了,
    URL 就跟着变,浏览器会认成一个"新文件"重新下载;内容没变的话 URL 也不变,
    还是能吃到浏览器缓存的好处。不然文件名一直叫 style.css,浏览器缓存旧版本
    之后,就算服务器上早就换了新内容,访问者不主动强制刷新也看不到更新。"""
    path = os.path.join(STATIC_DIR, rel_path)
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

VIDEO_TAG_RE = re.compile(r"\{\{video:\s*(.+?)\s*\}\}")
BILIBILI_TAG_RE = re.compile(r"\{\{bilibili:\s*(.+?)\s*\}\}")
BILIBILI_V_TAG_RE = re.compile(r"\{\{bilibili-v:\s*(.+?)\s*\}\}")
BVID_RE = re.compile(r"(BV[0-9A-Za-z]+)")
ROW_TAG_RE = re.compile(r"\{\{row:\s*(.+?)\s*\}\}")
ROWFIT_TAG_RE = re.compile(r"\{\{rowfit:\s*(.+?)\s*\}\}")
ROWH_TAG_RE = re.compile(r"\{\{rowh:\s*(.+?)\s*\}\}")
IMG_TAG_RE = re.compile(r"<img[^>]+>")
IMG_SRC_RE = re.compile(r'src="([^"]+)"')
ALT_RE = re.compile(r'alt="([^"]*)"')
EXTERNAL_LINK_RE = re.compile(r'<a href="(https?://[^"]+)"')


def slugify_topic(topic):
    return topic.strip()


def copy_asset(rel_path):
    """Copies one file from 个人网页素材/<rel_path> into public/assets/<rel_path>,
    returns the public-relative path to use in HTML (assets/<rel_path>)."""
    if not rel_path:
        return None
    src = os.path.join(ASSETS_SRC_DIR, rel_path)
    dst = os.path.join(PUBLIC_DIR, "assets", rel_path)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isfile(src):
        shutil.copyfile(src, dst)
    else:
        print(f"  [警告] 素材文件不存在,跳过: {src}")
        return None
    return "assets/" + rel_path.replace(os.sep, "/")


def load_articles():
    articles = []
    for fname in sorted(os.listdir(CONTENT_DIR)):
        if not fname.endswith(".md") or fname == "首页.md":
            continue
        path = os.path.join(CONTENT_DIR, fname)
        md = markdown.Markdown(extensions=["meta", "fenced_code", "tables"])
        with open(path, encoding="utf-8") as f:
            raw = f.read()

        # {{bilibili: BV号 或链接 | 可选的图题}} -> 替换成 iframe 嵌入,可选图题当作 figcaption
        # (在 markdown 转换前处理,这样它是独立的 HTML 块,不会被套进 <p> 标签里)
        # {{bilibili-v: ...}} 语法相同,用于竖屏(手机拍的竖版)视频,嵌入框是窄的竖版比例
        # 而不是横版 16:9,不会把竖屏视频压扁/两边留黑边。
        def make_replace_bilibili(vertical):
            def replace_bilibili(m):
                parts = m.group(1).split("|", 1)
                raw_id = parts[0].strip()
                caption = parts[1].strip() if len(parts) > 1 else ""
                bvid_m = BVID_RE.search(raw_id)
                bvid = bvid_m.group(1) if bvid_m else raw_id
                src = f"https://player.bilibili.com/player.html?bvid={bvid}&page=1&high_quality=1&danmaku=0&autoplay=1&muted=1&t=0"
                cls = "video-embed video-embed-vertical" if vertical else "video-embed"
                embed = f'<div class="{cls}"><iframe class="lazy-bilibili" data-src="{src}" scrolling="no" frameborder="no" allowfullscreen="true"></iframe></div>'
                if caption:
                    return f'<figure class="img-figure">{embed}<figcaption>{caption}</figcaption></figure>'
                return embed
            return replace_bilibili

        raw = BILIBILI_TAG_RE.sub(make_replace_bilibili(vertical=False), raw)
        raw = BILIBILI_V_TAG_RE.sub(make_replace_bilibili(vertical=True), raw)

        # {{row: 路径1 | 路径2}} -> 两张图片并排放一行(比如两张竖图),按各自比例显示,不裁剪。
        # 每张图可以带图题: {{row: 路径1 :: 图题1 | 路径2 :: 图题2}}
        # {{rowfit: ...}} 语法相同,但强制两张图一样高、居中留白(适合比例差很多的图片,比如装备照片)。
        # 这里只生成普通 <img> 标签、用的还是素材相对路径,真正的素材拷贝/路径改写
        # 交给下面统一处理 <img> 的那一步,和普通 markdown 图片走同一套逻辑。
        def make_replace_row(item_class):
            def replace_row(m):
                items = [p.strip() for p in m.group(1).split("|")]
                cells = ""
                for item in items:
                    if not item:
                        continue
                    if "::" in item:
                        path, caption = item.split("::", 1)
                        cells += f'<figure class="{item_class}"><img src="{path.strip()}" alt=""><figcaption>{caption.strip()}</figcaption></figure>'
                    else:
                        cells += f'<img src="{item}" alt="">'
                return f'<div class="img-row">{cells}</div>'
            return replace_row

        raw = ROW_TAG_RE.sub(make_replace_row("img-row-item"), raw)
        raw = ROWFIT_TAG_RE.sub(make_replace_row("img-row-item-fit"), raw)

        # {{rowh: 路径1 :: 图题1 | 路径2 :: 图题2}} -> 两张图片强制等高、按各自比例缩放、
        # 不居中留白(不要求各占一半宽度)。
        # 不在编译时按某个假定的容器宽度(比如桌面正文的720px)算死一个像素高度——那样的值
        # 只对那一种屏幕宽度成立,换个屏幕(比如手机)容器变窄了,像素高度却不会跟着变,图片
        # 就会被挤得又细又高。这里改成给每张图的 flex-grow 设成它自己的宽高比,配合
        # flex-basis:0 和 img 的 width:100%/height:auto——flexbox 会按这个比例分配宽度,
        # 可以证明无论容器实际有多宽,算出来的每张图最终高度必然相等,而且是浏览器在渲染
        # 那一刻实时算的,不管屏幕多宽都自动正确,不需要为不同屏幕单独适配。
        def replace_rowh(m):
            items = [p.strip() for p in m.group(1).split("|")]
            paths, captions = [], []
            for item in items:
                if not item:
                    continue
                if "::" in item:
                    path, caption = item.split("::", 1)
                    paths.append(path.strip())
                    captions.append(caption.strip())
                else:
                    paths.append(item)
                    captions.append(None)
            aspects = []
            for p in paths:
                try:
                    with Image.open(os.path.join(ASSETS_SRC_DIR, p)) as im:
                        aspects.append(im.width / im.height)
                except OSError:
                    aspects.append(1.0)
            cells = ""
            for path, caption, aspect in zip(paths, captions, aspects):
                grow = f' style="flex-grow:{aspect:.4f};flex-shrink:{aspect:.4f}"'
                if caption is not None:
                    cells += f'<figure class="img-row-item-h"{grow}><img src="{path}" alt=""><figcaption>{caption}</figcaption></figure>'
                else:
                    cells += f'<img class="img-row-item-h-bare" src="{path}" alt=""{grow}>'
            return f'<div class="img-row">{cells}</div>'

        raw = ROWH_TAG_RE.sub(replace_rowh, raw)

        html_body = md.convert(raw)
        meta = {k: " ".join(v) for k, v in md.Meta.items()} if md.Meta else {}

        # video placeholders -> real <video> tags, copying the asset
        def replace_video(m):
            rel = m.group(1)
            pub_path = copy_asset(rel)
            if not pub_path:
                return ""
            return f'<video controls src="{pub_path}"></video>'

        html_body = VIDEO_TAG_RE.sub(replace_video, html_body)

        # rewrite every <img src="..."> from a 素材-relative path to the copied public path,
        # keeping the rest of the tag (alt text etc.) intact; if it has alt text, wrap it in
        # a <figure> with a visible <figcaption> underneath (alt text alone isn't shown on screen)
        def replace_img_tag(m):
            tag = m.group(0)
            src_m = IMG_SRC_RE.search(tag)
            if not src_m:
                return tag
            rel = src_m.group(1)
            pub_path = copy_asset(rel)
            new_tag = tag[:src_m.start()] + f'src="{pub_path or rel}"' + tag[src_m.end():]
            alt_m = ALT_RE.search(new_tag)
            alt_text = alt_m.group(1) if alt_m else ""
            if alt_text:
                return f'<figure class="img-figure">{new_tag}<figcaption>{alt_text}</figcaption></figure>'
            return new_tag

        html_body = IMG_TAG_RE.sub(replace_img_tag, html_body)

        # external links (http/https, i.e. not our own relative paths) open in a new tab
        # instead of navigating away from the article
        html_body = EXTERNAL_LINK_RE.sub(
            r'<a href="\1" target="_blank" rel="noopener noreferrer"', html_body
        )

        cover_pub = copy_asset(meta.get("cover"))

        slug = os.path.splitext(fname)[0]
        articles.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "topic": meta.get("topic", "未分类"),
            "group": meta.get("group", "其他"),
            "date": meta.get("date", ""),
            "location": meta.get("location", ""),
            "summary": meta.get("summary", ""),
            "cover": cover_pub,
            "cover_fit": meta.get("cover_fit", ""),
            "show_cover_in_article": meta.get("show_cover_in_article", "yes") != "no",
            "unlisted": meta.get("unlisted", "") == "yes",
            "body_html": html_body,
        })
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def group_by_topic(articles):
    topics = {}
    for a in articles:
        topics.setdefault(a["topic"], []).append(a)
    return topics


GROUP_ORDER = ["技术相关", "个人生活"]  # 侧边栏分组的固定显示顺序,不在列表里的分组按出现顺序排在后面
TOPIC_ORDER = {  # 每个分组内,主题的固定显示顺序;某个主题不在列表里就按首次出现顺序排在后面
    "技术相关": ["机器人", "AI", "创客", "游戏"],
    "个人生活": ["攀岩", "徒步", "玩游戏"],
}


def group_by_group_and_topic(articles):
    """{ group_name: { topic_name: [articles...] } },分组按 GROUP_ORDER 排序,
    每个分组内的主题按 TOPIC_ORDER[分组] 排序(不在列表里的按首次出现顺序排在后面)。"""
    groups = {}
    for a in articles:
        groups.setdefault(a["group"], {}).setdefault(a["topic"], []).append(a)

    def group_sort_key(group_name):
        return GROUP_ORDER.index(group_name) if group_name in GROUP_ORDER else len(GROUP_ORDER)

    sorted_groups = {}
    for group_name, topics in sorted(groups.items(), key=lambda item: group_sort_key(item[0])):
        order = TOPIC_ORDER.get(group_name, [])

        def topic_sort_key(topic_name):
            return order.index(topic_name) if topic_name in order else len(order)

        sorted_groups[group_name] = dict(sorted(topics.items(), key=lambda item: topic_sort_key(item[0])))
    return sorted_groups


def topic_href(prefix, topic, arts):
    return f"{prefix}topics/{topic}.html"


def sidebar_html(prefix, groups, active):
    home_cls = " active" if active == "home" else ""
    group_blocks = ""
    for group_name, topics in groups.items():
        links = ""
        for topic, arts in topics.items():
            active_cls = " active" if topic == active else ""
            links += f'''
              <a class="sidebar-link{active_cls}" href="{topic_href(prefix, topic, arts)}">
                <span>{topic}</span><span class="sidebar-count">{len(arts)}</span>
              </a>'''
        group_blocks += f'''
          <div class="sidebar-group">
            <div class="sidebar-group-label">{group_name}</div>
            <nav class="sidebar-nav">{links}
            </nav>
          </div>'''
    return f'''
      <aside class="sidebar">
        <a class="sidebar-link sidebar-home{home_cls}" href="{prefix}index.html">首页</a>{group_blocks}
      </aside>'''


def page_shell(title, depth, body_html, groups, active=None):
    prefix = "../" * depth
    sidebar = sidebar_html(prefix, groups, active)
    footer = f'''
      <footer id="site-footer">
        <div class="wrap">
          qinyongze2002@gmail.com · 最后更新于{datetime.date.today().year}年{datetime.date.today().month}月
        </div>
      </footer>'''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="stylesheet" href="{prefix}static/css/style.css?v={_asset_version('css/style.css')}">
</head>
<body>
      <div class="layout">
        {sidebar}
        <main class="content">
        {body_html}
        </main>
      </div>
{footer}
<script src="{prefix}static/js/lazy-video.js?v={_asset_version('js/lazy-video.js')}" defer></script>
</body>
</html>'''


def load_home():
    """读取 content/首页.md,frontmatter 是 title/photo/basic(出生年·籍贯这种
    一行简介)/intro(自我介绍,放在头部区域)/email/phone,正文部分普通 Markdown
    语法,小节之间用 --- 分隔线,
    "经历"/"技能"/"语言" 这几节内部排版比较特殊,直接在正文里写的是原始 HTML
    (python-markdown 默认会原样透传)。"""
    md = markdown.Markdown(extensions=["meta"])
    with open(os.path.join(CONTENT_DIR, "首页.md"), encoding="utf-8") as f:
        raw = f.read()
    html_body = md.convert(raw)
    meta = {k: " ".join(v) for k, v in md.Meta.items()} if md.Meta else {}
    return {
        "title": meta.get("title", ""),
        "photo": meta.get("photo", ""),
        "basic": meta.get("basic", ""),
        "intro": meta.get("intro", ""),
        "email": meta.get("email", ""),
        "phone": meta.get("phone", ""),
        "body_html": html_body,
    }


def render_home(home, groups):
    photo_pub = copy_asset(home["photo"]) if home["photo"] else None
    photo_html = f'<img class="avatar-square" src="{photo_pub}" alt="{home["title"]}">' if photo_pub else ""
    contact_rows = (
        ("fa-envelope", home["email"]),
        ("fa-phone", home["phone"]),
    )
    contact_items = "".join(
        f'<li><i class="fa-solid {icon}"></i><span>{value}</span></li>'
        for icon, value in contact_rows if value
    )
    body = f'''
    <section class="profile">
      <div class="profile-header">
        {photo_html}
        <div class="profile-header-text">
          <h1>{home["title"]}</h1>
          <p class="basic-line">{home["basic"]}</p>
          <p class="intro-text">{home["intro"]}</p>
          <ul class="contact-list">
            {contact_items}
          </ul>
        </div>
      </div>
      {home["body_html"]}
    </section>'''
    return page_shell(SITE_NAME, 0, body, groups, active="home")


def render_topic(topic, arts, groups):
    cards = ""
    for a in arts:
        if a["cover_fit"] == "contain":
            thumb_style = ' style="object-fit:contain;background:#fff"'
        elif a["cover_fit"] == "top":
            thumb_style = ' style="object-position:top"'
        else:
            thumb_style = ""
        thumb_img = f'<img src="../{a["cover"]}" alt=""{thumb_style}>' if a["cover"] else ""
        thumb = f'<div class="thumb">{thumb_img}</div>'
        cards += f'''
        <a class="card" href="../articles/{a["slug"]}.html">
          {thumb}
          <div class="body">
            <h3>{a["title"]}</h3>
            <div class="meta"><span class="meta-date">{a["date"]}</span><span class="meta-location">{a["location"]}</span></div>
            <div class="summary">{a["summary"]}</div>
          </div>
        </a>'''

    body = f'''
    <div class="page-head">
      <h1>{topic}</h1>
    </div>
    <div class="grid">{cards}
    </div>'''
    return page_shell(f"{topic} · {SITE_NAME}", 1, body, groups, active=topic)


def render_article(a, groups):
    cover_html = f'<img src="../{a["cover"]}" alt="">' if a["cover"] and a["show_cover_in_article"] else ""
    body_html = re.sub(r'src="assets/', 'src="../assets/', a["body_html"])
    body = f'''
    <div class="article-head">
      <div class="article-topic-tag">{a["topic"]}</div>
      <h1>{a["title"]}</h1>
    </div>
    <div class="article-body">
      {cover_html}
      {body_html}
    </div>'''
    return page_shell(f"{a['title']} · {SITE_NAME}", 1, body, groups, active=a["topic"])


def main():
    if os.path.isdir(PUBLIC_DIR):
        try:
            shutil.rmtree(PUBLIC_DIR)
        except PermissionError:
            # Windows 下如果某个终端的当前工作目录还停留在 public/ 里(比如之前跑过
            # `cd public && python -m http.server` 忘了退出),这个目录句柄本身会被占用,
            # 导致目录连同它自己都删不掉(即便内容已经清空)。这种情况下退化成"清空内容,
            # 保留目录",不影响构建结果。
            for entry in os.listdir(PUBLIC_DIR):
                entry_path = os.path.join(PUBLIC_DIR, entry)
                if os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
                else:
                    os.remove(entry_path)
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(os.path.join(PUBLIC_DIR, "topics"))
    os.makedirs(os.path.join(PUBLIC_DIR, "articles"))

    print("读取文章...")
    articles = load_articles()
    # unlisted 的文章不出现在侧边栏/主题列表页里(也就没有对应的主题列表页),
    # 但文章页本身照常生成,直接用链接访问不受影响
    listed_articles = [a for a in articles if not a["unlisted"]]
    topics = group_by_topic(listed_articles)
    groups = group_by_group_and_topic(listed_articles)
    print(f"共 {len(articles)} 篇文章,{len(topics)} 个主题,{len(groups)} 个分组: {', '.join(groups)}")

    home = load_home()
    with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_home(home, groups))

    for topic, arts in topics.items():
        with open(os.path.join(PUBLIC_DIR, "topics", f"{topic}.html"), "w", encoding="utf-8") as f:
            f.write(render_topic(topic, arts, groups))

    for a in articles:
        with open(os.path.join(PUBLIC_DIR, "articles", f"{a['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(render_article(a, groups))

    shutil.copytree(STATIC_DIR, os.path.join(PUBLIC_DIR, "static"))

    print(f"生成完成 -> {PUBLIC_DIR}")


if __name__ == "__main__":
    main()
