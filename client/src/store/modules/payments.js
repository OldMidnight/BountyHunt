import { api } from '@/api'

const namespaced = true;

const state = {};

const getters = {};

const actions = {
  async processPayment(_, options) {
    const client_secret = api.post('/payments/create_intent', options)
      .then(({ data }) => data.client_secret)
    return client_secret
  }
};

const mutations = {
  
};

export default {
  namespaced,
  state,
  getters,
  actions,
  mutations
}