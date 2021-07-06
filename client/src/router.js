import Vue from 'vue'
import Router from 'vue-router'
import store from './store'
import { api } from '@/api'

Vue.use(Router)

async function canEdit(resource, params) {
  // Only the creator of a resource or assigned users can edit that resource. This is run before routes that give that functionality are entered
  return await api.post('/auth/res/permission', { resource, params })
    .then(({ data }) => data)
}

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/bounty/create',
      name: 'createBounty',
      component: () => import('@/views/bounty/create.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/bounty/create/git',
      name: 'createGitBounty',
      component: () => import('@/views/bounty/git/index.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        await store.dispatch('git/githubSearchRepos', {
          q: '',
          page: 1,
          perPage: 10
        })
        await store.dispatch('git/fetchGitRepos')
        next()
      }
    },
    {
      path: '/bounty/create/git/:user/:repo',
      name: 'createGitBountyRepo',
      component: () => import('@/views/bounty/git/repo.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        await store.dispatch('git/fetchCurrentRepo', `${to.params.user}/${to.params.repo}`)
        next()
      }
    },
    {
      path: '/bounty/create/git/:user/:repo/issues/:issue',
      component: () => import('@/views/bounty/git/issue.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        await store.dispatch('git/fetchCurrentIssue', {
          issueNumber: to.params.issue,
          full_name: `${to.params.user}/${to.params.repo}`
        })
        next()
      }
    },
    {
      path: '/auth/register',
      name: 'register',
      component: () => import('@/views/auth/register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/auth/login',
      name: 'login',
      component: () => import('@/views/auth/login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/bounty/:bountyUrl',
      component: () => import('@/views/bounty/bounty.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/bounty/git/:user/:repo/issues/:issue',
      component: () => import('@/views/bounty/git.vue'),
      meta: { requiresAuth: false },
      async beforeEnter(to, _, next) {
        await store.dispatch('bounty/fetchGitBounty', `${to.params.user}/${to.params.repo}/issues/${to.params.issue}`)
        next()
      }
    },
    {
      path: '/bounty/:bounty_url/manage',
      component: () => import('@/views/bounty/manage.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        const can_edit = await canEdit('bounty', { bounty_url:  to.params.bounty_url })
        if (can_edit) {
          next()
        } else {
          next('/')
        }
      }
    },
    {
      path: '/bounty/git/:user/:repo/issues/:issue/manage',
      component: () => import('@/views/bounty/git/manage.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        const can_edit = await canEdit('bounty', {
          bounty_url:  `${to.params.user}/${to.params.repo}/issues/${to.params.issue}`
        })
        if (can_edit) {
          await store.dispatch('bounty/fetchGitBounty', `${to.params.user}/${to.params.repo}/issues/${to.params.issue}`)
          next()
        } else {
          next('/')
        }
      }
    },
    {
      path: '/bounty/git/:user/:repo/issues/:issue/hunter',
      component: () => import('@/views/bounty/git/hunter.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        await store.dispatch('bounty/fetchGitBounty', `${to.params.user}/${to.params.repo}/issues/${to.params.issue}`)
        next()
      }
    },
    {
      path: '/bounty/:bounty_url/hunter',
      component: () => import('@/views/bounty/hunter.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        await store.dispatch('bounty/fetchBounty', {
          bounty_url: to.params.bounty_url,
          show_details: false
        })
        next()
      }
    },
    {
      path: '/u/:user',
      component: () => import('@/views/u/profile.vue'),
      meta: { requiresAuth: true },
      async beforeEnter(to, _, next) {
        await store.dispatch('bounty/fetchCategories')
        await store.dispatch('bounty/fetchCurrentBounty', to.params.user)
        next()
      }
    },
    {
      path: '/auth/github/callback',
      component: () => import('@/views/auth/github/callback.vue')
    },
    {
      path: '/404',
      component: () => import('@/views/404.vue'),
      meta: { requiresAuth: false }
    }, 
    {
      path: '*',
      redirect: '/404'
    }
  ]
})

// Check if the user is authenticated and handle redirecting to login page
router.beforeEach(async (to, _, next) => {
  const isLoggedIn = store.getters['auth/user'].authenticated;
  if ((to.name === 'login' || to.name === 'register') && isLoggedIn) {
    next('/')
  }
  if(to.meta.requiresAuth && !isLoggedIn) {
    next({
      path: '/auth/login',
      query: { redirect: to.path }
    })
    return
  }
  next();
})

export default router;