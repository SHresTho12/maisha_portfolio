"""Dependency-free static build for GitHub Pages. Run: python build.py"""
from pathlib import Path
from html import escape
from datetime import date
import json,re,shutil
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'dist'

def text(value):return escape(str(value),quote=True)
def asset_url(value,prefix='../../',image=False):
    from urllib.parse import urlsplit,quote
    value=value.strip();parsed=urlsplit(value)
    if parsed.scheme:
        if parsed.scheme not in ['https','http']:raise ValueError('Only http/https URLs are supported')
        return value
    if value.startswith('#') and not image:return value
    if value.startswith('//') or value.startswith('/') or '..' in Path(value).parts:raise ValueError('Use repository-relative assets/ paths, not root paths or parent traversal')
    if not value.startswith('assets/') or not (ROOT/value).is_file():raise ValueError(f'Missing local asset: {value}. Store article images in assets/blogs/')
    if image and Path(value).suffix.lower() not in ['.jpg','.jpeg','.png','.gif','.webp','.avif']:raise ValueError('Use JPG, PNG, GIF, WebP or AVIF images')
    return prefix+quote(value,safe='/')

def inline(value):
    pattern=re.compile(r'!\[([^\]]*)\]\(([^)]+)\)|\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*')
    parts=[];offset=0
    for m in pattern.finditer(value):
        parts.append(text(value[offset:m.start()]));alt,image,label,link,code,bold,italic=m.groups()
        if image is not None:parts.append('<img class="blog-image" src="'+text(asset_url(image,image=True))+'" alt="'+text(alt)+'" loading="lazy">')
        elif link is not None:parts.append('<a href="'+text(asset_url(link))+'">'+text(label)+'</a>')
        elif code is not None:parts.append('<code>'+text(code)+'</code>')
        elif bold is not None:parts.append('<strong>'+text(bold)+'</strong>')
        else:parts.append('<em>'+text(italic)+'</em>')
        offset=m.end()
    parts.append(text(value[offset:]));return ''.join(parts)

def render_markdown(body):
    parts=[];paragraph=[];items=[];code=[];fenced=False
    def flush():
        if paragraph:parts.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
        if items:parts.append('<ul>'+''.join('<li>'+inline(i)+'</li>' for i in items)+'</ul>');items.clear()
    for line in body.splitlines():
        if line.startswith('```'):
            if fenced:parts.append('<pre><code>'+text('\n'.join(code))+'</code></pre>');code.clear();fenced=False
            else:flush();fenced=True
            continue
        if fenced:code.append(line);continue
        if not line.strip():flush();continue
        image=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line.strip())
        if image:
            flush();alt,url=image.groups();parts.append('<figure><img class="blog-image" src="'+text(asset_url(url,image=True))+'" alt="'+text(alt)+'" loading="lazy">'+('<figcaption>'+text(alt)+'</figcaption>' if alt else '')+'</figure>');continue
        m=re.match(r'^(#{1,3})\s+(.+)$',line)
        if m:flush();level=min(len(m[1])+1,4);parts.append(f'<h{level}>'+inline(m[2])+f'</h{level}>')
        elif line.startswith('- '):
            if paragraph:flush()
            items.append(line[2:])
        else:
            if items:flush()
            paragraph.append(line)
    if fenced:parts.append('<pre><code>'+text('\n'.join(code))+'</code></pre>')
    flush();return '\n'.join(parts)

def discussion_widget(cfg,slug):
    g=cfg.get('comments',{})
    if not g.get('enabled'):return '<section class="article-discussion"><h2>Reactions and comments</h2><p>Comments and reactions are not connected yet.</p></section>'
    required=['repo','repoId','category','categoryId']
    if not all(g.get(k) for k in required):raise ValueError('Enabled comments need repo, repoId, category and categoryId from giscus.app')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',g['repo']):raise ValueError('Comments repo must use OWNER/REPOSITORY format')
    attrs={'data-repo':g['repo'],'data-repo-id':g['repoId'],'data-category':g['category'],'data-category-id':g['categoryId'],'data-mapping':'specific','data-term':'dental-blog/'+slug,'data-strict':'1','data-reactions-enabled':'1','data-emit-metadata':'0','data-input-position':'top','data-theme':'light','data-lang':g.get('language','en')}
    return '<section class="article-discussion"><h2>Reactions and comments</h2><p>Use thumbs-up to like or thumbs-down to dislike this article. Sign in with GitHub to react or comment.</p><div class="giscus"></div><script src="https://giscus.app/client.js" '+ ' '.join(k+'="'+text(v)+'"' for k,v in attrs.items())+' crossorigin="anonymous" async></script><p class="photo-comment"><a href="https://github.com/'+text(g['repo'])+'/discussions" target="_blank" rel="noopener">Open discussions on GitHub to attach a photo</a>. Choose the discussion titled dental-blog/'+text(slug)+'.</p><noscript>Enable JavaScript to view the comments, or open GitHub Discussions.</noscript></section>'

def article(path):
    source=path.read_text(encoding='utf-8');sections=source.split('---',2)
    if len(sections)!=3 or sections[0].strip():raise ValueError(f'{path.name}: use the front-matter format from first-article.md')
    meta={}
    for line in sections[1].splitlines():
        if not line.strip():continue
        key,value=line.split(':',1);meta[key.strip()]=value.strip()
    if meta.get('published','false').lower()!='true':return None
    if not meta.get('title'):raise ValueError(f'{path.name}: missing title')
    date.fromisoformat(meta['date'])
    if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',path.stem):raise ValueError('Use lowercase hyphenated filenames for articles')
    return dict(meta,slug=path.stem,body=render_markdown(sections[2]))

