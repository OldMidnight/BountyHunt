import { api } from '@/api'

const namespaced = true;

const state = {
  gitRepos: [],
  repos: {},
  currentRepo: {},
  currentRepoIssues: [],
  currentRepoIssuesCount: [],
  currentIssue: {},
  currentIssueComments: []
};

const getters = {
  gitRepos: state => state.gitRepos,
  repos: state => state.repos,
  currentRepo: state => state.currentRepo,
  currentRepoIssues: state => state.currentRepoIssues,
  currentRepoIssuesCount: state => state.currentRepoIssuesCount,
  currentIssue: state => state.currentIssue,
  currentIssueComments: state => state.currentIssueComments
};

const actions = {
  async githubSearchRepos({ commit }, { q, page, perPage }) {
    await api.get('/git/github/repos', {
      params: {
        q,
        per_page: perPage,
        page
      }
    })
      .then(({ data }) => commit('setRepos', data))
  },
  async githubSearchIssues({ commit }, { repo, searchString }) {
    const s = encodeURIComponent(`${searchString} repo:${repo} is:issue is:open`)
    await api.get('/git/github/search/issues', {
      params: {
        q: s
      }
    })
      .then(({ data }) => commit('setCurrentRepoIssues', data.items))
  },
  async addGithubRepositories(_, repos) {
    return await api.post('/git/github/repos', repos)
      .then((response) => response)
  },
  async fetchGitRepos({ commit }) {
    await api.get('/git/github/user/repos')
      .then(({ data }) => commit('setGitRepos', data))
  },
  async fetchCurrentRepo({ commit }, full_name) {
    const q = encodeURIComponent(`repo:${full_name} is:issue is:open`)
    await api.get(`/git/github/repo`, {
      params: { 
        full_name,
        q
      }
    })
      .then(({ data }) => {
        commit('setCurrentRepo', data.repo)
        commit('setCurrentRepoIssues', data.issues)
      })
  },
  async fetchCurrentIssue({ commit }, { issueNumber, full_name }) {
    await api.get(`/git/github/repo/issues/${issueNumber}`, { params: { full_name }})
      .then(({ data }) => commit('setCurrentIssue', data))
  }
};

const mutations = {
  setGitRepos(state, repos) {
    state.gitRepos = repos
  },
  setRepos(state, data) {
    state.repos = data
  },
  setCurrentRepo(state, repo) {
    state.currentRepo = repo
  },
  setCurrentRepoIssues(state, { items, total_count }) {
    state.currentRepoIssues = items
    state.currentRepoIssuesCount = total_count
  },
  setCurrentIssue(state, { issue, comments }) {
    state.currentIssue = issue
    state.currentIssueComments = comments
  }
};

export default {
  namespaced,
  state,
  getters,
  actions,
  mutations
}