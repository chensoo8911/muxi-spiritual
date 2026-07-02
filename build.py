#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""木喜身心靈 · 靜態網站產生器（輸出純 HTML，可直接上 GitHub Pages）"""
import os, re, html, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
BOOK_SRC = os.path.join(ROOT, "..", "電子書", "01_海奧華預言")

# ============================================================ 共用樣板
def head(title, depth, desc=""):
    a = "../" * depth
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="stylesheet" href="{a}assets/style.css">
</head>
<body>
{nav(depth)}
"""

def nav(depth):
    a = "../" * depth
    return f"""<header class="nav">
  <a class="brand" href="{a}index.html">木喜<small>身心靈</small></a>
  <button class="nav-toggle" aria-label="開啟選單" aria-expanded="false"><span></span><span></span><span></span></button>
  <nav class="links">
    <a href="{a}書籍/index.html">推薦書單</a>
    <a href="{a}影片/index.html">靈性影片</a>
    <a href="{a}木喜專區/index.html">木喜專區</a>
  </nav>
</header>"""

_CRUMB_BOOKNAME = {"耶穌-我的自傳": "耶穌：我的自傳"}
_CRUMB_ZONE = {"書籍": "推薦書單", "影片": "靈性影片", "木喜專區": "木喜專區"}
_CRUMB_WIDE = {"書籍/index.html", "影片/index.html"}  # 用 .wrap(1080) 寬容器的頁面，麵包屑同寬對齊卡片
def crumb(path, title):
    """依頁面路徑產生麵包屑：桌面完整路徑＋手機上一頁按鈕（回上一層）。首頁不加。"""
    parts = path.split("/")
    cur = title.split(" · ")[0].strip()
    up = "../" * (len(parts) - 1)
    if len(parts) == 1:
        return ""
    if len(parts) == 2 and parts[1] == "index.html":          # 區首頁
        zone = _CRUMB_ZONE.get(parts[0], parts[0])
        items = [("首頁", up + "index.html"), (zone, None)]; back = up + "index.html"
    elif len(parts) == 2:                                       # 書籍/slug.html 導讀頁
        items = [("首頁", up + "index.html"), ("推薦書單", "index.html"), (cur, None)]; back = "index.html"
    elif len(parts) == 3 and parts[2] == "index.html":         # 書目錄
        items = [("首頁", up + "index.html"), ("推薦書單", "../index.html"), (cur, None)]; back = "../index.html"
    elif len(parts) == 3:                                       # 章節頁
        bname = _CRUMB_BOOKNAME.get(parts[1], parts[1])
        items = [("首頁", up + "index.html"), ("推薦書單", "../index.html"),
                 (bname, "index.html"), (cur, None)]; back = "index.html"
    else:
        return ""
    lis = "".join(f'<li><a href="{h}">{l}</a></li>' if h else f'<li aria-current="page">{l}</li>'
                  for l, h in items)
    cls = "crumb crumb-wide" if path in _CRUMB_WIDE else "crumb"
    return (f'<nav class="{cls}" aria-label="breadcrumb"><a class="crumb-back" href="{back}">‹ 上一頁</a>'
            f'<ol class="crumb-full">{lis}</ol></nav>\n')

def foot(depth):
    return """<footer class="foot">
  <div class="f-title">木喜身心靈</div>
  <p>整理自木喜與學生的多年分享<br><span class="foot-disclaimer">免責聲明：各書籍與影片版權歸原作者所有，本站為非營利分享，僅供有緣人自我成長之用；<br>如有侵權請來信告知，將即刻移除。</span></p>
</footer>
<script src="%sassets/app.js"></script>
</body></html>""" % ("../" * depth)

def page(path, title, depth, body, desc=""):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    parts = path.split("/")
    # 章節頁的麵包屑放進 reader-top 工具列（跟著 sticky 顯示），外層不再注入
    is_chapter = len(parts) == 3 and parts[2] != "index.html"
    cr = "" if is_chapter else crumb(path, title)
    with open(full, "w", encoding="utf-8") as f:
        f.write(head(title, depth, desc) + cr + body + foot(depth))
    print("✓", path)

def lite_yt(vid, title, desc):
    return f"""<div class="vcard">
  <div class="yt" data-id="{vid}">
    <img loading="lazy" src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="{html.escape(title)}">
    <button class="play" aria-label="播放">▶</button>
  </div>
  <div class="vmeta"><h3>{html.escape(title)}</h3><p>{html.escape(desc)}</p></div>
