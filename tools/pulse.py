# -*- coding: utf-8 -*-
"""Carbon Pulse — 碳市場新聞聚合
   自公開 RSS 抓取、去重、依關鍵字分類，輸出 data/news.json
   用法：python pulse.py <輸出目錄>
"""
import io, sys, os, json, re, time, html, urllib.request
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

# 來源對齊 .claude/watchlist/sources.md 的 11 條情報線
FEEDS = [
    # 碳市場專門（相關度最高，優先）
    ('Verra',                'https://verra.org/feed/',                        '標準'),
    ('ICVCM',                'https://icvcm.org/feed/',                        '標準'),
    ('Carbon Market Watch',  'https://carbonmarketwatch.org/feed/',            '完整性'),
    ('Ecosystem Marketplace','https://www.ecosystemmarketplace.com/feed/',     '市場'),
    ('Carbon Credits',       'https://carboncredits.com/feed/',                '市場'),
    ('Carbon Herald',        'https://carbonherald.com/feed/',                 '市場'),
    # 氣候政策與科學（相關度中，會被閘門過濾）
    ('Carbon Brief',         'https://www.carbonbrief.org/feed/',              '科學'),
    ('IPCC',                 'https://www.ipcc.ch/feed/',                      '科學'),
    ('Climate Home News',    'https://www.climatechangenews.com/feed/',        '政策'),
    ('ESG Today',            'https://www.esgtoday.com/feed/',                 '企業'),
    ('Eco-Business',         'https://www.eco-business.com/feeds/news/',       '亞太'),
]

# 相關性閘門：未命中者標為「一般」，不進主流
RELEVANT = re.compile(
    r'\b(carbon|co2|co₂|emission|offset|credit|net[- ]zero|decarbon|ghg|'
    r'removal|sequestr|cdr|mitigation|climate finance|carbon market|'
    r'verra|gold standard|icvcm|corsia|sbti|article\s*6|redd|'
    r'reforest|afforest|mangrove|biochar|cookstove|碳)\b', re.I)

# 分類規則：依序比對，先中者為準（完整性最優先，它最具新聞價值）
RULES = [
    ('完整性', r'\b(integrity|fraud|overstat|greenwash|investigation|scandal|'
               r'suspend|revok|withdraw|junk credit|phantom|misleading|lawsuit|'
               r'sued|allegation|probe|whistleblow)\b'),
    ('標準', r'\b(verra|gold standard|\bvcs\b|methodolog|icvcm|\bccp\b|corsia|sbti|vcmi|'
             r'plan vivo|puro|isometric|accredit|validat|verif|registry|'
             r'protocol|certif|label|baseline|additionality|buffer pool)\b'),
    ('法規', r'\b(regulation|legislation|directive|compliance|parliament|'
             r'article\s*6|paris agreement|cop\d{1,2}|unfccc|ets\b|'
             r'carbon tax|carbon price|cbam|mandate|ruling|court|bill\b|'
             r'government|ministry|policy|law\b)\b'),
    ('市場', r'\b(price|market|trading|demand|supply|offtake|deal\b|acquisition|'
             r'funding|invest|raise[sd]?\b|portfolio|buyer|purchase|sold|sales|'
             r'million|billion|transaction|exchange)\b'),
    ('專案', r'\b(project|reforestation|afforestation|mangrove|biochar|cookstove|'
             r'redd|removal|sequestration|restoration|hectare|plantation|'
             r'pilot|deploy|launch)\b'),
    ('科學', r'\b(study|research|report|paper|data|analysis|scientist|'
             r'ipcc|assessment|model|finding)\b'),
]

# 與我方業務相關的標記
TAGS = [
    ('藍碳',   r'\b(mangrove|blue carbon|tidal|seagrass|salt marsh|紅樹林|藍碳)\b'),
    ('ARR',    r'\b(afforestation|reforestation|revegetation|agroforestry|arr)\b'),
    ('土壤碳', r'\b(soil carbon|soc|grassland|rangeland|regenerative ag)\b'),
    ('東非',   r'\b(kenya|tanzania|uganda|ethiopia|rwanda|east africa)\b'),
    ('東南亞', r'\b(myanmar|vietnam|indonesia|thailand|cambodia|laos|philippines)\b'),
    ('莫三比克', r'\b(mozambique)\b'),
    ('第六條', r'\b(article\s*6|itmo|corresponding adjustment|pacm)\b'),
]


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': UA,
                'Accept': 'application/rss+xml,application/xml,text/xml,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
                'Accept-Encoding': 'identity'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1:
                return None
            time.sleep(2)


def strip(s):
    s = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', s or '', flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def field(block, *names):
    for n in names:
        m = re.search(r'<%s[^>]*>(.*?)</%s>' % (n, n), block, re.S | re.I)
        if m:
            return strip(m.group(1))
    return ''


def classify(text):
    if not RELEVANT.search(text):
        return '一般'
    for name, pat in RULES:
        if re.search(pat, text, re.I):
            return name
    return '其他'


def tags_of(text):
    t = text.lower()
    return [n for n, p in TAGS if re.search(p, t, re.I)]


items, seen = [], set()
for src, url, bucket in FEEDS:
    raw = get(url)
    if not raw:
        print('  %-20s 抓取失敗' % src); continue
    blocks = re.findall(r'<item[^>]*>(.*?)</item>', raw, re.S | re.I)
    if not blocks:
        blocks = re.findall(r'<entry[^>]*>(.*?)</entry>', raw, re.S | re.I)
    n = 0
    for b in blocks:
        title = field(b, 'title')
        if not title:
            continue
        key = re.sub(r'[^a-z0-9]', '', title.lower())[:70]
        if key in seen:
            continue
        seen.add(key)
        link = field(b, 'link')
        if not link:
            m = re.search(r'<link[^>]*href="([^"]+)"', b)
            link = m.group(1) if m else ''
        desc = field(b, 'description', 'summary', 'content:encoded')[:400]
        pub = field(b, 'pubDate', 'published', 'updated', 'dc:date')
        ts = None
        for parse in (lambda s: parsedate_to_datetime(s),
                      lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))):
            try:
                d = parse(pub)
                ts = int((d if d.tzinfo else d.replace(tzinfo=timezone.utc)).timestamp())
                break
            except Exception:
                pass
        blob = title + ' ' + desc
        cat = classify(blob)
        items.append(dict(t=title, u=link, s=src, b=bucket, d=desc,
                          ts=ts or 0, c=cat, g=tags_of(blob),
                          rel=0 if cat == '一般' else 1))
        n += 1
    print('  %-20s %d 則' % (src, n))

items.sort(key=lambda x: (-x['rel'], -x['ts']))
items = items[:400]

OUT = sys.argv[1] if len(sys.argv) > 1 else '../data'
os.makedirs(OUT, exist_ok=True)
json.dump(dict(
    built=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M'),
    sources=[f[0] for f in FEEDS],
    items=items,
), open(os.path.join(OUT, 'news.json'), 'w', encoding='utf-8'),
    ensure_ascii=False, separators=(',', ':'))

print()
print('共 %d 則 → %s/news.json' % (len(items), OUT))
cnt = {}
for i in items:
    cnt[i['c']] = cnt.get(i['c'], 0) + 1
print('分類：' + '  '.join('%s %d' % kv for kv in sorted(cnt.items(), key=lambda x: -x[1])))
tg = {}
for i in items:
    for g in i['g']:
        tg[g] = tg.get(g, 0) + 1
if tg:
    print('標記：' + '  '.join('%s %d' % kv for kv in sorted(tg.items(), key=lambda x: -x[1])))
