(function () {
  const match = window.location.href.match(/^https:\/\/github\.com\/([^\/\?#]+\/[^\/\?#]+)/);
  if (match) {
    const newUrl = 'https://deepwiki.com/' + match[1];
    window.open(newUrl, '_blank');
  } else {
    alert('Not on a valid GitHub page.');
  }
})();
