const form = document.querySelector('#link-form');
const input = document.querySelector('#url');
const message = document.querySelector('#message');
const result = document.querySelector('#result');
const list = document.querySelector('#links-list');
const count = document.querySelector('#link-count');

function shortUrl(code) { return `${location.origin}/${code}`; }
function safeText(value) { return String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char])); }

async function loadLinks() {
  const response = await fetch('/api/links');
  const links = await response.json();
  count.textContent = `${links.length} ${links.length === 1 ? 'LINK' : 'LINKS'}`;
  if (!links.length) { list.innerHTML = '<div class="empty">Your links will show up here.</div>'; return; }
  list.innerHTML = links.map(link => `<div class="link-row"><span class="destination" title="${safeText(link.destination)}">${safeText(link.destination)}</span><a class="short-link" href="/${encodeURIComponent(link.code)}" target="_blank" rel="noopener">${safeText(shortUrl(link.code))}</a><span class="clicks">${link.clicks}</span></div>`).join('');
}

form.addEventListener('submit', async event => {
  event.preventDefault(); message.textContent = ''; result.hidden = true;
  try {
    const response = await fetch('/api/links', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url:input.value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not create that link.');
    result.innerHTML = `Your short link is ready: <a href="/${encodeURIComponent(data.code)}" target="_blank" rel="noopener">${safeText(shortUrl(data.code))}</a>`;
    result.hidden = false; input.value = ''; await loadLinks();
  } catch (error) { message.textContent = error.message || 'Something went wrong. Please try again.'; }
});

loadLinks().catch(() => { list.innerHTML = '<div class="empty">Could not load links. Refresh to try again.</div>'; });
