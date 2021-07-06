import Vue from 'vue';
import Vuex from 'vuex';
import bounty from './modules/bounty';
import auth from './modules/auth';
import payments from './modules/payments';
import git from './modules/git';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    bounty,
    auth,
    payments,
    git
  }
});