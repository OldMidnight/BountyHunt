import { api } from '@/api';
import router from '@/router'

const namespaced = true;

const state = {
  bounty: {},
  has_application: false,
  categories: [],
  currencies: [
    {
      code: 'EUR',
      name: 'Euro',
      symbol: '€'
    },
    {
      code: 'GBP',
      name: 'British Pound Sterling',
      symbol: '£'
    },
    {
      code: 'USD',
      name: 'US Dollar',
      symbol: '$'
    }
  ],
  current_bounty: {}
};

const getters = {
  bounty: state => state.bounty,
  has_application: state => state.has_application,
  categories: state => state.categories,
  currencies: state => state.currencies,
  current_bounty: state => state.current_bounty
};

const actions = {
  async createBounty({ commit }, { amount, allow_multiple_investors }) {
    const timestamp = new Date(Date.now()).toISOString().replace('T',' ').replace('Z','');
    const bounty = {...state.bounty};
    bounty.created = !state.bounty.created ? timestamp : bounty.created;
    bounty.last_edited = timestamp;
    bounty.url = bounty.title.replace(/\W+/g, "-").toLowerCase();
    bounty.amount = amount;
    bounty.allow_multiple_investors = allow_multiple_investors;

    commit('setBounty', bounty);
    await api.post('/bounty/', state.bounty)
      .then(() => router.push(`/bounty/${bounty.url}`))
  },
  async createGitBounty({ rootState }, amount) {
    const timestamp = new Date(Date.now()).toISOString().replace('T',' ').replace('Z','');
    const issue = rootState.git.currentIssue
    const bounty = {
      title: issue.title,
      amount,
      allow_multiple_investors: true,
      created: timestamp,
      last_edited: timestamp,
      url: issue.html_url.split('/').slice(-4).join('/'),
      currency_code: 'EUR',
      is_git_bounty: true,
      git_url: issue.url,
      selected_categories: [['git', 3]],
      user_id: rootState.auth.user.user_id
    }

    await api.post('/bounty/', bounty)
      .then(() => router.push(`/bounty/git/${bounty.url}`))
  },
  editStateBounty({ commit }, bounty) {
    commit('setBounty', bounty);
  },
  async fetchCategories({ commit }) {
    await api.get('/bounty/categories')
      .then(({ data }) => {
        commit('setCategories', data);
      });
  },
  async fetchBountyList(_, options) {
    return await api.get('/bounty/list', {
      params: options
    })
      .then(({ data }) => data)
  },
  async fetchBounty({ commit }, { bounty_url, show_details }) {
    return await api.get(`/bounty/${bounty_url}`, {
      params: { show_details }
    })
      .then(({ data }) => {
        commit('setBounty', data.bounty)
        commit('setHasApplication', data.has_application)
      })
  },
  async applyToBounty(_, { bounty_url, application_text }) {
    const timestamp = new Date(Date.now()).toISOString().replace('T',' ').replace('Z','');
    return await api.post('/bounty/apply', {
      application_text,
      created: timestamp,
      bounty_url
    })
  },
  async assignBounty(_, { bounty_url, assigned_user_id }) {
    return await api.put(`/bounty/assign`, {
      assigned_user_id,
      bounty_url
    })
  },
  async fetchAssignedHunter(_, bounty_url) {
    return await api.get(`/bounty/hunter`, { params: { bounty_url }})
      .then(({ data }) => data)
  },
  async investBounty(_, { bounty_url, investment}) {
    const timestamp = new Date(Date.now()).toISOString().replace('T',' ').replace('Z','');
    investment.created = timestamp;
    await api.post(`/bounty/invest`, { investment, bounty_url })
  },
  async fetchCurrentBounty({ commit }, user) {
    return await api.get(`/bounty/user/${user}/current`)
      .then(({ data }) => {
        commit('setCurrentBounty', data)
      })
  },
  async submitBounty(_, { bounty_url, submission }) {
    return await api.put(`/bounty/submission`, {
      submission,
      bounty_url
    })
      .then((response) => response)
  },
  async approveBounty(_, { bounty_url, is_approved }) {
    const decision_datetime = new Date(Date.now()).toISOString().replace('T',' ').replace('Z','');
    return await api.post(`/bounty/submission/approval`, { is_approved, decision_datetime, bounty_url })
      .then((response) => response)
  },
  async fetchUserApproval(_, { bounty_url, username }) {
    return await api.get(`/bounty/${username}/approval`, { params: { bounty_url }})
      .then(({ data }) => data)
  },
  async fetchUserBountyInvestment(_, bounty_url) {
    return await api.get('/bounty/invest', { params: { bounty_url }})
      .then(({ data }) => data)
  },
  async fetchGitBounty({ commit }, bountyUrl) {
    await api.get(`/bounty/git/${bountyUrl}`)
      .then(({ data }) => {
        commit('setBounty', data.bounty)
        commit('setHasApplication', data.has_application)
        commit('git/setCurrentIssue', data, { root: true })
      })
  }
};

const mutations = {
  setBounty(state, bounty) {
    state.bounty = bounty;
  },
  setHasApplication(state, value) {
    state.has_application = value
  },
  setCategories(state, categories) {
    state.categories = categories;
  },
  setCurrentBounty(state, bounty) {
    state.current_bounty = bounty;
  }
};

export default {
  namespaced,
  state,
  getters,
  actions,
  mutations
};