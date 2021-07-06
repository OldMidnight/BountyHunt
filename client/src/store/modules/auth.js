import { api } from '@/api'

const namespaced = true;

const state = {
  user: {
    user_id: null,
    username: null,
    email: null,
    authenticated: false,
    github_access_token: null
  },
  isLoggedIn: false
};

const getters = {
  isLoggedIn: state => state.isLoggedIn,
  user: state => state.user
};

const actions = {
  async registerUser({ dispatch }, user) {
    await api.post('/auth/register', user)
    await dispatch('fetchUser')
  },
  async loginUser({ dispatch }, user) {
    await api.post('/auth/login', user)
    await dispatch('fetchUser')
  },
  async fetchUser({ commit }) {
    await api.get('/auth/user')
      .then((response) => commit('setUser', response.data))
  },
  async logoutUser({ commit }) {
    await api.post('/auth/logout');
    commit('logoutUserState');
  },
  async createGithubAccessToken({ dispatch }, code) {
    await api.post('/auth/github/token', { code })
    await dispatch('fetchUser')
  }
};

const mutations = {
  setUser(state, user) {
    state.isLoggedIn = true;
    state.user = user;
  },
  logoutUserState(state) {
    state.isLoggedIn = false;
    state.user = {
      user_id: null,
      username: null,
      email: null,
      authenticated: false
    };
  }
};

export default {
  namespaced,
  state,
  getters,
  actions,
  mutations
};