def blog_page(title,content,prefix,cfg):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{text(title)} | {text(cfg['name'])}</title><link rel="stylesheet" href="{prefix}assets/styles.css"></head><body><header class="blog-header"><div class="wrap"><a class="brand" href="{prefix}index.html">{text(cfg['name'])} · BDS</a><nav><a href="{prefix}blogs/">Blogs</a><a href="{prefix}index.html#booking">Book a consultation</a></nav></div></header><main class="section"><div class="wrap">{content}</div></main><footer>{text(cfg['name'])} · Dental Professional Portfolio</footer></body></html>'''

def main():
    cfg=json.loads((ROOT/'site.json').read_text(encoding='utf-8'));schedule=cfg['schedule']
    from zoneinfo import ZoneInfo
    ZoneInfo(schedule['timezone'])
    for key in ['start','end']:
        if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',schedule[key]):raise ValueError('Schedule times must be HH:MM in 24-hour format')
    start,end=[int(schedule[k][:2])*60+int(schedule[k][3:]) for k in ['start','end']]
    duration=schedule['durationMinutes']
    if type(duration)!=int or duration<=0 or start>=end or duration>end-start:raise ValueError('Invalid appointment duration or time range')
    if not schedule['days'] or any(type(d)!=int or d<0 or d>6 for d in schedule['days']):raise ValueError('Days use 0=Sunday through 6=Saturday')
    OUT.mkdir(exist_ok=True)
    # Clear only generated HTML so removing/unpublishing an article removes its page.
    if (OUT/'blogs').exists():shutil.rmtree(OUT/'blogs')
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    (OUT/'assets/config.js').write_text('window.SITE_CONFIG='+json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c')+';\n',encoding='utf-8')
    image=cfg.get('profileImage','')
    if image:
        if not image.startswith('assets/') or '..' in Path(image).parts or not (ROOT/image).is_file():raise ValueError('profileImage must point to an existing file under assets/')
        photo=f'<img class="profile-image" src="{text(image)}" alt="{text(cfg.get("profileImageAlt",cfg["name"]))}">'
    else:photo='<div class="monogram" aria-hidden="true">BDS</div>'
    reviews=cfg.get('reviews',[])
    review_html='<div class="review-grid">'+''.join('<article class="review"><blockquote>'+text(x['text'])+'</blockquote><p>'+text(x['name'])+'</p></article>' for x in reviews)+'</div>' if reviews else '<div class="review-empty"><h3>No patient reviews published yet.</h3><p>Genuine feedback shared with permission will appear here.</p></div>'
    names=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    label=f"Online: {', '.join(names[d] for d in schedule['days'])} · {schedule['start']}–{schedule['end']}<br>{duration}-minute slots · {text(schedule['timezone'])}"
    html=(ROOT/'templates/index.html').read_text(encoding='utf-8')
    for token,value in {'NAME':text(cfg['name']),'LOCATION':text(cfg['location']),'INTRO':text(cfg['intro'].replace('[FULL NAME]',cfg['name'])),'PROFILE_IMAGE':photo,'SCHEDULE_LABEL':label,'REVIEWS':review_html}.items():html=html.replace('{{'+token+'}}',value)
    (OUT/'index.html').write_text(html,encoding='utf-8');(OUT/'.nojekyll').touch()
    articles=[a for p in sorted((ROOT/'articles').glob('*.md')) if (a:=article(p))]
    articles.sort(key=lambda a:a['date'],reverse=True)
    cards=''.join(f'<article class="blog-card"><p class="eyebrow">{text(a["date"])}</p><h2><a href="{a["slug"]}/">{text(a["title"])}</a></h2><p>{text(a.get("summary",""))}</p><a href="{a["slug"]}/">Read article</a></article>' for a in articles)
    content='<p class="eyebrow">Notes on dental care</p><h1>Articles and insights</h1><p>Thoughts on oral health, preventive care and clinical experience.</p>'
    content+=('<div class="blog-list">'+cards+'</div>') if articles else '<h2>No articles published yet.</h2><p>New articles will appear here when they are published.</p>'
    (OUT/'blogs').mkdir(exist_ok=True);(OUT/'blogs/index.html').write_text(blog_page('Blogs',content,'../',cfg),encoding='utf-8')
    for a in articles:
        folder=OUT/'blogs'/a['slug'];folder.mkdir()
        content=f'<article class="article-body"><a href="../">All articles</a><p class="eyebrow" style="margin-top:25px">{text(a["date"])}</p><h1>{text(a["title"])}</h1><p>{text(a.get("summary",""))}</p>{a["body"]}</article>'
        cover=a.get('image','')
        if cover:
            cover_html='<img class="blog-cover" src="'+text(asset_url(cover,image=True))+'" alt="'+text(a.get('imageAlt',a['title']))+'">'
            content=content.replace('<h1>',cover_html+'<h1>',1)
        content+=discussion_widget(cfg,a['slug'])
        (folder/'index.html').write_text(blog_page(a['title'],content,'../../',cfg),encoding='utf-8')
    print(f'Built portfolio and {len(articles)} published articles in dist/')
if __name__=='__main__':main()
