#!/usr/bin/env python3
"""Build the Cai Lab's portable, dependency-free GitHub Pages website."""
from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import shutil
from datetime import date
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
DATA = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
LAB = DATA['lab']
PI = LAB['pi']
PAGES = [('home','Home','index.html'),('research','Research','research.html'),
         ('people','People','people.html'),('publications','Publications','publications.html'),
         ('news','News','news.html'),('join','Join Us','join-us.html'),('contact','Contact','contact.html')]
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>'
EXTERNAL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 18 18 6M6 6h12v12"/></svg>'

def esc(value):
    return html.escape(str(value), quote=True)

def link(url, label, css='text-link', external=False):
    extra = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return f'<a class="{css}" href="{esc(url)}"{extra}>{label}{EXTERNAL if external else ARROW}</a>'

def mail(subject='Research inquiry'):
    return f'mailto:{LAB["email"]}?subject={quote(subject)}'

def kicker(text):
    return f'<p class="eyebrow"><span class="eyebrow-line" aria-hidden="true"></span>{esc(text)}</p>'

def date_label(value):
    return date.fromisoformat(value).strftime('%B %d, %Y').replace(' 0',' ')

def section_head(label, title, href=None, cta=None):
    return f'<div class="section-heading"><div>{kicker(label)}<h2>{title}</h2></div>{link(href, cta) if href else ""}</div>'

def page_head(label, title, description, aside=''):
    return f'<section class="page-head wrap"><div>{kicker(label)}<h1>{title}</h1><p class="page-intro">{description}</p></div>{aside}</section>'

def tags(values):
    return '<div class="tags">'+''.join(f'<span>{esc(t)}</span>' for t in values)+'</div>'

def pub_card(pub, compact=False):
    title = esc(pub['title'])
    authors = '; '.join(f'<strong>{esc(a)}</strong>' if a == PI['name'] else esc(a) for a in pub['authors'])
    citation = f'{"; ".join(pub["authors"])}. {pub["title"]}. {pub["journal"]}. {pub["year"]};{pub["volume_issue_pages"]}. doi:{pub["doi"]}'
    search = ' '.join([pub['title'],*pub['authors'],pub['journal'],*pub['topics'],str(pub['year'])])
    return f'''<article class="publication {'compact' if compact else ''}" data-publication data-year="{pub['year']}" data-topics="{esc('|'.join(pub['topics']))}" data-search="{esc(search.lower())}">
      <div class="pub-year">{pub['year']}<span class="pub-year-line"></span></div>
      <div class="pub-content"><p class="pub-journal">{esc(pub['journal'])}</p>
      <h3><a href="https://doi.org/{esc(pub['doi'])}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
      <p class="pub-authors">{authors}</p><p class="pub-details">{pub['year']}; {esc(pub['volume_issue_pages'])}</p>
      {'' if compact else tags(pub['topics'])}
      <div class="pub-actions">{link('https://doi.org/'+pub['doi'],'Read article',external=True)}{link(pub['pubmed_url'],'PubMed',external=True)}
      {'' if compact else f'<button class="text-link copy-citation" data-copy="{esc(citation)}" type="button">Copy citation<span aria-hidden="true">+</span></button>'}</div></div></article>'''

def news_card(item, idx):
    return f'''<article class="news-card"><div class="news-card-top"><span class="news-number">0{idx+1}</span><time datetime="{item['date']}">{date_label(item['date'])}</time></div>
    <p class="eyebrow">From Mizzou</p><h3><a href="{esc(item['url'])}" target="_blank" rel="noopener noreferrer">{esc(item['title'])}</a></h3><p>{esc(item['summary'])}</p>
    {link(item['url'],'Read the story',external=True)}</article>'''

