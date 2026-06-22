<template>
  <div class="submit-page">

    <!-- HERO -->
    <div class="hero">
      <div class="hero-grid" aria-hidden="true" />
      <p class="hero-eyebrow">Decentralized AI Resolution</p>
      <h1 class="hero-title">What's your <span class="hero-accent">problem?</span></h1>
      <p class="hero-sub">
        Submit any problem. Multiple independent AI validators reach consensus.
        Solution sealed on Bradbury chain — permanently.
      </p>
    </div>

    <!-- FORM CARD -->
    <div v-if="!txHash" class="card form-card">
      <div class="field">
        <label class="field-label">Problem Title</label>
        <input
          v-model="form.title"
          class="field-input"
          placeholder="e.g. My API keeps timing out under load"
          maxlength="120"
        />
      </div>

      <div class="field-row">
        <div class="field">
          <label class="field-label">Category</label>
          <select v-model="form.category" class="field-input">
            <option value="TECHNICAL">⚙️ Technical</option>
            <option value="BUSINESS">📊 Business</option>
            <option value="PERSONAL">🧠 Personal</option>
            <option value="RESEARCH">🔬 Research</option>
          </select>
        </div>
        <div class="field">
          <label class="field-label">Severity</label>
          <select v-model="form.severity" class="field-input">
            <option value="CRITICAL">🔴 Critical</option>
            <option value="HIGH">🟠 High</option>
            <option value="MEDIUM">🔵 Medium</option>
            <option value="LOW">🟢 Low</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label class="field-label">Describe the Problem</label>
        <textarea
          v-model="form.description"
          class="field-input field-textarea"
          placeholder="Give as much context as possible — the more detail you provide, the better the AI solution will be."
          rows="6"
        />
      </div>

      <div class="form-footer">
        <p class="form-note">
          AI consensus takes ~3–5 min on Bradbury. Do not close this tab.
        </p>
        <button
          class="btn-primary btn-submit"
          :disabled="!canSubmit || submitting"
          @click="submit"
        >
          {{ submitting ? 'Submitting…' : '⬡ Solve It on Chain' }}
        </button>
      </div>

      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>

    <!-- TX STATUS TRACKER -->
    <div v-if="txHash && !solution" class="card status-card">
      <p class="section-label">AI Validators Working</p>
      <h2 class="status-title">Reaching Consensus…</h2>

      <div class="status-track">
        <div
          v-for="(stage, i) in stages"
          :key="stage.key"
          class="stage"
          :class="{
            'stage--done':    stageIndex > i,
            'stage--active':  stageIndex === i,
            'stage--pending': stageIndex < i,
          }"
        >
          <div class="stage-dot">
            <span v-if="stageIndex > i">✓</span>
            <span v-else-if="stageIndex === i" class="pulse" />
          </div>
          <div class="stage-info">
            <span class="stage-name">{{ stage.label }}</span>
            <span class="stage-desc">{{ stage.desc }}</span>
          </div>
          <div v-if="i < stages.length - 1" class="stage-line" />
        </div>
      </div>

      <div class="status-meta">
        <span class="mono">TX: {{ shortHash }}</span>
        <span>Elapsed: {{ elapsed }}</span>
      </div>
    </div>

    <!-- SOLUTION REVEAL -->
    <div v-if="solution" class="solution-wrap">
      <div class="solution-header card">
        <div class="solution-badges">
          <span class="badge" :class="`badge-${solution.difficulty.toLowerCase()}`">
            {{ solution.difficulty }}
          </span>
          <span class="badge" :class="`badge-${solution.confidence.toLowerCase()}`">
            {{ solution.confidence }} CONFIDENCE
          </span>
          <span class="badge badge-solved">✓ SEALED ON CHAIN</span>
        </div>
        <h2 class="solution-title">{{ solution.title }}</h2>
        <p class="solution-summary">{{ solution.problem_summary }}</p>
        <div class="solution-actions">
          <RouterLink :to="`/problem/${solution.id}`" class="btn-primary">
            View Full Solution →
          </RouterLink>
          <RouterLink to="/archive" class="btn-ghost">Browse Archive</RouterLink>
        </div>
      </div>

      <div class="solution-grid">
        <div class="card solution-section">
          <p class="section-label">Root Cause</p>
          <p>{{ solution.root_cause }}</p>
        </div>
        <div class="card solution-section">
          <p class="section-label">Risks</p>
          <p>{{ solution.risks }}</p>
        </div>
      </div>

      <div class="card solution-section">
        <p class="section-label">Primary Solution</p>
        <p class="solution-primary">{{ solution.primary_solution }}</p>
      </div>

      <div class="card solution-section">
        <p class="section-label">Alternative Approaches</p>
        <div class="alternatives">
          <div
            v-for="(alt, i) in alternatives"
            :key="i"
            class="alt-item"
          >
            <span class="alt-num">{{ i + 1 }}</span>
            <span>{{ alt }}</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { writeWithRetry, readContract, isConnected, connectWallet } from '../client'