</div>"""

# ============================================================ 首頁
def build_home():
    body = f"""<section class="hero wrap">
  <div class="eyebrow">A Spiritual Archive</div>
  <h1>木喜身心靈</h1>
  <p>這裡彙整木喜多年來推薦、朗讀與口傳的身心靈資源與教導。</p>
  <span class="seal">聆聽內在那微細的低語</span>
</section>

<section class="wrap">
  <div class="zones">
    <a class="zone" href="書籍/index.html">
      <div><div class="num">I.</div><h2>推薦書單</h2>
      <p>海奧華預言、阿納絲塔夏、耶穌自傳⋯⋯ 可閱讀全文，並一鍵朗讀。</p></div>
      <div class="go">進入書房</div>
    </a>
    <a class="zone" href="影片/index.html">
      <div><div class="num">II.</div><h2>靈性 ／ 外星人影片</h2>
      <p>巴夏、阿納絲塔夏、靈界見證、心咒⋯⋯ 分類整理，輕觸即看。</p></div>
      <div class="go">觀看影片</div>
    </a>
    <a class="zone" href="木喜專區/index.html">
      <div><div class="num">III.</div><h2>木喜專區</h2>
      <p>十一項核心教導與十句金句，木喜身心靈理念的精華統整。</p></div>
      <div class="go">閱讀教導</div>
    </a>
  </div>
