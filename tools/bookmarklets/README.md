# Bookmarklets

Small JavaScript bookmarklets for browser productivity. Readable sources are in [`src/`](src/).

## Installation

1. Create a new bookmark in your browser.
2. Set any name you like.
3. Paste the minified code below as the URL.
4. Save.

---

## Get GitHub RSS Feed

Shows the Atom/RSS feed URL for a GitHub file's commit history.

**Works on:** GitHub file pages (`github.com/owner/repo/blob/branch/path/to/file`)

```
javascript:void function(){if(!window.location.href.includes('github.com'))return void alert('This bookmarklet only works on GitHub pages');const e=window.location.pathname.split('/');if(e.length<5||'blob'!==e[3])return void alert('This does not appear to be a GitHub file page');const t=e[1],n=e[2],o=e[4],i=e.slice(5).join('/'),r='https://github.com/'+t+'/'+n+'/commits/'+o+'/'+i+'.atom',l=document.createElement('div');l.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:flex;justify-content:center;align-items:center;z-index:9999;';const d=document.createElement('div');d.style.cssText='background:white;padding:20px;border-radius:6px;max-width:500px;width:90%;position:relative;font-family:sans-serif;';const a=document.createElement('span');a.textContent='×';a.style.cssText='position:absolute;right:10px;top:5px;cursor:pointer;font-size:20px;';a.onclick=function(){l.remove()};const h=document.createElement('h3');h.style.marginTop='0';h.textContent='RSS Feed URL';const p=document.createElement('input');p.type='text';p.value=r;p.readOnly=true;p.style.cssText='width:100%;padding:8px;margin:10px 0;border:1px solid #ddd;border-radius:4px;box-sizing:border-box;';p.onclick=function(){this.select()};const b=document.createElement('button');b.textContent='Copy';b.style.cssText='padding:8px 16px;background:#2da44e;color:white;border:none;border-radius:4px;cursor:pointer;font-size:14px;';b.onclick=function(){navigator.clipboard.writeText(r).then(function(){b.textContent='Copied!';setTimeout(function(){b.textContent='Copy'},2000)})};d.appendChild(a);d.appendChild(h);d.appendChild(p);d.appendChild(b);l.appendChild(d);document.body.appendChild(l);l.addEventListener('click',function(e){e.target===l&&l.remove()})}();
```

**Usage:** Open a GitHub file page, click the bookmarklet. A modal appears with the feed URL — click Copy to copy it.

---

## View in DeepWiki

Opens the current GitHub repository in [DeepWiki](https://deepwiki.com) in a new tab.

**Works on:** Any GitHub repository page (`github.com/owner/repo/*`)

```
javascript:(function(){const match=window.location.href.match(/^https:\/\/github\.com\/([^\/\?#]+\/[^\/\?#]+)/);if(match){const newUrl='https://deepwiki.com/'+match[1];window.open(newUrl,'_blank');}else{alert('Not on a valid GitHub page.');}})();
```

**Usage:** Open any page of a GitHub repository, click the bookmarklet. DeepWiki opens in a new tab.
