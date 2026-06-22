<template>
  <div class="detail-page">

    <!-- LOADING -->
    <div v-if="loading" class="empty-state">
      <div class="spinner" />
      <p>Loading from chain…</p>
    </div>

    <!-- NOT FOUND -->
    <div v-else-if="!problem" class="empty-state">
      <p class="empty-icon">⬡</p>
      <p>Problem not found on chain.</p>
      <RouterLink to="/archive" class="btn-ghost">← Back to Archive</RouterLink>
    </div>

    <template v-else>

      <!-- BREADCRUMB -->
      <div class="breadcrumb">
        <RouterLink to="/archive" class="breadcrumb-link">Archive</RouterLink>
        <span class="breadcrumb-sep">/</span>
        <span>Problem #{{ problem.id }}</span>
      </div>

      <!-- TITLE SECTION -->
      <div class="title-section">
        <div class="title-badges">
          <span class="badge" :class="`badge-${problem.category.toLowerCase()}`">{{ problem.category }}</span>
          <span class="badge" :class="`badge-${problem.severity.toLowerCase()}`">{{ problem.severity }}</span>
          <span class="badge" :class="`badge-${problem.difficulty.toLowerCase()}`">{{ problem.difficulty }}</span>
          <span class="badge" :class="`badge-${problem.confidence.toLowerCase()}`">{{ problem.confidence }} CONFIDENCE</span>
          <span class="badge" :class="`badge-${problem.status.toLowerCase()}`">{{ problem.status }}</span>
        </div>
        <h1 class="detail-title">{{ problem.title }}</h1>
        <p class="detail-submitter mono">
          Submitted by {{ shortAddr(problem.submitter) }}
        </p>
      </div>

      <!-- ACTION BAR -->
      <div class="action-bar card">
        <!-- Upvote -->
        <button
          class="btn-ghost action-btn"
          :disabled="actionLoading === 'upvote'"
          @click="upvote"
        >
          <span>▲</span>
          <span>{{ problem.upvote_count }} Upvote{{ problem.upvote_count !== 1 ? 's' : '' }}</span>
          <span v-if="actionLoading === 'upvote'" class="spinner-sm" />
        </button>

        <!-- Mark Solved (submitter only) -->
        <button
          v-if="isSubmitter && problem.status === 'OPEN'"
          class="btn-ghost action-btn"
          :disabled="actionLoading === 'solved'"
          @click="markSolved"
        >
          <span>✓</span>
          <span>Mark as Solved</span>
          <span v-if="actionLoading === 'solved'" class="spinner-sm" />
        </button>

        <div class="action-spacer" />
        <span class="action-id mono">#{{ problem.id }}</span>
      </div>

      <!-- SOLUTION SECTIONS -->
      <div class="card">
        <p class="section-label">The Problem</p>
        <p class="detail-desc">{{ problem.description }}</p>
      </div>

      <div class="card highlight-card">
        <p class="section-label">AI Summary</p>
        <p class="detail-summary">{{ problem.problem_summary }}</p>
      </div>

      <div class="two-col">
        <div class="card">
          <p class="section-label">Root Cause</p>
          <p class="body-text">{{ problem.root_cause }}</p>
        </div>
        <div class="card">
          <p class="section-label">Risks</p>
          <p class="body-text">{{ problem.risks }}</p>
        </div>
      </div>

      <div class="card">
        <p class="section-label">Primary Solution</p>
        <p class="body-text solution-text">{{ problem.primary_solution }}</p>
      </div>

      <div class="card">
        <p class="section-label">Alternative Approaches</p>
        <div class="alternatives">
          <div v-for="(alt, i) in alternatives" :key="i" class="alt-item">
            <span class="alt-num">{{ i + 1 }}</span>
            <span class="body-text">{{ alt }}</span>
          </div>
        </div>
      </div>

      <!-- RE-ANALYSIS HISTORY -->
      <div v-if="reanalysisList.length > 0" class="reanalysis-history">
        <p class="section-label">Re-Analysis History</p>
        <div
          v-for="r in reanalysisList"
          :key="r.reanalysis_num"
          class="card reanalysis-card"
        >
          <div class="reanalysis-meta">
            <span class="badge badge-research">RE-ANALYSIS #{{ r.reanalysis_num + 1 }}</span>
            <div class="reanalysis-badges">
              <span class="badge" :class="`badge-${r.difficulty.toLowerCase()}`">{{ r.difficulty }}</span>
              <span class="badge" :class="`badge-${r.confidence.toLowerCase()}`">{{ r.confidence }}</span>
            </div>
          </div>
          <div class="reanalysis-context">
            <p class="section-label" style="font-size:10px">New Context Added</p>
            <p class="body-text context-text">{{ r.context_added }}</p>
          </div>
          <div>
            <p class="section-label" style="font-size:10px">Updated Solution</p>
            <p class="body-text">{{ r.primary_solution }}</p>
          </div>
        </div>
      </div>

      <!-- RE-ANALYZE FORM -->
      <div class="card reanalyze-form">
        <p class="section-label">Request Re-Analysis</p>
        <p class="reanalyze-hint">
          Have new information? Add context and AI validators will produce an updated solution.
        </p>
        <textarea
          v-model="newContext"
          class="field-input field-textarea"
          placeholder="Describe what has changed or what additional context should be considered…"
          rows="4"
        />
        <div class="reanalyze-footer">
          <p class="form-note">Re-analysis takes ~3–5 min on Bradbury.</p>
          <button
            class="btn-primary"
            :disabled="!newContext.trim() || actionLoading === 'reanalyze'"
            @click="reanalyze"
          >
            <span v-if="actionLoading === 'reanalyze'">Running Re-Analysis…</span>
            <span v-else>⬡ Re-Analyze</span>
          </button>
        </div>
        <p v-if="reanalyzeHash" class="tx-note mono">
          TX: {{ reanalyzeHash.slice(0, 16) }}… (waiting for consensus)
        </p>
        <p v-if="actionError" class="error-msg">{{ actionError }}</p>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { readContract, writeWithRetry, walletAddress, isConnected, connectWallet } from '../client'