</section>"""
    page("index.html", "木喜身心靈", 0, body,
         "吳木喜推薦與朗讀的身心靈書籍、影片與核心教導彙整。")

# ============================================================ 書籍區
BOOKS = [
  {"slug":"海奧華預言", "spine":"", "author":"米歇・戴斯瑪克特",
   "tags":[("full","全文可讀"),("audio","有聲書")],
   "blurb":"第九級星球的九日旅程。談人類起源、靈魂演化、地球文明的真相與未來。",
   "reader":True, "src":"01_海奧華預言", "subtitle":"第九級星球的九日旅程，奇幻不思議的真實見聞。",
   "audio_embeds":[("fUr4Nv7tryk","有聲書 · 上","YouTube 有聲書朗讀（上集）"),
                   ("C87YV0iCVK4","有聲書 · 下","YouTube 有聲書朗讀（下集）")]},
  {"slug":"阿納絲塔夏", "spine":"green", "author":"弗拉狄米爾・米格烈",
   "tags":[("audio","有聲書"),("link","導讀")],
   "blurb":"鳴響雪松系列第一冊。西伯利亞森林的隱居女子，談人與自然合一、回歸土地。",
   "audio_playlist":"PLJe-eUPHwIHOv-rOoEUfreaH7JCa9owlg", "audio_id":"DN2EIMBMc3s",
   "why":"階梯書單的起點。「回歸自然、相信直覺」的精神，與木喜搬到鄉下務農的實踐高度呼應。",
   "links":[("鳴響雪松中文官網","https://www.cedarray.com/"),("讀墨電子書","https://readmoo.com/book/210086601000101")]},
  {"slug":"耶穌-我的自傳", "name":"耶穌：我的自傳", "spine":"gold", "author":"蒂娜・司帕爾汀 傳訊",
   "tags":[("full","全文可讀"),("audio","木喜朗讀")],
   "blurb":"以第一人稱講述一個平易近人、非教會版本的耶穌。木喜親自朗讀成有聲書。",
   "reader":True, "src":"04_耶穌-我的自傳", "subtitle":"以第一人稱講述一個平易近人、非教會版本的耶穌。",
   "audio_playlist":"PLzGMJVlc_bxUqbgiCLHBegQ1Ei69KzYFj",
   "audio_id":"L-YjOqq1zgY",
   "episodes":[("001 譯者序","L-YjOqq1zgY"),("002 作者序","TxBgNSgELnU"),("003 導言","OOjRSN-p2xQ"),
               ("004 詞彙解析","LrSW0JL8Wbk"),("005 第一章 故事一開始","5Z8nYQHPWhk"),
               ("006 第二章 旅行","rSQ2zf6BInI"),("007 第三章 沙漠裡的殿堂","maaiGupb1Tw"),
               ("008 第四章 印度","H0vzBifiBYw"),("009 第五章 返鄉","RcrkFvCOBMw")],
   "why":"木喜「上主即合一、耶穌是覺醒者、天國在心裡」的觀點主要源自本書。",
   "links":[("繁中 Kindle 版","https://www.amazon.com/dp/B081HXB75Y")]},
  {"slug":"告別娑婆", "spine":"", "author":"蓋瑞・雷納",
   "tags":[("full","全文可讀"),("link","導讀")],
   "blurb":"進入《奇蹟課程》前最受歡迎的導讀書。十七場與揚升大師的對話，談寬恕與幻相。",
   "reader":True, "src":"02_告別娑婆", "subtitle":"十七場與揚升大師的對話，談寬恕、幻相與真寬恕。",
   "local_audio":{"00_序":"告別娑婆_00序.mp3", "01_1_阿頓與白沙的出現":"告別娑婆_01第一章.mp3"},
   "why":"階梯書單中「奇蹟課程」的前一站，木喜的寬恕教導大量取自本書。",
   "links":[("英文全文 Internet Archive","https://archive.org/details/disappearanceof00gary")]},
  {"slug":"奇蹟課程", "spine":"gold", "author":"海倫・舒曼 筆錄",
   "tags":[("link","英文免費")],
   "blurb":"一套自學的心靈訓練課程，專教「寬恕」。練習手冊 365 課，一天一課。",
   "why":"階梯書單的終點與核心。木喜常引用練習手冊原文，強調用寬恕化解一切問題。",
   "links":[("英文公共版全文 acim.org","https://acim.org/acim/en"),("中文官網（若水譯）","https://www.acimtaiwan.info/")]},
  {"slug":"巴夏文集", "spine":"green", "author":"巴夏（Darryl Anka 傳訊）",
   "tags":[("link","免費全文")],
   "blurb":"來自愛莎莎尼文明的傳訊，談跟隨最高的興奮、頻率與顯化、死亡是擴展。",
   "why":"木喜「天音即興奮、死亡是頻率轉換」等教導，直接呼應巴夏訊息。",
   "links":[("巴夏中文文集（全文）","https://zenkarsha.github.io/bashar/archive.html"),("光中心文章","https://lightcenter.tw/?p=7112")]},
]

def book_name(b): return b.get("name", b["slug"])

def build_book_list():
    cards = []
    for b in BOOKS:
        href = f"{b['slug']}/index.html" if b.get("reader") else f"{b['slug']}.html"
        tags = "".join(f'<span class="tag {k}">{v}</span> ' for k,v in b["tags"])
        cls = ("book " + b["spine"]).strip()
        cards.append(f"""<a class="{cls}" href="{href}">
  <div class="spine"></div>
  <div><h3>{html.escape(book_name(b))}</h3>
  <div class="meta">{html.escape(b['author'])}</div>
  <p>{html.escape(b['blurb'])}</p>{tags}</div>
</a>""")
    body = f"""<div class="wrap">
