import { createRouter, createWebHistory } from 'vue-router'
import SubmitView from '../views/SubmitView.vue'
import ArchiveView from '../views/ArchiveView.vue'
import ProblemDetailView from '../views/ProblemDetailView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: SubmitView },
    { path: '/archive', component: ArchiveView },
    { path: '/problem/:id', component: ProblemDetailView },
  ],
})

export default router
