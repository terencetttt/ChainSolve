<template>
  <div class="submit-page">

    <!-- HERO -->
    <div class="hero">
      <p class="hero-eyebrow">Decentralized AI Resolution</p>
      <h1 class="hero-title">What's your problem?</h1>
      <p class="hero-sub">
        Submit any problem. Multiple independent AI validators reach consensus.
        The solution is sealed on Bradbury chain — permanently.
      </p>
      <div class="hero-rule" aria-hidden="true"></div>
    </div>

    <!-- FORM CARD -->
    <div v-if="!txHash" class="card form-card">
      <div class="field">
        <label class="field-label">Problem title</label>
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
            <option value="TECHNICAL">Technical</option>
            <option value="BUSINESS">Business</option>
            <option value="PERSONAL">Personal</option>
            <option value="RESEARCH">Research</option>
          </select>
        </div>
        <div class="field">
          <label class="field-label">Severity</label>
          <select v-model="form.severity" class="field-input">
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      <div class="field">
        <label class="field-label">Describe the problem</label>
        <textarea
          v-model="form.description"
          class="field-input field-textarea"
          placeholder="Give as much context as possible — the more detail you provide, the better the solution will be."
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
          {{ submitting ? 'Submitting…' : 'Solve it on chain' }}
        </button>
      </div>

      <p v-if="error" class="error-msg">{{ error }}</p>
    </div>

    <!-- TX STATUS TRACKER -->
    <div v-if="txHash && !solution" class="card status-card">
      <p class="status-eyebrow">Matter in review</p>
      <h2 class="status-title">Reaching consensus</h2>

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
        <span class="mono">Elapsed: {{ elapsed }}</span>
      </div>
    </div>

    <!-- SOLUTION REVEAL — REPORT DOCUMENT -->
    <div v-if="solution" class="solution-wrap">
      <div class="report-head card">
        <div class="report-badges">
          <span class="badge" :class="`badge-${solution.difficulty.toLowerCase()}`">
            {{ solution.difficulty }}
          </span>
          <span class="badge" :class="`badge-${solution.confidence.toLowerCase()}`">
            {{ solution.confidence }} confidence
          </span>
          <span class="badge badge-solved">Sealed on chain</span>
        </div>
        <h2 class="report-title">{{ solution.title }}</h2>
        <div class="report-actions">
          <RouterLink :to="`/problem/${solution.id}`" class="btn-primary">
            View full report →
          </RouterLink>
          <RouterLink to="/archive" class="btn-ghost">Browse archive</RouterLink>
        </div>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">01</span> Executive summary</p>
        <p class="body-text">{{ solution.problem_summary }}</p>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">02</span> Root cause analysis</p>
        <p class="body-text">{{ solution.root_cause }}</p>
      </div>

      <div class="card report-section">
        <p class="section-label"><span class="section-num">03</span> Recommended course of action</p>
        <p class="body-text pre-wrap">{{ solution.primary_solution }}</p>
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
        <p class="body-text">{{ solution.risks }}</p>
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

const stages = [
  { key: 'pending',   label: 'Submitted',           desc: 'Transaction broadcast' },
  { key: 'proposing', label: 'Validators selected', desc: 'Leader chosen' },
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
    if (secondsElapsed.value === 20)  stageIndex.value = 1
    if (secondsElapsed.value === 60)  stageIndex.value = 2
    if (secondsElapsed.value === 120) stageIndex.value = 3
  }, 1000)
}

function stopTimer() {
  if (timer) { clearInterval(timer); timer = null }
}

onUnmounted(stopTimer)