const form = ref({ title: '', category: 'TECHNICAL', severity: 'MEDIUM', description: '' })
const submitting = ref(false)
const error = ref('')
const txHash = ref('')
const solution = ref<any>(null)

const canSubmit = computed(
  () => form.value.title.trim().length > 3 && form.value.description.trim().length > 10,
)

// ── TX status stages ──────────────────────────────────────────
const stages = [
  { key: 'pending',    label: 'Submitted',         desc: 'Transaction broadcast' },
  { key: 'proposing', label: 'Validators Selected', desc: 'Leader chosen' },
  { key: 'committing',label: 'Committing',          desc: 'Validators submitting' },
  { key: 'revealing', label: 'Revealing',           desc: 'Results surfacing' },
  { key: 'accepted',  label: 'Accepted',            desc: 'Solution locked on-chain' },
]

const stageIndex = ref(0)
const secondsElapsed = ref(0)

const elapsed = computed(() => {
  const m = Math.floor(secondsElapsed.value / 60)
  const s = secondsElapsed.value % 60
  return `${m}:${s.toString().padStart(2, '0')}`
})

const shortHash = computed(() =>
  txHash.value ? `${txHash.value.slice(0, 10)}…${txHash.value.slice(-6)}` : '',
)

let timer: ReturnType<typeof setInterval> | null = null

function startTimer() {
  secondsElapsed.value = 0
  stageIndex.value = 0
  timer = setInterval(() => {
    secondsElapsed.value++
    // Advance stages based on typical Bradbury timing
    if (secondsElapsed.value === 20)  stageIndex.value = 1
    if (secondsElapsed.value === 60)  stageIndex.value = 2
    if (secondsElapsed.value === 120) stageIndex.value = 3
  }, 1000)
}

function stopTimer() {
  if (timer) { clearInterval(timer); timer = null }
}

onUnmounted(stopTimer)

// ── Submit ────────────────────────────────────────────────────
async function submit() {
  error.value = ''
  if (!isConnected.value) {
    try { await connectWallet() } catch { error.value = 'Please connect your wallet first.'; return }
  }

  submitting.value = true
  try {
    startTimer()
    const result = await writeWithRetry(
      'solve_problem',
      [form.value.title, form.value.description, form.value.category, form.value.severity],
      (hash) => { txHash.value = hash },
    )
    stopTimer()
    stageIndex.value = 4

    // Small delay so user sees the "Accepted" stage
    await new Promise(r => setTimeout(r, 800))

    // Fetch solution from chain
    const count = await readContract('get_problem_count') as number
    const data = await readContract('get_problem', [count - 1]) as any
    solution.value = data
  } catch (e: unknown) {
    stopTimer()
    const msg = e instanceof Error ? e.message : String(e)
    if (!msg.includes('wallet_getSnaps')) error.value = `Error: ${msg}`
    txHash.value = ''
  } finally {
    submitting.value = false
  }
}