def home():
    research = ''.join(f'''<a class="research-teaser" href="research.html#{esc(r['id'])}"><span class="teaser-number">0{i+1}</span><h3>{esc(r['title'])}</h3><p>{esc(r['summary'])}</p><span class="teaser-link">Explore this area {ARROW}</span></a>''' for i,r in enumerate(DATA['research']))
    focus_labels = ['Marfan syndrome', 'RNA therapeutics', 'AVC', 'Thoracic aortic aneurysm']
    focus = ''.join(f'<a href="research.html#{esc(r["id"])}">{esc(label)}</a>' for r,label in zip(DATA['research'],focus_labels))
    spotlight = next((n for n in DATA['news'] if 'marfan' in n['title'].lower()), DATA['news'][0])
    featured = [pub_card(p, True) for p in DATA['publications'] if p['featured']]
    return f'''
    <section class="hero wrap"><div class="hero-copy">{kicker('University of Missouri · School of Medicine')}
      <h1>Marfan syndrome.<br><em>Toward RNA therapies.</em></h1>
      <p class="hero-intro">We study Marfan syndrome, develop RNA-based therapeutic strategies, and investigate aortic valve calcification and thoracic aortic aneurysm.</p>
      <nav class="hero-focus" aria-label="Research focus">{focus}</nav>
      <div class="hero-actions">{link('research.html','Explore our research','button button-dark')}{link('people.html','Meet the lab')}</div>
    </div><figure class="hero-art"><img src="assets/vessel-field.svg" width="1100" height="1250" alt="Conceptual illustration combining a golden aortic arch and RNA forms" fetchpriority="high"><div class="art-label"><span>Aortic disease &amp; RNA therapeutics</span><span>From mechanisms to new possibilities</span></div><figcaption>Conceptual aortic &amp; RNA illustration</figcaption></figure></section>
    <section class="news-strip wrap" aria-label="Research highlight"><span class="news-strip-label"><span class="status-dot" aria-hidden="true"></span>Research spotlight</span><p>Exploring RNA-based approaches to Marfan syndrome.</p>{link(spotlight['url'],'Read at Mizzou',external=True)}</section>
    <section class="section wrap">{section_head('Four research directions','Aortic disease.<br>New therapeutic possibilities.','research.html','All research areas')}<p class="section-lead">Marfan syndrome and RNA therapeutics anchor our work, alongside investigations of aortic valve calcification (AVC) and thoracic aortic aneurysm (TAA).</p><div class="research-teasers">{research}</div></section>
    <section class="approach-section"><div class="wrap approach-grid"><div>{kicker('Our approach')}<h2>From molecular causes<br>to therapeutic strategies.</h2><p>We connect molecular biology, RNA approaches, imaging, and experimental models to investigate aortic and valve disease.</p>{link('research.html#rna-therapeutics','Explore RNA research','text-link light-link')}</div><div class="approach-steps"><div><span>01</span><h3>Understand disease mechanisms</h3><p>Investigate how genetic changes and cellular responses affect the aortic wall and valve.</p></div><div><span>02</span><h3>Explore RNA strategies</h3><p>Study RNA-based approaches that address disease-associated molecular changes.</p></div><div><span>03</span><h3>Evaluate in disease models</h3><p>Connect mechanistic insights with experimental studies of potential interventions.</p></div></div></div></section>
    <section class="section wrap">{section_head('Selected publications','Discovery, in print.','publications.html','Browse publications')}<div class="publication-list">{''.join(featured)}</div></section>
    <section class="section news-section"><div class="wrap">{section_head('Lab & university news','The latest from our research.','news.html','All news')}<div class="news-grid">{''.join(news_card(n,i) for i,n in enumerate(DATA['news']))}</div></div></section>
    <section class="join-banner wrap"><div>{kicker('Connect with us')}<h2>Good science starts<br>with a conversation.</h2><p>Interested in our research, training, or collaboration? We would like to hear from you.</p></div>{link('join-us.html','Explore opportunities','button button-dark')}</section>
    '''

def research():
    parts=[]
    own_publications = {p['pubmed_url'] for p in DATA['publications']}
    legacy_ids = {'marfan-syndrome': [], 'rna-therapeutics': ['rna-approaches'], 'aortic-valve-calcification': ['valve-disease'], 'thoracic-aortic-aneurysm': ['vascular-remodeling']}
    for i,r in enumerate(DATA['research']):
        related=''.join(link(u, 'University research story' if 'medicine.missouri.edu' in u else ('Related publication' if u in own_publications else 'Scientific background'), external=True) for u in r['source_urls'][:2])
        aliases=''.join(f'<span id="{esc(alias)}" class="anchor-alias" aria-hidden="true"></span>' for alias in legacy_ids.get(r['id'], []))
        parts.append(f'''<article class="research-area" id="{esc(r['id'])}">{aliases}<div class="area-index">0{i+1}<span>{esc(r['eyebrow'])}</span></div><div class="area-main"><h2>{esc(r['title'])}</h2><p class="area-summary">{esc(r['summary'])}</p><p>{esc(r['body'])}</p>{tags(r['topics'])}<div class="research-sources">{related}</div></div><div class="area-art art-{i}" aria-hidden="true"><div class="art-orbit one"></div><div class="art-orbit two"></div><div class="art-orbit three"></div><span class="art-center"></span></div></article>''')
    jump_nav='<nav class="wrap research-jump-nav" aria-label="Research directions">'+''.join(f'<a href="#{esc(r["id"])}"><span>0{i+1}</span> {esc(r["title"])}</a>' for i,r in enumerate(DATA['research']))+'</nav>'
    return page_head('Research','Marfan syndrome.<br><em>RNA therapeutics &amp; aortic disease.</em>','Four connected programs explore Marfan syndrome, RNA-based therapeutic strategies, aortic valve calcification (AVC), and thoracic aortic aneurysm (TAA).')+jump_nav+f'<div class="wrap research-areas">{"".join(parts)}</div>'+f'<section class="wrap bottom-cta" id="disease-models"><div><p class="eyebrow">Mechanisms &amp; models</p><h2>Explore the work behind the questions.</h2></div>{link("publications.html","View selected publications","button button-dark")}</section>'