<div class="section-head"><div class="eyebrow">Section I</div>
<h1>推薦書單</h1>
<p>推薦學習地圖：阿納絲塔夏 → 耶穌：我的自傳 → 告別娑婆 → 奇蹟課程</p>
<hr class="divider"></div>
<div class="books">{''.join(cards)}</div>
</div>"""
    page("書籍/index.html", "推薦書單 · 木喜身心靈", 1, body)

# ---------- 通用全文閱讀器（任何 reader 書都能用）----------
ELECTRONIC = os.path.join(ROOT, "..", "電子書")

def read_chapters(src_folder):
    files = sorted(glob.glob(os.path.join(ELECTRONIC, src_folder, "[0-9]*.md")))
    chs = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            txt = fh.read()
        title = txt.split("\n",1)[0].lstrip("# ").strip()
        paras = [p.strip() for p in txt.split("\n\n")[1:] if p.strip()]
        slug = os.path.splitext(os.path.basename(f))[0]
        chs.append({"slug":slug, "title":title, "paras":paras})
    return chs

_LEAD = set('”’」』。！？，、；）)》')
def merge_paras(paras):
    """把以收引號或句末標點開頭的段落併回前一段（修對話被 OCR 拆行的不自然段行）。"""
    out = []
    for p in paras:
        if out and p and p[0] in _LEAD:
            out[-1] = out[-1] + p
        else:
            out.append(p)
    return out

def build_reader(b):
    """產生某書的目錄頁＋各章閱讀頁。若無章節檔，回傳 False（改走導讀頁）。"""
    chs = read_chapters(b["src"])
    if not chs:
        return False
    name = book_name(b); slug = b["slug"]

    # 有聲書嵌入（海奧華=上下集、耶穌=木喜朗讀九集）
    aud = ""
    if b.get("audio_embeds"):
        cards = "".join(lite_yt(i,t,d) for i,t,d in b["audio_embeds"])
        aud = f'<h2 style="font-size:1.3rem;margin:2.5rem 0 1rem">有聲書</h2><div class="vid-grid" style="grid-template-columns:1fr 1fr">{cards}</div>'
    elif b.get("episodes"):
        cards = "".join(lite_yt(vid,t,"木喜朗讀") for t,vid in b["episodes"])
        aud = f'<h2 style="font-size:1.3rem;margin:1.5rem 0 1rem">木喜朗讀有聲書</h2><div class="vid-grid">{cards}</div>'

    # 目錄頁
    toc = []
    for i, c in enumerate(chs):
        no = "0" if i==0 else str(i)
        toc.append(f'<li><a href="{c["slug"]}.html"><span class="n">{no}</span><span>{html.escape(c["title"])}</span></a></li>')
    body = f"""<div class="read">
<div class="section-head"><div class="eyebrow">{html.escape(b['author'])}</div>
<h1>{html.escape(name)}</h1>
<p>{html.escape(b.get('subtitle', b['blurb']))}</p><hr class="divider"></div>
<ul class="toc">{''.join(toc)}</ul>
{aud}
</div>"""
    page(f"書籍/{slug}/index.html", f"{name} · 木喜身心靈", 2, body)

    # 各章閱讀頁
    for i, c in enumerate(chs):
        prev_a = f'<a href="{chs[i-1]["slug"]}.html" class="prev"><span class="dir">← 上一章</span><span class="ttl">{html.escape(chs[i-1]["title"])}</span></a>' if i>0 else '<span class="prev disabled"><span class="dir">← 上一章</span><span class="ttl">已是開頭</span></span>'
        nxt_a  = f'<a href="{chs[i+1]["slug"]}.html" class="next"><span class="dir">下一章 →</span><span class="ttl">{html.escape(chs[i+1]["title"])}</span></a>' if i<len(chs)-1 else '<span class="next disabled"><span class="dir">下一章 →</span><span class="ttl">已是結尾</span></span>'
        paras = "\n".join(f"<p>{html.escape(p)}</p>" for p in merge_paras(c["paras"]))
        no_label = "序" if i==0 else f"第 {i} 章"
        # 本章若有 AI 朗讀音檔，放真人聲克隆播放器
        la = b.get("local_audio", {}).get(c["slug"])
        local_player = ""
        if la:
            local_player = f"""<div class="local-audio">
      <div class="la-label">🎧 AI 有聲書（試聽版）</div>
      <audio controls preload="none" src="../../audio/{slug}/{la}"></audio>
    </div>"""
        body = f"""<div class="reader-top">
  <div class="read reader-bar">
    {crumb(f"書籍/{slug}/{c['slug']}.html", f"{html.escape(c['title'])} · {name}")}
    {local_player}
    <div class="player">
      <button class="btn-audio" id="btn-read"><span class="ico"></span><span class="txt">▶ 朗讀本章</span></button>
      <button class="btn-ghost" id="btn-stop" style="display:none">停止</button>
    </div>
  </div>
</div>
<div class="read">
<article class="reading">
  <span class="chap-no">{no_label}</span>
  <h1>{html.escape(c["title"])}</h1>
  {paras}
