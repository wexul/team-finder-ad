function csrfToken() {
  const item = document.cookie.split(';').map(v => v.trim()).find(v => v.startsWith('csrftoken='));
  return item ? decodeURIComponent(item.split('=')[1]) : '';
}

const input = document.getElementById('skill-input');
const addBtn = document.getElementById('skill-add-btn');
const suggestions = document.getElementById('skill-suggestions');

async function addSkill(payload) {
  const formData = new FormData();
  Object.entries(payload).forEach(([key, value]) => formData.append(key, value));
  const response = await fetch(input.dataset.addUrl, {method: 'POST', headers: {'X-CSRFToken': csrfToken()}, body: formData});
  if (!response.ok) return;
  location.reload();
}

let timer = null;
input?.addEventListener('input', () => {
  clearTimeout(timer);
  const q = input.value.trim();
  if (!q) { suggestions.innerHTML = ''; return; }
  timer = setTimeout(async () => {
    const response = await fetch(`${input.dataset.suggestUrl}?q=${encodeURIComponent(q)}`);
    const data = await response.json();
    suggestions.innerHTML = '';
    data.forEach(skill => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = skill.name;
      button.addEventListener('click', () => addSkill({skill_id: skill.id}));
      suggestions.appendChild(button);
    });
    const createButton = document.createElement('button');
    createButton.type = 'button';
    createButton.textContent = `Создать «${q}»`;
    createButton.addEventListener('click', () => addSkill({name: q}));
    suggestions.appendChild(createButton);
  }, 250);
});

addBtn?.addEventListener('click', () => {
  const value = input.value.trim();
  if (value) addSkill({name: value});
});

document.querySelectorAll('.remove-skill').forEach(button => {
  button.addEventListener('click', async () => {
    const response = await fetch(button.dataset.url, {method: 'POST', headers: {'X-CSRFToken': csrfToken()}});
    if (response.ok) location.reload();
  });
});
