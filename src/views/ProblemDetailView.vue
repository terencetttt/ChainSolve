<template>
  <div class="detail-page">

    <!-- LOADING -->
    <div v-if="loading" class="empty-state">
      <div class="spinner" />
      <p>Loading from chain…</p>
    </div>

    <!-- NOT FOUND -->
    <div v-else-if="!problem" class="empty-state">
      <p>Problem not found on chain.</p>
      <RouterLink to="/archive" class="btn-ghost">← Back to archive</RouterLink>
    </div>

    <template v-else>

      <!-- BREADCRUMB -->
      <div class="breadcrumb">
        <RouterLink to="/archive" class="breadcrumb-link">Archive</RouterLink>
        <span class="breadcrumb-sep">/</span>
        <span class="mono">Case No. {{ String(problem.id).padStart(3, '0') }}</span>
      </div>

      <!-- REPORT HEAD -->
      <div class="report-head card">
        <div class="title-badges">
          <span class="badge" :class="`badge-${problem.category.toLowerCase()}`">{{ problem.category }}</span>
          <span class="badge" :class="`badge-${problem.severity.toLowerCase()}`">{{ problem.severity }}</span>
          <span class="badge" :class="`badge-${problem.difficulty.toLowerCase()}`">{{ problem.difficulty }}</span>
          <span class="badge" :class="`badge-${problem.confidence.toLowerCase()}`">{{ problem.confidence }} confidence</span>
          <span class="badge" :class="`badge-${problem.status.toLowerCase()}`">{{ problem.status }}</span>
        </div>
        <h1 class="detail-title">{{ problem.title }}</h1>
        <p class="detail-submitter mono">
          Submitted by {{ shortAddr(problem.submitter) }}
        </p>
      </div>

      <!-- ACTION BAR -->
      <div class="action-bar card">
        <button
          class="btn-ghost action-btn"
          :disabled="actionLoading === 'upvote'"
          @click="upvote"
        >
          <span>▲</span>
          <span>{{ problem.upvote_count }} upvote{{ problem.upvote_count !== 1 ? 's' : '' }}</span>
          <span v-if="actionLoading === 'upvote'" class="spinner-sm" />
        </button>

        <button
          v-if="isSubmitter && problem.status === 'OPEN'"
          class="btn-ghost action-btn"
          :disabled="actionLoading === 'solved'"
          @click="markSolved"
        >
          <span>✓</span>
          <span>Mark as solved</span>
          <span v-if="actionLoading === 'solved'" class="spinner-sm" />
        </button>

        <div class="action-spacer" />
        <span class="action-id mono">No. {{ String(problem.id).padStart(3, '0') }}</span>
      </div>

      <!-- REPORT SECTIONS -->
      <div class="card report-section">
        <p class="section-label"><span class="section-num">§</span> The problem as submitted</p>
        <p class="body-text soft pre-wrap">{{ problem.description }}</p>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">01</span> Executive summary</p>
        <p class="body-text">{{ problem.problem_summary }}</p>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">02</span> Root cause analysis</p>
        <p class="body-text">{{ problem.root_cause }}</p>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">03</span> Recommended course of action</p>
        <p class="body-text pre-wrap">{{ problem.primary_solution }}</p>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">04</span> Alternative approaches</p>
        <div class="alternatives">
          <div v-for="(alt, i) in alternatives" :key="i" class="alt-item">
            <span class="alt-marker mono">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="body-text">{{ alt }}</span>
          </div>
        </div>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">05</span> Risk assessment</p>
        <p class="body-text">{{ problem.risks }}</p>
      </div>

      <!-- RE-ANALYSIS HISTORY -->
      <div v-if="reanalysisList.length > 0" class="reanalysis-history">
        <p class="history-heading">Re-analysis history</p>
        <div
          v-for="r in reanalysisList"
          :key="r.reanalysis_num"
          class="card reanalysis-card"
        >
          <div class="reanalysis-meta">
            <span class="badge badge-research">Re-analysis {{ String(r.reanalysis_num + 1).padStart(2, '0') }}</span>
            <div class="reanalysis-badges">
              <span class="badge" :class="`badge-${r.difficulty.toLowerCase()}`">{{ r.difficulty }}</span>
              <span class="badge" :class="`badge-${r.confidence.toLowerCase()}`">{{ r.confidence }}</span>
            </div>
          </div>
          <div class="reanalysis-context">
            <p class="context-label">New context added</p>
            <p class="body-text context-text">{{ r.context_added }}</p>
          </div>
          <div>
            <p class="context-label">Updated recommendation</p>
            <p class="body-text">{{ r.primary_solution }}</p>
          </div>
        </div>
      </div>

      <!-- RE-ANALYZE FORM -->
      <div class="card reanalyze-form">
        <p class="section-label"><span class="section-num">+</span> Request re-analysis</p>
        <p class="reanalyze-hint">
          Have new information? Add context and the validators will produce an updated recommendation.
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
            <span v-if="actionLoading === 'reanalyze'">Running re-analysis…</span>
            <span v-else>Re-analyze</span>
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
  max-width: 780px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ── States ── */