def people():
    bio=''.join(f'<p>{esc(x)}</p>' for x in PI['bio'])
    training=''.join(f'<li>{esc(x)}</li>' for x in PI['education'])
    return page_head('People','Meet our<br><em>principal investigator.</em>','Research in Marfan syndrome, RNA therapeutics, and aortic disease at the University of Missouri.')+f'''
    <section class="wrap pi-profile"><figure class="pi-photo"><img src="assets/dunpeng-cai.png" width="1000" height="1200" alt="Dunpeng Cai, PhD" loading="eager"><figcaption>Photo: University of Missouri School of Medicine</figcaption></figure><div class="pi-bio">{kicker('Principal Investigator')}<h2>{esc(PI['name'])}, <span>{esc(PI['credentials'])}</span></h2><p class="pi-title">{esc(PI['title'])} · {esc(LAB['department'])}<br>{esc(LAB['school'])}, {esc(LAB['institution'])}</p>{bio}<div class="profile-links">{link(PI['profile_url'],'Faculty profile',external=True)}{link(PI['scholar_url'],'Google Scholar',external=True)}{link(mail('Research inquiry'),'Email Dr. Cai')}</div><div class="training"><h3>Education &amp; training</h3><ul>{training}</ul></div></div></section>
    <section class="wrap people-note"><div><p class="eyebrow">A collaborative research environment</p><h2>Shared curiosity.<br>Complementary perspectives.</h2></div><div><p>Our scientific questions connect cell biology, vascular physiology, microsurgery, and translational research. We value conversations across these fields.</p>{link('join-us.html','Get in touch about working together')}</div></section>'''

def publications():
    years=sorted({p['year'] for p in DATA['publications']},reverse=True)
    topics=sorted({t for p in DATA['publications'] for t in p['topics']})
    options=''.join(f'<option value="{y}">{y}</option>' for y in years)
    chips='<button type="button" class="filter-chip active" data-topic="all" aria-pressed="true">All topics</button>'+''.join(f'<button type="button" class="filter-chip" data-topic="{esc(t)}" aria-pressed="false">{esc(t)}</button>' for t in topics)
    return page_head('Publications','Selected work.<br><em>Open to exploration.</em>','A selection of publications involving Dr. Cai, including work from prior training and collaborative research.',link(PI['scholar_url'],'Full bibliography','button button-outline',True))+f'''
    <section class="wrap publications-section"><div class="publication-tools js-only"><div class="search-field"><label for="pub-search">Search publications</label><input type="search" id="pub-search" placeholder="Search a title, author, or topic…" autocomplete="off"></div><div class="year-field"><label for="pub-year">Publication year</label><select id="pub-year"><option value="all">All years</option>{options}</select></div><button class="reset-button" type="button" id="pub-reset">Reset filters</button></div><div class="filter-chips js-only" aria-label="Filter publications by topic">{chips}</div><div class="pub-toolbar"><p id="pub-count" aria-live="polite">{len(DATA['publications'])} selected publications</p><div class="citation-downloads"><a href="publications.ris" download>Download RIS</a><a href="publications.bib" download>BibTeX</a></div></div><div class="publication-list">{''.join(pub_card(p) for p in DATA['publications'])}</div><div class="no-results" id="no-results" hidden><h2>No matching publications</h2><p>Try a broader search or reset the filters.</p></div><p class="publication-note">Years follow the journal issue citation when available. RIS files can be imported into EndNote, Zotero, and other reference managers.</p></section>'''

def news():
    return page_head('News','Research, milestones,<br><em>and new directions.</em>','Selected research stories published by the University of Missouri School of Medicine.')+f'<section class="wrap section news-page-grid"><div class="news-grid">{"".join(news_card(n,i) for i,n in enumerate(DATA["news"]))}</div></section><section class="wrap bottom-cta"><div><p class="eyebrow">Explore further</p><h2>The science behind the stories.</h2></div>{link("publications.html","View publications","button button-dark")}</section>'

