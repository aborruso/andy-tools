void function () {
  if (!window.location.href.includes('github.com'))
    return void alert('This bookmarklet only works on GitHub pages');

  const parts = window.location.pathname.split('/');
  if (parts.length < 5 || 'blob' !== parts[3])
    return void alert('This does not appear to be a GitHub file page');

  const owner = parts[1];
  const repo = parts[2];
  const branch = parts[4];
  const filePath = parts.slice(5).join('/');

  const feedUrl =
    'https://github.com/' + owner + '/' + repo +
    '/commits/' + branch + '/' + filePath + '.atom';

  const overlay = document.createElement('div');
  overlay.style.cssText =
    'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);' +
    'display:flex;justify-content:center;align-items:center;z-index:9999;';

  const box = document.createElement('div');
  box.style.cssText =
    'background:white;padding:20px;border-radius:6px;max-width:500px;' +
    'width:90%;position:relative;font-family:sans-serif;';

  const close = document.createElement('span');
  close.textContent = '×';
  close.style.cssText = 'position:absolute;right:10px;top:5px;cursor:pointer;font-size:20px;';
  close.onclick = function () { overlay.remove(); };

  const title = document.createElement('h3');
  title.style.marginTop = '0';
  title.textContent = 'RSS Feed URL';

  const input = document.createElement('input');
  input.type = 'text';
  input.value = feedUrl;
  input.readOnly = true;
  input.style.cssText =
    'width:100%;padding:8px;margin:10px 0;border:1px solid #ddd;' +
    'border-radius:4px;box-sizing:border-box;';
  input.onclick = function () { this.select(); };

  const btn = document.createElement('button');
  btn.textContent = 'Copy';
  btn.style.cssText =
    'padding:8px 16px;background:#2da44e;color:white;border:none;' +
    'border-radius:4px;cursor:pointer;font-size:14px;';
  btn.onclick = function () {
    navigator.clipboard.writeText(feedUrl).then(function () {
      btn.textContent = 'Copied!';
      setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
    });
  };

  box.appendChild(close);
  box.appendChild(title);
  box.appendChild(input);
  box.appendChild(btn);
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  overlay.addEventListener('click', function (e) { if (e.target === overlay) overlay.remove(); });
}();