.empty-state {
  text-align: center;
  padding: 88px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  color: var(--soft);
}
.spinner {
  width: 30px; height: 30px;
  border: 2px solid var(--rule);
  border-top-color: var(--forest);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.spinner-sm {
  display: inline-block;
  width: 13px; height: 13px;
  border: 2px solid var(--rule);
  border-top-color: var(--forest);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ── Breadcrumb ── */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--faint);
  padding-bottom: 4px;
}
.breadcrumb-link { color: var(--forest); font-weight: 500; }
.breadcrumb-link:hover { text-decoration: underline; }
.breadcrumb-sep { opacity: 0.5; }

/* ── Report head ── */
.report-head {
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-top: 3px solid var(--forest);
}
.title-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.detail-title {
  font-family: var(--font-display);
  font-size: clamp(24px, 4vw, 34px);
  font-weight: 700;
  color: var(--ink);
  line-height: 1.25;
}
.detail-submitter { font-size: 12px; color: var(--faint); }

/* ── Action bar ── */
.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  flex-wrap: wrap;
}
.action-btn { gap: 8px; }
.action-spacer { flex: 1; }
.action-id { font-size: 11px; color: var(--faint); }

/* ── Report sections ── */
.report-section { padding: 26px 32px; }
.body-text { font-size: 14.5px; line-height: 1.75; color: var(--ink); }
.body-text.soft { color: var(--soft); }
.pre-wrap { white-space: pre-wrap; }

.alternatives { display: flex; flex-direction: column; gap: 14px; }
.alt-item { display: flex; gap: 16px; align-items: baseline; }
.alt-marker {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--forest);
  font-weight: 500;
}

/* ── Re-analysis ── */
.reanalysis-history { display: flex; flex-direction: column; gap: 12px; }
.history-heading {
  font-family: var(--font-display);
  font-size: 19px;
  font-weight: 700;
  color: var(--ink);
  padding: 12px 0 4px;
}
.reanalysis-card { display: flex; flex-direction: column; gap: 18px; }
.reanalysis-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--rule);
}
.reanalysis-badges { display: flex; gap: 6px; }
.reanalysis-context {
  padding: 16px 18px;
  background: var(--paper);
  border-left: 2px solid var(--rule-dark);
}
.context-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--faint);
  margin-bottom: 8px;
}
.context-text { font-style: italic; color: var(--soft); font-size: 13.5px; }

/* ── Re-analyze form ── */
.reanalyze-form { display: flex; flex-direction: column; gap: 16px; }
.reanalyze-hint { font-size: 13px; color: var(--soft); }

.field-input {
  background: var(--card);
  border: 1px solid var(--rule-dark);
  padding: 12px 14px;
  color: var(--ink);
  font-family: var(--font-body);
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
  border-radius: 0;
}
.field-input:focus {
  border-color: var(--forest);
  box-shadow: 0 0 0 3px var(--forest-wash);
}
.field-input::placeholder { color: var(--faint); }
.field-textarea { resize: vertical; min-height: 110px; line-height: 1.65; }

.reanalyze-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.form-note { font-size: 12px; color: var(--faint); }
.tx-note { font-size: 11px; color: var(--faint); }
.error-msg { font-size: 13px; color: var(--red); }

@media (max-width: 600px) {
  .reanalyze-footer { flex-direction: column; align-items: stretch; }
  .report-section { padding: 22px 20px; }
}
</style>
