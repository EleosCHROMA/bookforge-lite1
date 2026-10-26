"""Offline, escaped reviewer view; contains answers and never grants approval."""
from html import escape


def render(packet,report):
    statuses={item['id']:item['status'] for item in report['items']}
    cards=[]
    import json
    for item in packet['items']:
        content=item['content']
        title=f"Chapter {content['chapter']} | {content['kind']} | {item['id']}"
        body=json.dumps(content['source'],indent=2,ensure_ascii=False)
        status=statuses[item['id']]
        cards.append(f'<article><h2>{escape(title)}</h2><p><strong>{escape(status)}</strong></p>'
                     f'<details><summary>Source fingerprint</summary><code>{escape(item["content_sha256"])}</code></details>'
                     f'<pre>{escape(body)}</pre></article>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mistake Mechanics editorial review</title>
<style>body{font:16px system-ui;max-width:1000px;margin:32px auto;padding:0 20px;color:#183354}
article{border:1px solid #cad6df;border-radius:10px;padding:18px;margin:18px 0}
h2{font-size:18px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.6 monospace}
input{font:inherit;padding:10px;width:90%}code{overflow-wrap:anywhere}header{border-bottom:3px solid #286e9c}
[hidden]{display:none}</style>
<header><h1>Mistake Mechanics: editorial review</h1>
<p>This reviewer-only file contains answers. Do not include it in the student workbook.</p>
<p>Statuses reflect supplied metadata. This page cannot approve or publish anything.</p></header>
<p><label for="search">Filter by chapter, item ID, prompt, answer or status</label></p>
<input id="search" type="search" placeholder="Search review items" autocomplete="off">
<p id="count" aria-live="polite"></p><main>'''+''.join(cards)+'''</main>
<script>
const input=document.getElementById('search'),cards=[...document.querySelectorAll('article')];
function filter(){let count=0;const term=input.value.toLowerCase();for(const card of cards){
card.hidden=!card.textContent.toLowerCase().includes(term);if(!card.hidden)count++;}
document.getElementById('count').textContent=count+' of '+cards.length+' review items shown';}
input.addEventListener('input',filter);filter();
</script></html>'''
