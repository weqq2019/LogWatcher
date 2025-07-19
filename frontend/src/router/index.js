import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Projects from '../views/Projects.vue'
import News from '../views/News.vue'
import Tools from '../views/Tools.vue'
import Cursor from '../views/Cursor.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects
  },
  {
    path: '/news',
    name: 'News',
    component: News
  },
  {
    path: '/tools',
    name: 'Tools',
    component: Tools
  },
  {
    path: '/cursor',
    name: 'Cursor',
    component: Cursor
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 