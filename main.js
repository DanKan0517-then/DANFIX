/* ── main.js — DanFix Frontend Logic ──────────────────────────── */
'use strict';

// ── Element refs ────────────────────────────────────────────────────
const inputEl       = document.getElementById('input-text');
const charCountEl   = document.getElementById('char-count');
const analyzeBtn    = document.getElementById('analyze-btn');
const clearBtn      = document.getElementById('clear-btn');
const demoBtn       = document.getElementById('demo-btn');
const uploadZone    = document.getElementById('upload-zone');
const fileInput     = document.getElementById('file-input');
const fileNameTag   = document.getElementById('file-name-tag');
const outputSection = document.getElementById('output-section');
const resultsCard   = document.getElementById('results-card');
const toastContainer = document.getElementById('toast-container');

const stages = {
  lexer:    document.getElementById('stage-lexer'),
  parser:   document.getElementById('stage-parser'),
  semantic: document.getElementById('stage-semantic'),
  reporter: document.getElementById('stage-reporter'),
};

let uploadedFile = null;

// ── Utilities ────────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  toastContainer.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function setStage(active) {
  const order = ['lexer', 'parser', 'semantic', 'reporter'];
  const idx   = order.indexOf(active);
  order.forEach((s, i) => {
    stages[s].classList.toggle('active', i === idx);
    stages[s].classList.toggle('done',   i < idx);
  });
}

function resetStages() {
  Object.values(stages).forEach(s => {
    s.classList.remove('active', 'done');
  });
}

function setLoading(on) {
  analyzeBtn.classList.toggle('loading', on);
  analyzeBtn.disabled = on;
}

// ── Character counter ────────────────────────────────────────────────
inputEl.addEventListener('input', () => {
  charCountEl.textContent = `${inputEl.value.length.toLocaleString()} / 50,000 chars`;
});

// ── File upload ──────────────────────────────────────────────────────
uploadZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => {
  const f = e.target.files[0];
  if (!f) return;
  uploadedFile = f;
  fileNameTag.textContent = `📄 ${f.name}`;
  fileNameTag.style.display = 'inline-block';
});

uploadZone.addEventListener('dragover', e => {
  e.preventDefault();
  uploadZone.classList.add('drag-over');
});
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (!f) return;
  uploadedFile = f;
  fileNameTag.textContent = `📄 ${f.name}`;
  fileNameTag.style.display = 'inline-block';
});

// ── Demo button ──────────────────────────────────────────────────────
demoBtn.addEventListener('click', async () => {
  try {
    const r = await fetch('/demo');
    const d = await r.json();
    inputEl.value = d.text;
    charCountEl.textContent = `${d.text.length.toLocaleString()} / 50,000 chars`;
    uploadedFile = null;
    fileNameTag.style.display = 'none';
    toast('Demo text loaded! ✨', 'success');
  } catch {
    toast('Could not load demo.', 'error');
  }
});

// ── Clear button ─────────────────────────────────────────────────────
clearBtn.addEventListener('click', () => {
  inputEl.value = '';
  charCountEl.textContent = '0 / 50,000 chars';
  uploadedFile = null;
  fileNameTag.style.display = 'none';
  outputSection.innerHTML = '';
  if (resultsCard) resultsCard.style.display = 'none';
  resetStages();
});

// ── Analyse ──────────────────────────────────────────────────────────
analyzeBtn.addEventListener('click', runAnalysis);

async function runAnalysis() {
  const text = inputEl.value.trim();
  if (!text && !uploadedFile) {
    toast('Please enter some text first!', 'error');
    return;
  }

  setLoading(true);
  resetStages();

  try {
    // Animate through pipeline stages
    const stageKeys = ['lexer', 'parser', 'semantic', 'reporter'];
    for (let i = 0; i < stageKeys.length; i++) {
      setStage(stageKeys[i]);
      await sleep(400);
    }

    let response;
    if (uploadedFile) {
      const fd = new FormData();
      fd.append('file', uploadedFile);
      response = await fetch('/analyse', { method: 'POST', body: fd });
    } else {
      response = await fetch('/analyse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
    }

    if (!response.ok) throw new Error('Server error');
    const data = await response.json();

    // Mark all done
    stageKeys.forEach(k => {
      stages[k].classList.remove('active');
      stages[k].classList.add('done');
    });

    renderResults(data);
    toast(`Found ${data.stats.total_errors} issue(s) ✅`, data.stats.total_errors > 0 ? 'error' : 'success');

  } catch (err) {
    toast('Analysis failed — is the server running?', 'error');
    resetStages();
  } finally {
    setLoading(false);
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Render results ───────────────────────────────────────────────────
function renderResults(data) {
  if (resultsCard) resultsCard.style.display = 'block';

  outputSection.innerHTML = `
    ${renderStats(data.stats)}
    <div class="tabs">
      <button class="tab-btn active" data-tab="annotated">📝 Annotated</button>
      <button class="tab-btn" data-tab="corrected">✅ Corrected</button>
      <button class="tab-btn" data-tab="errors">🚨 Errors (${data.stats.total_errors})</button>
      <button class="tab-btn" data-tab="tokens">🔡 Tokens</button>
      <button class="tab-btn" data-tab="ast">🌳 AST</button>
    </div>
    <div id="tab-annotated" class="tab-pane active">${renderAnnotated(data)}</div>
    <div id="tab-corrected" class="tab-pane">${renderCorrected(data)}</div>
    <div id="tab-errors"    class="tab-pane">${renderErrors(data.errors)}</div>
    <div id="tab-tokens"    class="tab-pane">${renderTokens(data.tokens)}</div>
    <div id="tab-ast"       class="tab-pane">${renderAST(data.ast)}</div>
  `;

  // Tab switching
  outputSection.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      outputSection.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      outputSection.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
    });
  });

  resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderStats(s) {
  return `<div class="stats-grid">
    <div class="stat-card stat-errors">
      <div class="stat-value">${s.total_errors}</div>
      <div class="stat-label">Total Errors</div>
    </div>
    <div class="stat-card stat-spell">
      <div class="stat-value">${s.spelling_errors}</div>
      <div class="stat-label">Spelling</div>
    </div>
    <div class="stat-card stat-grammar">
      <div class="stat-value">${s.grammar_errors}</div>
      <div class="stat-label">Grammar</div>
    </div>
    <div class="stat-card stat-words">
      <div class="stat-value">${s.word_count}</div>
      <div class="stat-label">Words</div>
    </div>
    <div class="stat-card stat-sents">
      <div class="stat-value">${s.sentence_count}</div>
      <div class="stat-label">Sentences</div>
    </div>
    <div class="stat-card stat-unique">
      <div class="stat-value">${s.unique_words}</div>
      <div class="stat-label">Unique Words</div>
    </div>
  </div>`;
}

