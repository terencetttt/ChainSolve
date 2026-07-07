<template>
  <div class="archive-page">

    <div class="archive-header">
      <div>
        <p class="archive-eyebrow">Solution archive</p>
        <h1 class="archive-title">Every problem. Every solution.</h1>
        <p class="archive-sub">
          {{ problems.length }} problem{{ problems.length !== 1 ? 's' : '' }} solved on Bradbury chain.
        </p>
      </div>
      <RouterLink to="/" class="btn-primary">Submit a problem</RouterLink>
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
        >{{ sev === '' ? 'Any severity' : sev }}</button>
      </div>
      <div class="filter-group">
        <button
          class="filter-chip"
          :class="{ 'filter-chip--active': activeStatus === 'SOLVED' }"
          @click="activeStatus = activeStatus === 'SOLVED' ? '' : 'SOLVED'"
        >Solved only</button>
      </div>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="empty-state">
      <div class="spinner" />
      <p>Fetching from Bradbury…</p>
    </div>

    <!-- EMPTY -->
    <div v-else-if="!isConnected" class="empty-state">
      <p>Connect your wallet to browse the archive.</p>
      <button class="btn-primary" @click="connect">Connect wallet</button>
    </div>

    <div v-else-if="filtered.length === 0" class="empty-state">
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
.archive-page { display: flex; flex-direction: column; gap: 34px; }

.archive-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding-bottom: 26px;
  border-bottom: 1px solid var(--rule);
}
.archive-eyebrow {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--forest);
  margin-bottom: 10px;
}
.archive-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 8px;
  line-height: 1.2;
}
.archive-sub { color: var(--soft); font-size: 14px; }

/* ── Filters ── */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-right: 14px;
  border-right: 1px solid var(--rule);
}
.filter-group:last-child { border-right: none; }

.filter-chip {
  padding: 6px 13px;
  border: 1px solid var(--rule-dark);
  background: var(--card);
  color: var(--soft);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
}
.filter-chip:hover { color: var(--ink); border-color: var(--ink); }
.filter-chip--active {
  background: var(--forest);
  border-color: var(--forest);
  color: #fff;
}

/* ── States ── */
.empty-state {
  text-align: center;
  padding: 88px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  color: var(--soft);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--rule);
  border-top-color: var(--forest);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Grid ── */
.problems-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.problem-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  cursor: pointer;
  padding: 26px;
  transition: border-color 0.2s, box-shadow 0.2s;
  text-decoration: none;
}
.problem-card:hover {
  border-color: var(--forest);
  box-shadow: 0 2px 14px rgba(22, 24, 29, 0.06);
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
  font-size: 17px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.35;
}

.pc-summary {
  font-size: 13px;
  color: var(--soft);
  line-height: 1.65;
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
  padding-top: 14px;
  border-top: 1px solid var(--rule);
}
.pc-meta { display: flex; align-items: center; gap: 12px; }
.upvote-count { font-size: 12px; color: var(--soft); font-weight: 500; }
.pc-addr { font-size: 11px; color: var(--faint); }
</style>
