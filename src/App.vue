<template>
  <div class="app">
    <!-- LETTERHEAD NAV -->
    <nav class="nav">
      <div class="nav-inner">
        <RouterLink to="/" class="nav-brand">
          <span class="brand-seal" aria-hidden="true"></span>
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
          Connect wallet
        </button>
        <div v-else class="wallet-chip">
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
      <span>ChainSolve · GenLayer Bradbury Testnet</span>
      <a href="https://explorer-bradbury.genlayer.com" target="_blank" rel="noopener">
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
/* ── RESET + TOKENS ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --paper:       #F7F6F1;
  --card:        #FFFFFF;
  --ink:         #16181D;
  --soft:        #5E6572;
  --faint:       #9AA0AA;
  --rule:        #E3E1D9;
  --rule-dark:   #C9C6BB;

  --forest:      #1D5C45;
  --forest-deep: #14432F;
  --forest-wash: #EDF3EF;

  --red:         #9B2C2C;
  --red-wash:    #F7ECEC;
  --amber:       #8A5A00;
  --amber-wash:  #F7F0DF;
  --blue:        #1E4E79;
  --blue-wash:   #EAF0F6;

  --font-display: 'Libre Caslon Text', Georgia, serif;
  --font-body:    'Inter', -apple-system, sans-serif;
  --font-mono:    'JetBrains Mono', monospace;
}

html { scroll-behavior: smooth; }

body {
  background: var(--paper);
  color: var(--ink);
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.65;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

a { color: inherit; text-decoration: none; }

::selection { background: var(--forest); color: #fff; }

/* ── NAV ────────────────────────────────────────────────────── */
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(247, 246, 241, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--rule);
}

.nav-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 28px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 36px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-seal {
  width: 12px;
  height: 12px;
  background: var(--forest);
  flex-shrink: 0;
}

.brand-name {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 19px;
  letter-spacing: 0.01em;
  color: var(--ink);
}

.nav-links {
  display: flex;
  gap: 26px;
  flex: 1;
}

.nav-link {
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.02em;
  color: var(--soft);
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}

.nav-link:hover { color: var(--ink); }
.nav-link--active { color: var(--ink); border-bottom-color: var(--forest); }

.btn-connect {
  margin-left: auto;
  padding: 9px 20px;
  background: var(--forest);
  border: 1px solid var(--forest);
  color: #fff;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.btn-connect:hover { background: var(--forest-deep); border-color: var(--forest-deep); }

.wallet-chip {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  background: var(--card);
  border: 1px solid var(--rule);
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--ink);
}

.wallet-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--forest);
  flex-shrink: 0;
}

/* ── MAIN + FOOTER ──────────────────────────────────────────── */
.main {
  max-width: 960px;
  margin: 0 auto;
  padding: 56px 28px 96px;
  min-height: calc(100vh - 64px - 56px);
}

.footer {
  border-top: 1px solid var(--rule);
  padding: 18px 28px;
  display: flex;
  justify-content: center;
  gap: 28px;
  font-size: 12px;
  letter-spacing: 0.04em;
  color: var(--faint);
}
.footer a { color: var(--faint); }
.footer a:hover { color: var(--forest); }

/* ── SHARED ─────────────────────────────────────────────────── */
.card {
  background: var(--card);
  border: 1px solid var(--rule);
  padding: 32px;
}

/* Classification stamps — small caps, hairline, square */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border: 1px solid;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  line-height: 1;
}

.badge-critical { color: var(--red);   border-color: var(--red);   background: var(--red-wash); }
.badge-high     { color: var(--amber); border-color: var(--amber); background: var(--amber-wash); }
.badge-medium   { color: var(--blue);  border-color: var(--blue);  background: var(--blue-wash); }
.badge-low      { color: var(--forest); border-color: var(--forest); background: var(--forest-wash); }

.badge-easy     { color: var(--forest); border-color: var(--forest); background: var(--forest-wash); }
.badge-moderate { color: var(--amber);  border-color: var(--amber);  background: var(--amber-wash); }
.badge-complex  { color: var(--red);    border-color: var(--red);    background: var(--red-wash); }

.badge-technical { color: var(--blue);   border-color: var(--blue);   background: var(--blue-wash); }
.badge-business  { color: var(--ink);    border-color: var(--rule-dark); background: var(--paper); }
.badge-personal  { color: var(--amber);  border-color: var(--amber);  background: var(--amber-wash); }
.badge-research  { color: var(--forest); border-color: var(--forest); background: var(--forest-wash); }

.badge-open   { color: var(--blue);   border-color: var(--blue);   background: var(--blue-wash); }
.badge-solved { color: var(--forest); border-color: var(--forest); background: var(--forest-wash); }

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 13px 30px;
  background: var(--forest);
  color: #fff;
  border: 1px solid var(--forest);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn-primary:hover:not(:disabled) { background: var(--forest-deep); border-color: var(--forest-deep); }
.btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 11px 20px;
  background: transparent;
  border: 1px solid var(--rule-dark);
  color: var(--ink);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}
.btn-ghost:hover:not(:disabled) { border-color: var(--forest); color: var(--forest); background: var(--forest-wash); }
.btn-ghost:disabled { opacity: 0.45; cursor: not-allowed; }

/* Numbered report-section header */
.section-label {
  display: flex;
  align-items: baseline;
  gap: 12px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--forest);
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--rule);
}

.section-num {
  font-family: var(--font-mono);
  font-weight: 500;
  color: var(--faint);
}

.mono { font-family: var(--font-mono); }

/* Focus visibility */
:focus-visible { outline: 2px solid var(--forest); outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
</style>