def join():
    roles=[('For prospective trainees','Tell us about your scientific interests, your training, and the questions you would like to investigate.','Training inquiry — Cai Lab'),('For research collaborators','Connect with us about complementary expertise, experimental models, and shared research questions.','Collaboration inquiry — Cai Lab')]
    cards=''.join(f'<article class="opportunity"><span class="teaser-number">0{i+1}</span><h3>{esc(t)}</h3><p>{esc(p)}</p>{link(mail(s),"Start a conversation")}</article>' for i,(t,p,s) in enumerate(roles))
    return page_head('Join Us','Bring your curiosity.<br><em>Start a conversation.</em>','If our research connects with your interests, contact Dr. Cai to discuss possible training and collaboration opportunities.')+f'''
    <section class="wrap join-layout"><div><h2>Science shaped<br>by shared questions.</h2><p>Our research brings together Marfan syndrome, RNA therapeutics, aortic valve calcification, and thoracic aortic aneurysm. Prospective trainees and collaborators are welcome to introduce their interests in these areas.</p><p class="quiet-note">For current opportunities and availability, please contact Dr. Cai directly.</p></div><div class="opportunities">{cards}</div></section>
    <section class="application-band"><div class="wrap application-inner"><div>{kicker('Getting in touch')}<h2>A useful first introduction.</h2></div><ol><li><span>01</span><div><strong>Your background</strong><p>A short introduction to your current role and training.</p></div></li><li><span>02</span><div><strong>Your scientific interests</strong><p>The research questions that draw you to the lab.</p></div></li><li><span>03</span><div><strong>Your next step</strong><p>The training or collaboration you would like to discuss, and your CV if relevant.</p></div></li></ol>{link(mail('Introduction — Cai Lab'), 'Email Dr. Cai', 'button button-dark')}</div></section>'''

def contact():
    address='<br>'.join(esc(a) for a in LAB['address'])
    return page_head('Contact','Let’s connect.<br><em>Science begins here.</em>','For research, training, and collaboration inquiries, please contact Dr. Dunpeng Cai.')+f'''
    <section class="wrap contact-layout"><div class="contact-primary">{kicker('Research inquiries')}<h2>{esc(PI['name'])}, PhD</h2><p>{esc(PI['title'])}<br>{esc(LAB['department'])}<br>{esc(LAB['school'])}</p><a class="contact-email" href="mailto:{esc(LAB['email'])}">{esc(LAB['email'])}{EXTERNAL}</a><div class="contact-actions">{link(mail('Research inquiry — Cai Lab'),'Send an email','button button-dark')}<button type="button" class="text-link js-only" data-copy="{esc(LAB['email'])}">Copy email<span aria-hidden="true">+</span></button></div></div><div class="contact-address"><span class="location-word" aria-hidden="true">Columbia<br><em>Missouri.</em></span><div class="location-details"><p class="eyebrow">University of Missouri</p><address>{address}</address>{link(PI['profile_url'],'Institutional profile',external=True)}</div></div></section>
    <section class="wrap contact-secondary"><h2>More from the lab</h2><div>{link('research.html','Research areas')}{link('publications.html','Selected publications')}{link(PI['scholar_url'],'Google Scholar',external=True)}</div></section>'''

def render(key, label, filename, body, site_url=''):
    nav=''.join(f'<a href="{f}" {"aria-current=\"page\"" if k==key else ""}>{n}</a>' for k,n,f in PAGES)
    footer_nav=''.join(f'<a href="{f}">{n}</a>' for k,n,f in PAGES if k!='home')
    title='Cai Lab | Marfan Syndrome & RNA Therapeutics | University of Missouri' if key=='home' else f'{label} | Cai Lab | University of Missouri'
    description='The Cai Lab at the University of Missouri studies Marfan syndrome, RNA therapeutics, aortic valve calcification (AVC), and thoracic aortic aneurysm.'
    canonical=f'<link rel="canonical" href="{esc(site_url+"/"+filename)}"><meta property="og:url" content="{esc(site_url+"/"+filename)}">' if site_url else ''
    if key == '404' and site_url:
        canonical = f'<base href="{esc(urlparse(site_url).path.rstrip("/")+"/")}">' + canonical
    structured={'@context':'https://schema.org','@type':'ResearchOrganization','name':LAB['name'],'description':description,'email':LAB['email'],'parentOrganization':{'@type':'CollegeOrUniversity','name':LAB['institution']},'address':{'@type':'PostalAddress','streetAddress':'1 Hospital Drive, M702','addressLocality':'Columbia','addressRegion':'MO','postalCode':'65201','addressCountry':'US'}}
    if site_url: structured['url']=site_url+'/'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#f1b82d"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">{canonical}<link rel="icon" type="image/svg+xml" href="assets/favicon.svg"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script><script type="application/ld+json">{json.dumps(structured).replace('<','\\u003c')}</script></head>
