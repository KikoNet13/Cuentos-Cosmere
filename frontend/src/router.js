import { createRouter, createWebHistory } from 'vue-router'
import LibraryView from './views/LibraryView.vue'
import StoryView from './views/StoryView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/biblioteca',
    },
    {
      path: '/biblioteca',
      component: LibraryView,
    },
    {
      path: '/biblioteca/:nodePath(.*)*',
      component: LibraryView,
    },
    {
      path: '/cuento/:storyPath(.*)*',
      component: StoryView,
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/biblioteca',
    },
  ],
})
