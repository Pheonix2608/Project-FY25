(function() {
  const chat = document.getElementById('chat');
  const input = document.getElementById('message');
  const sendBtn = document.getElementById('send');
  const apiBaseInput = document.getElementById('api-base');
  const apiKeyInput = document.getElementById('api-key');
  const saveBtn = document.getElementById('save-config');

  // Load saved config
  const saved = JSON.parse(localStorage.getItem('remote_chat_config') || '{}');
  if (saved.base) apiBaseInput.value = saved.base;
  if (saved.key) apiKeyInput.value = saved.key;

  function saveConfig() {
    const cfg = { base: apiBaseInput.value.trim(), key: apiKeyInput.value.trim() };
    localStorage.setItem('remote_chat_config', JSON.stringify(cfg));
    appendBot('Configuration saved.');
  }

  function appendUser(text) {
    const el = document.createElement('div');
    el.className = 'message user';
    el.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
  }

  function appendBot(text) {
    const el = document.createElement('div');
    el.className = 'message bot';
    el.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
    chat.appendChild(el);
    chat.scrollTop = chat.scrollHeight;
  }

  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function normalizeBase(url) {
    if (!url) return '';
    let u = url.trim();
    u = u.replace(/\/$/, '');
    if (!/^https?:\/\//i.test(u)) {
      u = 'http://' + u;
    }
    return u;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    appendUser(text);
    input.value = '';

    let base = apiBaseInput.value.trim();
    let key = apiKeyInput.value.trim();

    if (!base || !key) {
      const cfg = JSON.parse(localStorage.getItem('remote_chat_config') || '{}');
      base = base || (cfg.base || '');
      key = key || (cfg.key || '');
      if (base) apiBaseInput.value = cfg.base;
      if (key) apiKeyInput.value = cfg.key;
    }

    base = normalizeBase(base);

    if (!base || !key) {
      appendBot('Please set API Base URL and API Key.');
      return;
    }

    try {
      const res = await fetch(`${base}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': key
        },
        body: JSON.stringify({ message: text })
      });
      if (!res.ok) {
        let errText = `HTTP ${res.status}`;
        try {
          const errJson = await res.json();
          if (errJson && (errJson.error || errJson.message)) {
            errText += ` - ${errJson.error || errJson.message}`;
          }
        } catch (_) {
          try {
            const txt = await res.text();
            if (txt) errText += ` - ${txt}`;
          } catch (_) {}
        }
        appendBot(`Error: ${errText}`);
        return;
      }
      const data = await res.json();
      appendBot(data.response || '(no response)');
    } catch (e) {
      appendBot(`Network error. Check API Base URL and connectivity. Details: ${e && e.message ? e.message : e}`);
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
  saveBtn.addEventListener('click', saveConfig);
  apiBaseInput.addEventListener('blur', saveConfig);
  apiKeyInput.addEventListener('blur', saveConfig);
})();