</article>
<nav class="pager">{prev_a}{nxt_a}</nav>
</div>"""
        page(f"書籍/{slug}/{c['slug']}.html", f"{c['title']} · {name}", 2, body)
    return True

# ---------- 其他書 導讀頁 ----------
def build_book_intro(b):
    aud = ""
    if b.get("episodes"):
        cards = "".join(lite_yt(vid, t, "木喜朗讀") for t,vid in b["episodes"])
        aud = f'<h2 style="font-size:1.4rem;margin:2.5rem 0 1rem">木喜朗讀有聲書</h2><div class="vid-grid">{cards}</div>'
    elif b.get("audio_id"):
        aud = f'<h2 style="font-size:1.4rem;margin:2.5rem 0 1rem">有聲書</h2><div class="vid-grid" style="grid-template-columns:1fr 1fr">{lite_yt(b["audio_id"], book_name(b)+"．有聲書","YouTube 有聲書朗讀")}</div>'
    links = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{html.escape(t)} ↗</a></li>' for t,u in b.get("links",[]))
    body = f"""<div class="read">
<div class="section-head"><div class="eyebrow">{html.escape(b['author'])}</div>
<h1>{html.escape(book_name(b))}</h1><hr class="divider"></div>
<div class="intro-block">
<p>{html.escape(b['blurb'])}</p>
<p><strong>木喜為何推薦：</strong>{html.escape(b.get('why',''))}</p>
</div>
<h2 style="font-size:1.4rem;margin:2.5rem 0 1rem">取得方式</h2>
<ul class="toc">{links}</ul>
{aud}
<p style="margin:2rem 0 4rem"><a href="index.html">← 回書房</a></p>
</div>"""
    page(f"書籍/{b['slug']}.html", f"{book_name(b)} · 木喜身心靈", 1, body)

# ============================================================ 影片區
VIDEO_CATS = [
 ("巴夏與外星訊息","來自巴夏與外星文明的傳訊，談接觸、頻率與興奮。",[
   ("7NVZn-quKDw","2027 外星文明公開接觸","巴夏傳訊：2027 年公開接觸拍板，史匹柏將先以電影鋪陳。"),
   ("OWUVSSrAPD8","你最值錢的資產是「興奮感」","星際導師巴夏：跟隨興奮，就是與高我對齊的捷徑。"),
   ("Z9qGy-VkqoA","金星人的六個禁忌預言","1991 年自稱來自金星者的預言，35 年後四個正在成真。"),
   ("3z50AaPKT1E","巴夏：頻率切換技術","不想留在舊世界？學會把意識頻率切換到你要的實相。"),
 ]),
 ("阿納絲塔夏","認識西伯利亞森林隱士阿納絲塔夏與她的智慧。",[
   ("4yVCDYi5OzU","擁有療癒超能力的森林隱士","巴夏稱她為「真正的人類」，介紹其療癒身心的能力。"),
   ("nqKWjGHFOIs","《阿納絲塔夏》書中十大驚奇","整理書中最震撼的十個段落，快速認識這本書。"),
 ]),
 ("顯化・冥想・能量","關於顯化豐盛、冥想入門與能量流動的實用分享。",[
   ("08WrG9MoUOQ","如何與宇宙交換能量","五個面向：如何最短時間顯化豐盛、分辨自己在高維或低維。"),
   ("W4jAtGGi3-U","冥想初學者的十個問題","超級旅行者解答冥想常見疑問，片尾附冥想音樂與白光保護罩。"),
   ("422fTfWeUx4","沒動力不是懶，是靈魂拒絕低頻","揭密覺醒後「無所事事」的真正原因。"),
   ("dvkkodwCGhc","業力管理：助人即成就自己","睡前聽一本書《業力管理》，談因果與付出的法則。"),
 ]),
 ("靈界・瀕死見證","真實的瀕死與靈界紀錄，重新看待生命與死亡。",[
   ("9-UhsF00KzU","無神論者死而復生後的表白","一段真實瀕死經歷，改變了當事人對生命的看法。"),
   ("xq37c-RbX6o","史上最完整靈界紀錄","靈魂揭露：「不留遺憾的人生」原來長這樣。"),
   ("sXrUojsWhLM","你的人生劇本其實是神級逆轉","覺得劇本很爛？或許正在完成最震撼的安排。"),
   ("MDxSGuamtKQ","離世後神為他重塑身體","血型、DNA 全變，至今醫學無解的神蹟。"),
 ]),
 ("預言・覺醒","關於人類巨變與集體覺醒的訊息。",[
   ("8OGSx2xotQk","俄羅斯的未來與人類巨變","神現身預告，人類歷經輪迴已到關頭；每天發正念改變世界。"),
   ("lQTxbAVT3e0","靈性分享","木喜分享的一段靈性影片。"),
 ]),
 ("佛經・心咒","以淺白方式親近佛法與心咒。",[
   ("Qi8o7h2xvXw","心經：空，不是什麼都沒有","用淺白方式講《心經》的「空」與「到彼岸」。"),
   ("M42a-Qhv5-c","藥師佛心咒（中文＋梵語）","奇妙心國度的藥師佛心咒翻唱，可作背景冥想。"),
 ]),
]

def build_videos():
    cats = []
    for name, desc, vids in VIDEO_CATS:
        grid = "".join(lite_yt(v,t,d) for v,t,d in vids)
        cats.append(f"""<section class="vid-cat">
  <h2><span class="dot"></span>{html.escape(name)}</h2>
  <p class="cdesc">{html.escape(desc)}</p>
  <div class="vid-grid">{grid}</div>
