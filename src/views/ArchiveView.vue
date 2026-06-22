<template>
  <div class="archive-page">

    <div class="archive-header">
      <div>
        <p class="section-label">Solution Archive</p>
        <h1 class="archive-title">Every Problem. Every Solution.</h1>
        <p class="archive-sub">
          {{ problems.length }} problem{{ problems.length !== 1 ? 's' : '' }} solved on Bradbury chain.
        </p>
      </div>
      <RouterLink to="/" class="btn-primary">+ Submit Problem</RouterLink>
    </div>

    <!-- FILTERS -->
    <div class="filters">
      <div class="filter-group">
        <button
          v-for="cat in categories"
          :key="cat"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeCategory === cat }"
          @click="activeCategory = activeCategory === cat ? '' : cat"
        >{{ cat === '' ? 'All' : cat }}</button>
      </div>
      <div class="filter-group">
        <button
          v-for="sev in severities"
          :key="sev"
          class="filter-chip"
          :class="{ 'filter-chip--active': activeSeverity === sev }"
          @click="activeSeverity = activeSeverity === sev ? '' : sev"
        >{{ sev === '' ? 'Any Severity' : sev }}</button>
      </div>
      <div class="filter-group">
        <button
          class="filter-chip"
          :class="{ 'filter-chip--active': activeStatus === 'SOLVED' }"
          @click="activeStatus = activeStatus === 'SOLVED' ? '' : 'SOLVED'"
        >✓ Solved Only</button>
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="empty-state">
      <div class="spinner" />
      <p>Fetching from Bradbury…</p>
    </div>

    <!-- EMPTY -->
    <div v-else-if="!isConnected" class="empty-state">
      <p class="empty-icon">⬡</p>
      <p>Connect your wallet to browse the archive.</p>
      <button class="btn-primary" @click="connect">Connect Wallet</button>
    </div>

    <div v-else-if="filtered.length === 0" class="empty-state">
      <p class="empty-icon">🔍</p>
      <p>No problems match your filters.</p>
    </div>

    <!-- GRID -->
    <div v-else class="problems-grid">
      <RouterLink
        v-for="p in filtered"
        :key="p.id"
        :to="`/problem/${p.id}`"
        class="problem-card card"
      >
        <div class="pc-top">
          <div class="pc-badges">
            <span class="badge" :class="`badge-${p.category.toLowerCase()}`">{{ p.category }}</span>
            <span class="badge" :class="`badge-${p.severity.toLowerCase()}`">{{ p.severity }}</span>
          </div>
          <span class="badge" :class="`badge-${p.status.toLowerCase()}`">{{ p.status }}</span>
        </div>

        <h3 class="pc-title">{{ p.title }}</h3>
        <p class="pc-summary">{{ p.problem_summary }}</p>

        <div class="pc-footer">
          <div class="pc-meta">
            <span class="badge" :class="`badge-${p.difficulty.toLowerCase()}`">{{ p.difficulty }}</span>
            <span class="upvote-count">▲ {{ p.upvote_count }}</span>
          </div>
          <span class="pc-addr mono">{{ shortAddr(p.submitter) }}</span>
        </div>
      </RouterLink>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { readContract, isConnected, connectWallet } from '../client'

const problems = ref<any[]>([])
const loading  = ref(false)

const categories   = ['', 'TECHNICAL', 'BUSINESS', 'PERSONAL', 'RESEARCH']
const severities   = ['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
const activeCategory = ref('')
const activeSeverity = ref('')
const activeStatus   = ref('')

const filtered = computed(() =>
  problems.value
    .filter(p => !activeCategory.value || p.category === activeCategory.value)
    .filter(p => !activeSeverity.value || p.severity  === activeSeverity.value)
    .filter(p => !activeStatus.value   || p.status    === activeStatus.value)
    .slice()
    .reverse()
)

async function load() {
  if (!isConnected.value) return
  loading.value = true
  try {
    const data = await readContract('get_all_problems') as any[]
    problems.value = data ?? []
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function connect() {
  try { await connectWallet(); await load() } catch {}
}

onMounted(async () => {
  if (isConnected.value) await load()
})

const shortAddr = (addr: string) =>
  addr ? `${addr.slice(0, 6)}…${addr.slice(-4)}` : ''
</script>

<style scoped>
.archive-page { display: flex; flex-direction: column; gap: 32px; }

.archive-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.archive-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--bright);
  margin: 8px 0 6px;
}
.archive-sub { color: var(--muted); font-size: 14px; }

/* ── Filters ── */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-right: 12px;
  border-right: 1px solid var(--border);
}
.filter-group:last-child { border-right: none; }

.filter-chip {
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.filter-chip:hover { color: var(--text); border-color: var(--muted); }
.filter-chip--active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
}

/* ── States ── */
.empty-state {
  text-align: center;
  padding: 80px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--muted);
}
.empty-icon { font-size: 48px; }

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Problem Grid ── */
.problems-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.problem-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
  text-decoration: none;
}
.problem-card:hover {
  border-color: var(--border-h);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(34,211,238,0.06);
}

.pc-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.pc-badges { display: flex; gap: 6px; flex-wrap: wrap; }

.pc-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  color: var(--bright);
  line-height: 1.35;
}

.pc-summary {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.pc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}
.pc-meta { display: flex; align-items: center; gap: 10px; }
.upvote-count { font-size: 12px; color: var(--muted); font-weight: 500; }
.pc-addr { font-size: 11px; color: var(--muted); }
</style>
