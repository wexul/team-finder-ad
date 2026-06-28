function getCookie(name) {
  const cookies = document.cookie ? document.cookie.split(';') : [];
  for (const cookie of cookies) {
    const trimmed = cookie.trim();
    if (trimmed.startsWith(name + '=')) return decodeURIComponent(trimmed.slice(name.length + 1));
  }
  return null;
}

async function postJson(url) {
  const response = await fetch(url, {method: 'POST', headers: {'X-CSRFToken': getCookie('csrftoken')}});
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || 'request_failed');
  return data;
}

document.getElementById('complete-project')?.addEventListener('click', async (event) => {
  await postJson(event.currentTarget.dataset.url);
  location.reload();
});

document.getElementById('participate-project')?.addEventListener('click', async (event) => {
  await postJson(event.currentTarget.dataset.url);
  location.reload();
});