</section>""")
    body = f"""<div class="wrap">
<div class="section-head"><div class="eyebrow">Section II</div>
<h1>靈性 ／ 外星人影片</h1>
<p>木喜分享的靈性影片，依主題分類。為節省流量，點擊縮圖才開始播放。</p>
<hr class="divider"></div>
{''.join(cats)}
<div style="height:4rem"></div>
</div>"""
    page("影片/index.html", "靈性 ／ 外星人影片 · 木喜身心靈", 1, body)

# ============================================================ 木喜專區
TEACHINGS = [
 ("天音／直覺至上","「<strong>天音</strong>」是內在那微細的低語、直覺、第六感、童心，<br>來自內心的衝動（興奮感），是行動的第一順位。<span class='gap'></span><strong>覺察</strong> ≠ 想法、分析、恐懼、懷疑，而是從內在來臨的「<strong>靜默</strong>」和「<strong>平安</strong>」的召喚。<span class='gap'></span>大腦思維只用來「<strong>完成高我給的感覺</strong>」，純靠大腦想來想去只會困住自己。"),
 ("小我 vs. 高我／真我","<strong>小我</strong>：充滿分析、比較、批判、患得患失、想掌控；<br><strong>高我</strong>：<strong>靈魂想唱歌</strong>、照感覺走、不費力。<span class='gap'></span>情緒是指南針，走在對的路上會平安喜樂，偏離軌道時情緒會用不舒服提醒你。"),
 ("做自己、放掉掌控","木喜鼓勵，從日常小事（如洗澡、吃飯、散步、出門不規劃）開始練習相信直覺、放掉控制；<br>越不掌控，越能與「<strong>源頭</strong>」連結，奇蹟才出得來。<span class='gap'></span>他批評教育與社會總是「<strong>教人緊緊兮兮</strong>」、「<strong>毀壞天音</strong>」。"),
 ("顯化法則","心想事成關鍵：靜下來把希望的情景在腦中預演，留意那種完全滿足、安寧的感覺，輕柔握住、毫無擔心地讓它發生。<br>「<strong>只要你真心想做一件事，宇宙會為你顯化出配備</strong>」 內在的感覺就是顯化方針。"),
 ("一體（合一）與分裂","人的痛苦來自「<strong>分裂感</strong>」，覺得與他人是分離的個體、為生存互相算計；<br>其實，我們是需要互助互愛的<strong>一個整體</strong>。<span class='gap'></span>一體帶來歸屬感與安全感，所有靈性的共同目標都是「<strong>由分裂走向合一</strong>」。"),
 ("階梯式書單與課程","<strong style='color:var(--ink)'>學習地圖：阿納絲塔夏 → 耶穌：我的自傳 → 告別娑婆 → 奇蹟課程</strong><br>教導「<strong>上主是你可信賴的力量，不要只靠自己</strong>」。<br><span style='font-size:.88em;color:var(--ink-faint)'>——引用自《奇蹟課程》原文（第 47,50,88,110,132,182,268 等）</span>"),
 ("寬恕","「<strong>奇蹟課程</strong>」專教寬恕，用寬恕化解所有問題，連生老病死都能治。<br>真寬恕不是為改善關係，而是化解潛意識的罪咎。<span class='gap'></span><strong style='color:var(--ink)'>寬恕三要素：</strong>記得你在作夢、寬恕投射出的形象與自己、信賴聖靈。"),
 ("上主／耶穌（源自耶穌自傳，非新／舊約聖經）","「<strong>上帝</strong>」即「<strong>合一</strong>」，是一股無條件的愛的意識；<br>「<strong>耶穌</strong>」是平易近人的覺醒者，教人如何愛自己也愛別人。<span class='gap'></span><span style='color:var(--clay)'><strong>天國就在你心裡，物質世界是心靈分裂的夢境。</strong></span>"),
 ("對死亡的觀點","死亡不是滅亡，而是朝向更多的擴展，物質世界反而比死亡更像死亡。 <span style='font-size:.88em;color:var(--ink-faint)'>——巴夏</span>"),
 ("意識轉化四階段","從小我意識，轉向心靈意識<br>① 小我不再讓人滿足（內在空虛）<br>② 不帶評判、全然接納自己（療癒內在傷口）<br>③ 找到內在平靜、放開控制、努力「<strong>不做</strong>」<br>④ 向聖靈敞開、連結神性"),
 ("回歸自然","木喜將生活方式回歸自然，平日在山上種田養雞鴨，偶爾隨天音暫留城市完成任務，他表示：「<strong>人類世界本不自然，找回內在平靜，自然會好。</strong>」"),
]
QUOTES = [
 "你內那微細的勸勉之音，那輕柔的低語，在你開始思考它之前，真的就是上主天音的一部分……當你聽到它時，跟隨它。",
 "想做啥是第一個聲音，那是天音；如果跟「<strong>可是</strong>」是自我分析，專門破裂天音。",
 "放掉舊的才會看到新的。",
 "做自己就會帶來顯化，內在那感覺就是顯化方針。",
 "我給出去的會回來，讓它自然發展。",
 "天音就是我們內在的靈感、直覺、第六感、童心、赤子之心、還有來自內心的衝動（興奮）。",
 "只要你真心地想做一件事，宇宙會為你顯化出配備。",
 "能量可以轉變這句話，絕對稱不上是福音；造出能量的心靈是可以轉變的，這才是福音之所在。",
 "愛是老天賜給人的最偉大通靈能力。",
 "你沒病，是這社會運作方式讓人不舒服。",
]

def build_muxi():
    teach = "".join(f'<div class="teaching"><span class="t-no">{i+1:02d}</span><h3>{html.escape(t)}</h3><p>{d}</p></div>' for i,(t,d) in enumerate(TEACHINGS))
    quotes = "".join(f'<div class="quote">{q}</div>' for q in QUOTES)
    body = f"""<div class="read">