const route   = useRoute()
const loading = ref(true)
const problem = ref<any>(null)
const reanalysisList = ref<any[]>([])
const newContext     = ref('')
const actionLoading  = ref<string>('')
const actionError    = ref('')
const reanalyzeHash  = ref('')

const problemId = computed(() => Number(route.params.id))

const isSubmitter = computed(
  () => walletAddress.value.toLowerCase() === problem.value?.submitter?.toLowerCase(),
)

const alternatives = computed(() =>
  problem.value?.alternatives
    ? problem.value.alternatives.split(' | ').map((s: string) => s.trim()).filter(Boolean)
    : [],
)

async function loadProblem() {
  loading.value = true
  try {
    if (!isConnected.value) await connectWallet()
    const data = await readContract('get_problem', [problemId.value]) as any
    problem.value = data

    // Load all re-analyses
    const count = await readContract('get_reanalysis_count', [problemId.value]) as number
    const list = []
    for (let i = 0; i < count; i++) {
      const r = await readContract('get_reanalysis', [problemId.value, i]) as any
      if (r) list.push(r)
    }
    reanalysisList.value = list
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function upvote() {
  actionError.value = ''
  actionLoading.value = 'upvote'
  try {
    await writeWithRetry('upvote_solution', [problemId.value])
    await loadProblem()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    if (!msg.includes('wallet_getSnaps')) actionError.value = msg
  } finally {
    actionLoading.value = ''
  }
}

async function markSolved() {
  actionError.value = ''
  actionLoading.value = 'solved'
  try {
    await writeWithRetry('mark_solved', [problemId.value])
    await loadProblem()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    if (!msg.includes('wallet_getSnaps')) actionError.value = msg
  } finally {
    actionLoading.value = ''
  }
}

async function reanalyze() {
  actionError.value = ''
  reanalyzeHash.value = ''
  actionLoading.value = 'reanalyze'
  try {
    await writeWithRetry(
      'reanalyze_problem',
      [problemId.value, newContext.value],
      (hash) => { reanalyzeHash.value = hash },
    )
    newContext.value = ''
    reanalyzeHash.value = ''
    await loadProblem()
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e)
    if (!msg.includes('wallet_getSnaps')) actionError.value = msg
  } finally {
    actionLoading.value = ''
  }
}

const shortAddr = (addr: string) =>
  addr ? `${addr.slice(0, 6)}…${addr.slice(-4)}` : ''

onMounted(loadProblem)
</script>

<style scoped>
.detail-page {
  max-width: 820px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ── States ── */
.empty-state {
  text-align: center;
  padding: 80px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--muted);
}
.empty-icon { font-size: 48px; }
.spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.spinner-sm {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ── Breadcrumb ── */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--muted);
}
.breadcrumb-link { color: var(--accent); }
.breadcrumb-link:hover { text-decoration: underline; }
.breadcrumb-sep { opacity: 0.4; }