async function submit() {
  error.value = ''
  if (!isConnected.value) {
    try { await connectWallet() } catch { error.value = 'Please connect your wallet first.'; return }
  }

  submitting.value = true
  try {
    startTimer()
    await writeWithRetry(
      'solve_problem',
      [form.value.title, form.value.description, form.value.category, form.value.severity],
      (hash) => { txHash.value = hash },
    )
    stopTimer()
    stageIndex.value = 4

    await new Promise(r => setTimeout(r, 800))

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
.submit-page { max-width: 760px; margin: 0 auto; }

/* ── Hero ── */
.hero {
  text-align: center;
  padding: 40px 0 52px;
}
.hero-eyebrow {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--forest);
  margin-bottom: 22px;
}
.hero-title {
  font-family: var(--font-display);
  font-size: clamp(34px, 5.5vw, 52px);
  font-weight: 700;
  color: var(--ink);
  line-height: 1.15;
  margin-bottom: 20px;
}
.hero-sub {
  max-width: 480px;
  margin: 0 auto;
  color: var(--soft);
  font-size: 15px;
  line-height: 1.7;
}
.hero-rule {
  width: 56px;
  height: 2px;
  background: var(--forest);
  margin: 36px auto 0;
}

/* ── Form ── */
.form-card { display: flex; flex-direction: column; gap: 24px; }

.field { display: flex; flex-direction: column; gap: 8px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }

.field-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--soft);
}

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
  appearance: none;
  border-radius: 0;
}
.field-input:focus {
  border-color: var(--forest);
  box-shadow: 0 0 0 3px var(--forest-wash);
}
.field-input::placeholder { color: var(--faint); }
.field-textarea { resize: vertical; min-height: 150px; line-height: 1.65; }

select.field-input {
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%235E6572'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
}

.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-top: 6px;
  border-top: 1px solid var(--rule);
}
.form-note { font-size: 12px; color: var(--faint); max-width: 300px; }
.btn-submit { padding: 14px 34px; }
.error-msg { color: var(--red); font-size: 13px; }

/* ── Status tracker ── */
.status-card { margin-top: 8px; }
.status-eyebrow {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--forest);
  margin-bottom: 8px;
}
.status-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 36px;
}
.status-track {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;
}
.stage {
  display: grid;
  grid-template-columns: 32px 1fr;
  gap: 0 16px;
  align-items: start;
  position: relative;
}
.stage-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
  background: var(--card);
  border: 1px solid var(--rule-dark);
  color: var(--faint);
  transition: all 0.3s;
}
.stage--done .stage-dot   { background: var(--forest); border-color: var(--forest); color: #fff; }
.stage--active .stage-dot { border-color: var(--forest); color: var(--forest); }

.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--forest);
  animation: pulse 1.4s infinite;
}
@keyframes pulse {
  0%, 100% { transform: scale(1);   opacity: 1; }
  50%       { transform: scale(1.6); opacity: 0.4; }
}

.stage-info {
  padding: 5px 0 26px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stage-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--ink);
}
.stage--pending .stage-name { color: var(--faint); }
.stage--done .stage-name    { color: var(--forest); }
.stage-desc { font-size: 12px; color: var(--faint); }

.stage-line {
  position: absolute;
  left: 15px;
  top: 32px;
  width: 1px;
  height: calc(100% - 8px);
  background: var(--rule-dark);
}
.stage--done .stage-line { background: var(--forest); }

.status-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--faint);
  padding-top: 14px;
  border-top: 1px solid var(--rule);
}

/* ── Report document ── */
.solution-wrap { display: flex; flex-direction: column; gap: 14px; }

.report-head {
  display: flex;
  flex-direction: column;
  gap: 18px;
  border-top: 3px solid var(--forest);
}
.report-badges { display: flex; flex-wrap: wrap; gap: 8px; }
.report-title {
  font-family: var(--font-display);
  font-size: 26px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.25;
}
.report-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.report-section { padding: 26px 32px; }
.body-text { font-size: 14.5px; line-height: 1.75; color: var(--ink); }
.pre-wrap { white-space: pre-wrap; }

.alternatives { display: flex; flex-direction: column; gap: 14px; }
.alt-item {
  display: flex;
  gap: 16px;
  align-items: baseline;
}
.alt-marker {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--forest);
  font-weight: 500;
}

@media (max-width: 600px) {
  .field-row   { grid-template-columns: 1fr; }
  .form-footer { flex-direction: column; align-items: stretch; }
}
</style>