<div class="section-head"><div class="eyebrow">Section III</div>
<h1>木喜專區</h1>
<p>吳木喜身心靈教導精華：十一項核心理念與十句金句。</p>
<hr class="divider"></div>
{teach}

<div class="section-head" style="padding-top:3.5rem"><div class="eyebrow">Quotations</div><h2 style="font-size:2rem;font-weight:900">常引用的金句</h2><hr class="divider"></div>
<div class="quotes">{quotes}</div>
</div>"""
    page("木喜專區/index.html", "木喜專區 · 木喜身心靈", 1, body)

# ============================================================ 耶穌序精修
def patch_jesus_preface():
    """耶穌序專屬：抽出五個小節標題（引言/譯者序/作者序/導言/詞彙解析）＋跳轉按鈕、隱藏「序」大字。
    對 build_reader 產生的原始序頁做字串替換（因源檔為 OCR，小節標題黏在段落中）。"""
    f = os.path.join(ROOT, "書籍", "耶穌-我的自傳", "00_序.html")
    if not os.path.exists(f):
        print("  ⚠ 找不到耶穌序頁，跳過精修"); return
    s = open(f, encoding="utf-8").read()
    # 來源已改為乾淨 docx，小節標題各自獨立成段（<p>引言</p> 等），此處轉為 sec-title＋跳轉列。
    nav = ('<nav class="sec-jump">\n'
           '    <a href="#sec-translator">譯者序</a>\n'
           '    <a href="#sec-author">作者序</a>\n'
           '    <a href="#sec-preface">導言</a>\n'
           '    <a href="#sec-glossary">詞彙解析</a>\n'
           '  </nav>\n'
           '  <p class="sec-title" id="sec-intro">引言</p>')
    reps = [
      ('  <span class="chap-no">序</span>\n  <h1>序</h1>',
       '  <span class="chap-no" style="display:none">序</span>\n  <h1 style="display:none">序</h1>'),
      ('<p>引言</p>', nav),
      ('<p>譯者序</p>', '<p class="sec-title" id="sec-translator">譯者序</p>'),
      ('<p>作者序</p>', '<p class="sec-title" id="sec-author">作者序</p>'),
      ('<p>導言</p>', '<p class="sec-title" id="sec-preface">導言</p>'),
      ('<p>詞彙解析</p>', '<p class="sec-title" id="sec-glossary">詞彙解析</p>'),
    ]
    miss = 0
    for old, new in reps:
        if old in s: s = s.replace(old, new)
        else: miss += 1; print("  ⚠ 序頁 patch 未匹配：", old[:18], "…")
    open(f, "w", encoding="utf-8").write(s)
    print(f"✓ 耶穌序精修完成（{len(reps)-miss}/{len(reps)} 段套用）")

def patch_farewell_preface():
    """告別娑婆序：抽「作者序」小節標題、隱藏「序」大字（比照耶穌序）。"""
    f = os.path.join(ROOT, "書籍", "告別娑婆", "00_序.html")
    if not os.path.exists(f):
        print("  ⚠ 找不到告別娑婆序頁，跳過"); return
    s = open(f, encoding="utf-8").read()
    reps = [
      ('  <span class="chap-no">序</span>\n  <h1>序</h1>',
       '  <span class="chap-no" style="display:none">序</span>\n  <h1 style="display:none">序</h1>'),
      ('<p>作者序　當我還住在緬因州的鄉下時',
       '<p class="sec-title" id="sec-author">作者序</p>\n<p>當我還住在緬因州的鄉下時'),
    ]
    miss = 0
    for old, new in reps:
        if old in s: s = s.replace(old, new)
        else: miss += 1; print("  ⚠ 告別娑婆序 patch 未匹配：", old[:18], "…")
    open(f, "w", encoding="utf-8").write(s)
    print(f"✓ 告別娑婆序精修完成（{len(reps)-miss}/{len(reps)} 段套用）")

def patch_thiaoouba_preface():
    """海奧華序：抽「前言／序／問與答」三個小節標題＋跳轉按鈕、隱藏大字。"""
    f = os.path.join(ROOT, "書籍", "海奧華預言", "00_序與前言.html")
    if not os.path.exists(f):
        print("  ⚠ 找不到海奧華序頁，跳過"); return
    s = open(f, encoding="utf-8").read()
    reps = [
      ('  <span class="chap-no">序</span>\n  <h1>序與前言</h1>',
       '  <span class="chap-no" style="display:none">序</span>\n  <h1 style="display:none">序與前言</h1>\n'
       '  <nav class="sec-jump">\n'
       '    <a href="#sec-foreword">前言</a>\n'
       '    <a href="#sec-preface">序</a>\n'
       '    <a href="#sec-qa">問與答</a>\n'
       '  </nav>'),
      ('《聖經》譯文前言地球上有許許多多',
       '《聖經》譯文</p>\n<p class="sec-title" id="sec-foreword">前言</p>\n<p>地球上有許許多多'),
      ('<p>序我是遵命寫這本書的',
       '<p class="sec-title" id="sec-preface">序</p>\n<p>我是遵命寫這本書的'),
      ('<p>《海奧華預言》問與答問：怎麼發',
       '<p class="sec-title" id="sec-qa">問與答</p>\n<p>問：怎麼發'),
    ]
    miss = 0
    for old, new in reps:
        if old in s: s = s.replace(old, new)
        else: miss += 1; print("  ⚠ 海奧華序 patch 未匹配：", old[:18], "…")
    open(f, "w", encoding="utf-8").write(s)
    print(f"✓ 海奧華序精修完成（{len(reps)-miss}/{len(reps)} 段套用）")

# ============================================================ 執行
if __name__ == "__main__":
    build_home()
    build_book_list()
    for b in BOOKS:
        # 標記可讀全文者嘗試產生閱讀器；無章節檔則退回導讀頁
        if b.get("reader") and build_reader(b):
            continue
        build_book_intro(b)
    build_videos()
    build_muxi()
    patch_jesus_preface()
    patch_farewell_preface()
    patch_thiaoouba_preface()
    print("\n✅ 網站產生完成 →", ROOT)