function renderAnnotated(data) {
  let html = escapeHtml(data.original_text);

  // Sort by position descending to replace without offset shift
  const sorted = [...data.errors].sort((a, b) => (b.position || 0) - (a.position || 0));

  sorted.forEach(e => {
    if (!e.word) return;
    const cls   = e.type === 'SPELLING_ERROR' ? 'spell-error' : 'grammar-error';
    const esc   = escapeHtml(e.word);
    const title = escapeHtml(e.message || '');
    html = html.replace(
      esc,
      `<mark class="${cls}" title="${title}">${esc}</mark>`
    );
  });

  return `<div class="annotated-text">${html}</div>`;
}

function renderCorrected(data) {
  return `<div class="corrected-text">${escapeHtml(data.corrected_text)}</div>`;
}

function renderErrors(errors) {
  if (!errors.length) return '<p style="text-align:center;padding:30px;color:#64748B;font-weight:700;">🎉 No errors found!</p>';

  return `<div class="error-list">${errors.map(e => `
    <div class="error-item">
      <div class="error-top">
        <span class="error-word">${escapeHtml(e.word || '—')}</span>
        <span class="error-type-badge ${e.type === 'SPELLING_ERROR' ? 'badge-spell' : 'badge-grammar'}">
          ${e.type === 'SPELLING_ERROR' ? '🔴 Spelling' : '🟡 Grammar'}
        </span>
      </div>
      <div class="error-msg">${escapeHtml(e.message || '')}</div>
      ${e.suggestions && e.suggestions.length ? `
        <div class="error-suggestions">
          <span style="font-weight:800;font-size:14px;color:#64748B;">Suggestions:</span>
          ${e.suggestions.map(s => `<button class="suggestion-pill" onclick="applySuggestion('${escapeHtml(e.word || '')}','${escapeHtml(s)}')">${escapeHtml(s)}</button>`).join('')}
        </div>` : ''}
    </div>`).join('')}</div>`;
}

function renderTokens(tokens) {
  if (!tokens || !tokens.length) return '<p style="padding:20px;font-weight:700;">No tokens available.</p>';
  return `<div class="token-table-wrap">
    <table class="token-table">
      <thead><tr><th>#</th><th>Type</th><th>Value</th><th>Position</th></tr></thead>
      <tbody>${tokens.map((t, i) => `
        <tr>
          <td>${i + 1}</td>
          <td><span class="token-type-chip tt-${t.type}">${t.type}</span></td>
          <td><code>${escapeHtml(t.value)}</code></td>
          <td>${t.pos}</td>
        </tr>`).join('')}
      </tbody>
    </table>
  </div>`;
}

function renderAST(ast) {
  function walk(node, depth) {
    const indent = '  '.repeat(depth);
    const toks   = node.tokens && node.tokens.length
      ? ` [${node.tokens.map(t => `"${t.value}"`).join(', ')}]`
      : '';
    let out = `${indent}${node.type}${toks}\n`;
    (node.children || []).forEach(c => { out += walk(c, depth + 1); });
    return out;
  }
  return `<div class="ast-tree">${escapeHtml(walk(ast, 0))}</div>`;
}

// ── Apply suggestion ─────────────────────────────────────────────────
window.applySuggestion = function(word, suggestion) {
  inputEl.value = inputEl.value.replace(new RegExp(`\\b${escapeRegex(word)}\\b`), suggestion);
  toast(`Applied: "${word}" → "${suggestion}"`, 'success');
};

// ── Helpers ──────────────────────────────────────────────────────────
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
