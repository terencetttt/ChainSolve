<template>
  <div class="app">
    <!-- NAV -->
    <nav class="nav">
      <div class="nav-inner">
        <RouterLink to="/" class="nav-brand">
          <span class="brand-hex">⬡</span>
          <span class="brand-name">ChainSolve</span>
        </RouterLink>

        <div class="nav-links">
          <RouterLink to="/" class="nav-link" active-class="nav-link--active" exact>
            Submit
          </RouterLink>
          <RouterLink to="/archive" class="nav-link" active-class="nav-link--active">
            Archive
          </RouterLink>
        </div>

        <button v-if="!isConnected" class="btn-connect" @click="connect">
          Connect Wallet
        </button>
        <div v-else class="wallet-pill">
          <span class="wallet-dot" />
          {{ shortAddr }}
        </div>
      </div>
    </nav>

    <!-- PAGE -->
    <main class="main">
      <RouterView />
    </main>

    <!-- FOOTER -->
    <footer class="footer">
      <span>ChainSolve &mdash; Powered by GenLayer Bradbury</span>
      <a :href="`https://genlayer-explorer.vercel.app`" target="_blank" rel="noopener">
        Explorer ↗
      </a>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { connectWallet, walletAddress, isConnected } from './client'

const shortAddr = computed(() =>
  walletAddress.value
    ? `${walletAddress.value.slice(0, 6)}…${walletAddress.value.slice(-4)}`
    : '',
)

async function connect() {
  try {
    await connectWallet()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Connection failed')
  }
}
</script>

<style>
/* ── GLOBAL RESET + TOKENS ─────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:         #020817;
  --surface:    #0f172a;
  --card:       #1a2744;
  --border:     rgba(34, 211, 238, 0.12);
  --border-h:   rgba(34, 211, 238, 0.35);
  --accent:     #22d3ee;
  --accent-dim: rgba(34, 211, 238, 0.08);
  --violet:     #a78bfa;
  --text:       #e2e8f0;
  --muted:      #64748b;
  --bright:     #f8fafc;
  --success:    #10b981;
  --warn:       #f59e0b;
  --danger:     #ef4444;
  --info:       #60a5fa;

  --font-display: 'Space Grotesk', sans-serif;
  --font-body:    'Inter', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;

  --radius:   10px;
  --radius-sm: 6px;
}

html { scroll-behavior: smooth; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.6;
  min-height: 100vh;
}

a { color: inherit; text-decoration: none; }

/* ── NAV ──────────────────────────────────────────────────── */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(2, 8, 23, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.nav-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 18px;
  color: var(--bright);
}

.brand-hex {
  color: var(--accent);
  font-size: 22px;
  line-height: 1;
}

.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-link {
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  color: var(--muted);
  transition: color 0.15s, background 0.15s;
}

.nav-link:hover { color: var(--text); background: var(--accent-dim); }
.nav-link--active { color: var(--accent); background: var(--accent-dim); }

.btn-connect {
  margin-left: auto;
  padding: 8px 18px;
  background: transparent;
  border: 1px solid var(--accent);
  border-radius: var(--radius-sm);
  color: var(--accent);
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.btn-connect:hover { background: var(--accent); color: var(--bg); }

.wallet-pill {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  background: var(--accent-dim);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--accent);
}

.wallet-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
  flex-shrink: 0;
}

/* ── MAIN + FOOTER ────────────────────────────────────────── */
.main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 24px 80px;
  min-height: calc(100vh - 60px - 52px);
}

.footer {
  border-top: 1px solid var(--border);
  padding: 14px 24px;
  display: flex;
  justify-content: center;
  gap: 24px;
  font-size: 12px;
  color: var(--muted);
}
.footer a { color: var(--muted); }
.footer a:hover { color: var(--accent); }

/* ── SHARED UTILITY CLASSES ───────────────────────────────── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.badge-critical { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.badge-high     { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-medium   { background: rgba(96,165,250,0.15); color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }
.badge-low      { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }

.badge-easy     { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.badge-moderate { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.badge-complex  { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

.badge-technical { background: rgba(96,165,250,0.15); color: #60a5fa; border: 1px solid rgba(96,165,250,0.3); }
.badge-business  { background: rgba(167,139,250,0.15); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }
.badge-personal  { background: rgba(244,114,182,0.15); color: #f472b6; border: 1px solid rgba(244,114,182,0.3); }
.badge-research  { background: rgba(34,211,238,0.15); color: #22d3ee; border: 1px solid rgba(34,211,238,0.3); }

.badge-open   { background: rgba(34,211,238,0.1); color: #22d3ee; border: 1px solid rgba(34,211,238,0.3); }
.badge-solved { background: rgba(16,185,129,0.1); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 28px;
  background: var(--accent);
  color: var(--bg);
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
}
.btn-primary:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}
.btn-ghost:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
.btn-ghost:disabled { opacity: 0.4; cursor: not-allowed; }

.section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 8px;
}

.mono { font-family: var(--font-mono); }
</style>