const alternatives = computed(() =>
  solution.value?.alternatives
    ? solution.value.alternatives.split(' | ').map((s: string) => s.trim()).filter(Boolean)
    : [],
)
</script>

<style scoped>
.submit-page { max-width: 780px; margin: 0 auto; }

/* ── Hero ── */
.hero {
  position: relative;
  text-align: center;
  padding: 56px 0 48px;
  overflow: hidden;
}
.hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(34,211,238,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34,211,238,0.04) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 80%);
}
.hero-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 16px;
}
.hero-title {
  font-family: var(--font-display);
  font-size: clamp(36px, 6vw, 56px);
  font-weight: 700;
  color: var(--bright);
  line-height: 1.1;
  margin-bottom: 20px;
}
.hero-accent { color: var(--accent); }
.hero-sub {
  max-width: 520px;
  margin: 0 auto;
  color: var(--muted);
  font-size: 15px;
  line-height: 1.7;
}

/* ── Form ── */
.form-card { display: flex; flex-direction: column; gap: 22px; }

.field { display: flex; flex-direction: column; gap: 8px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.field-label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
}

.field-input {
  background: rgba(2, 8, 23, 0.6);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 11px 14px;
  color: var(--text);
  font-family: var(--font-body);
  font-size: 14px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
  appearance: none;
}
.field-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.field-input::placeholder { color: var(--muted); opacity: 0.6; }
.field-textarea { resize: vertical; min-height: 140px; line-height: 1.6; }

select.field-input { cursor: pointer; }
select.field-input option { background: #0f172a; }

.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-top: 4px;
}
.form-note { font-size: 12px; color: var(--muted); max-width: 300px; }
.btn-submit { padding: 13px 36px; font-size: 15px; }
.error-msg { color: var(--danger); font-size: 13px; }

/* ── Status Tracker ── */
.status-card { margin-top: 8px; }
.status-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  color: var(--bright);
  margin-bottom: 32px;
}
.status-track {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin-bottom: 28px;
  position: relative;
}
.stage {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 0 14px;
  align-items: start;
  position: relative;
}
.stage-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
  background: var(--surface);
  border: 2px solid var(--border);
  color: var(--muted);
  transition: all 0.3s;
}
.stage--done .stage-dot  { background: var(--success); border-color: var(--success); color: white; }
.stage--active .stage-dot{ background: var(--accent-dim); border-color: var(--accent); color: var(--accent); }

.pulse {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 1.2s infinite;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%       { transform: scale(1.5); opacity: 0.5; }
}

.stage-info {
  padding: 8px 0 24px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stage-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
}
.stage--active .stage-name { color: var(--accent); }
.stage--done .stage-name   { color: var(--success); }
.stage--pending .stage-name{ color: var(--muted); }
.stage-desc { font-size: 12px; color: var(--muted); }

.stage-line {
  position: absolute;
  left: 17px;
  top: 36px;
  width: 2px;
  height: calc(100% - 12px);
  background: var(--border);
}
.stage--done .stage-line { background: var(--success); }

.status-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
  padding-top: 8px;
  border-top: 1px solid var(--border);
}

/* ── Solution ── */
.solution-wrap { display: flex; flex-direction: column; gap: 16px; }
.solution-header { display: flex; flex-direction: column; gap: 16px; }
.solution-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.solution-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: var(--bright);
}
.solution-summary { color: var(--muted); line-height: 1.7; }
.solution-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.solution-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.solution-section { line-height: 1.75; font-size: 14px; }
.solution-primary { line-height: 1.8; white-space: pre-wrap; }

.alternatives { display: flex; flex-direction: column; gap: 12px; }
.alt-item {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  font-size: 14px;
  line-height: 1.6;
}
.alt-num {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--accent-dim);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
}

@media (max-width: 600px) {
  .field-row       { grid-template-columns: 1fr; }
  .form-footer     { flex-direction: column; align-items: stretch; }
  .solution-grid   { grid-template-columns: 1fr; }
}
</style>