<body class="page-{key}"><a class="skip-link" href="#main">Skip to content</a><div class="topbar"><div class="wrap"><span>{esc(LAB['institution'])} <span class="topbar-divider">/</span> {esc(LAB['school'])}</span><span class="topbar-location">Columbia, Missouri</span></div></div>
<header class="site-header"><div class="wrap nav-shell"><a class="brand" href="index.html" aria-label="Cai Lab home"><span class="brand-mark" aria-hidden="true">C<span></span></span><span class="brand-name">CAI <b>LAB</b><small>{esc(LAB['tagline'])}</small></span></a><button class="menu-toggle js-only" type="button" aria-controls="site-nav" aria-expanded="false"><span>Menu</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button><nav id="site-nav" class="site-nav" aria-label="Main navigation">{nav}</nav></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="wrap footer-top"><div><a class="footer-brand" href="index.html">CAI LAB<span>{esc(LAB['tagline'])}</span></a><p>{esc(LAB['department'])}<br>{esc(LAB['school'])}<br>{esc(LAB['institution'])}</p></div><div class="footer-nav" aria-label="Footer navigation">{footer_nav}</div><div class="footer-contact"><p class="eyebrow">Let’s connect</p><a href="mailto:{esc(LAB['email'])}">{esc(LAB['email'])}</a><p>Columbia, Missouri</p>{link(PI['profile_url'],'Mizzou faculty profile','text-link light-link',True)}</div></div><div class="wrap footer-bottom"><p>© {date.today().year} Cai Lab. All rights reserved.</p><span>Marfan syndrome · RNA therapeutics · AVC · Thoracic aortic aneurysm</span></div></footer><div class="toast" role="status" aria-live="polite" id="toast" hidden></div></body></html>'''

def exports():
    ris=[]; bib=[]
    for p in DATA['publications']:
        authors=[a.rsplit(' ',1)[1]+', '+a.rsplit(' ',1)[0] if ' ' in a else a for a in p['authors']]
        ris.extend(['TY  - JOUR',f'TI  - {p["title"]}',*[f'AU  - {a}' for a in authors],f'PY  - {p["year"]}',f'JO  - {p["journal"]}',f'DO  - {p["doi"]}',f'UR  - https://doi.org/{p["doi"]}','ER  - ',''])
        def safe(s): return str(s).replace('{','\\{').replace('}','\\}').replace('&','\\&')
        bib.append('@article{'+p['id']+',\n'+',\n'.join('  '+k+' = {'+safe(v)+'}' for k,v in [('title',p['title']),('author',' and '.join(authors)),('year',p['year']),('journal',p['journal']),('doi',p['doi']),('url','https://doi.org/'+p['doi'])])+'\n}')
    (OUT/'publications.ris').write_text('\n'.join(ris),encoding='utf-8')
    (OUT/'publications.bib').write_text('\n\n'.join(bib)+'\n',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-url',default=os.environ.get('SITE_URL',''))
    args=parser.parse_args()
    site_url=args.site_url.strip().rstrip('/')
    if site_url and (urlparse(site_url).scheme not in ('http','https') or not urlparse(site_url).netloc):
        raise SystemExit('--site-url must be an absolute HTTP(S) URL')
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    builders={'home':home,'research':research,'people':people,'publications':publications,'news':news,'join':join,'contact':contact}
    for key,label,filename in PAGES:
        (OUT/filename).write_text(render(key,label,filename,builders[key](),site_url),encoding='utf-8')
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    (OUT/'404.html').write_text(render('404','Page not found','404.html',page_head('404','A different direction.','The page you’re looking for could not be found.')+'<div class="wrap error-back">'+link('index.html','Return home','button button-dark')+'</div>',site_url),encoding='utf-8')
    if site_url:
        urls=''.join(f'<url><loc>{esc(site_url+"/"+f)}</loc></url>' for _,_,f in PAGES)
        (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>',encoding='utf-8')
        (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+site_url+'/sitemap.xml\n',encoding='utf-8')
    else:
        (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n',encoding='utf-8')
    exports()
    print(f'Built {len(PAGES)} pages, 404 page, and citation downloads in {OUT}')

if __name__=='__main__':
    main()