/* ── Title ── */
.title-section { display: flex; flex-direction: column; gap: 12px; }
.title-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.detail-title {
  font-family: var(--font-display);
  font-size: clamp(24px, 4vw, 36px);
  font-weight: 700;
  color: var(--bright);
  line-height: 1.2;
}
.detail-submitter { font-size: 12px; color: var(--muted); }

/* ── Action Bar ── */
.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  flex-wrap: wrap;
}
.action-btn { gap: 8px; }
.action-spacer { flex: 1; }
.action-id { font-size: 11px; color: var(--muted); }

/* ── Content ── */
.highlight-card {
  background: linear-gradient(135deg, rgba(34,211,238,0.06), rgba(167,139,250,0.04));
  border-color: rgba(34,211,238,0.2);
}
.detail-desc  { font-size: 14px; color: var(--muted); line-height: 1.8; white-space: pre-wrap; }
.detail-summary { font-size: 15px; color: var(--text); line-height: 1.75; }
.body-text    { font-size: 14px; line-height: 1.8; color: var(--text); }
.solution-text { white-space: pre-wrap; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

/* ── Alternatives ── */
.alternatives { display: flex; flex-direction: column; gap: 12px; }
.alt-item { display: flex; gap: 14px; align-items: flex-start; }
.alt-num {
  flex-shrink: 0;
  width: 24px; height: 24px;
  border-radius: 50%;
  background: var(--accent-dim);
  border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: var(--accent);
}

/* ── Re-analysis history ── */
.reanalysis-history { display: flex; flex-direction: column; gap: 12px; }
.reanalysis-card { display: flex; flex-direction: column; gap: 16px; }
.reanalysis-meta { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.reanalysis-badges { display: flex; gap: 6px; }
.reanalysis-context { padding: 12px; background: rgba(0,0,0,0.2); border-radius: var(--radius-sm); border: 1px solid var(--border); }
.context-text { font-style: italic; color: var(--muted); font-size: 13px; }

/* ── Re-analyze form ── */
.reanalyze-form { display: flex; flex-direction: column; gap: 16px; }
.reanalyze-hint { font-size: 13px; color: var(--muted); }

.field-input {
  background: rgba(2, 8, 23, 0.6);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 11px 14px;
  color: var(--text);
  font-family: var(--font-body);
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s;
  width: 100%;
}
.field-input:focus { border-color: var(--accent); }
.field-input::placeholder { color: var(--muted); opacity: 0.6; }
.field-textarea { resize: vertical; min-height: 100px; line-height: 1.6; }

.reanalyze-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.form-note { font-size: 12px; color: var(--muted); }
.tx-note { font-size: 11px; color: var(--muted); }
.error-msg { font-size: 13px; color: var(--danger); }

@media (max-width: 600px) {
  .two-col { grid-template-columns: 1fr; }
  .reanalyze-footer { flex-direction: column; align-items: stretch; }
}
</style>
