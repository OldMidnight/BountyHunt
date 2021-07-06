import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import vuetify from './plugins/vuetify';
import './assets/styles/main.scss'

import { extend } from 'vee-validate';
import * as rules from 'vee-validate/dist/rules';
import { messages } from 'vee-validate/dist/locale/en.json';

import 'animate.css';

Vue.config.productionTip = false; 

Object.keys(rules).forEach(rule => {
  extend(rule, {
    ...rules[rule],
    message: messages[rule]
  });
});

// Create custom vee-validate rules

extend('has_upper_case', {
  validate: value => {
    const pattern = /[A-Z]+/
    return pattern.test(value)
  },
  message: 'The {_field_} must contain at least 1 uppercase letter'
})

extend('has_digit', {
  validate: value => {
    const pattern = /\d+/
    return pattern.test(value)
  },
  message: 'The {_field_} must contain at least 1 digit'
})

extend('currency_decimal', {
  validate: value => {
    const split_val = value.toString().split('.')
    if (split_val.length === 1) {
      return true
    } else if (split_val.length === 2) {
      if (split_val[1].length > 2) {
        return false
      }
    }
    return true
  },
  message: 'The {_field_} must have less than 100 cents'
})

extend('no_whitespace', {
  validate: value => !(value || '').includes(' '),
  message: 'The {_field_} cannot contain spaces'
})

extend('decimals', {
  validate: (value, { fix = '*', separator = '.' }) => {
    if (Array.isArray(value)) {
      return value.every((val) => this(val, { fix, separator }))
    }

    // if is 0.
    if (Number(fix) === 0) {
      return /^-?\d*$/.test(value)
    }

    const regexPart = fix === '*' ? '+' : `{1,${fix}}`
    const regex = new RegExp(
      `^[-+]?\\d*(\\${separator}\\d${regexPart})?([eE]{1}[-]?\\d+)?$`
    )

    if (!regex.test(value)) {
      return false
    }

    const parsedValue = parseFloat(value)

    return parsedValue === parsedValue
  },
  params: ['fix', 'separator']
})

// Templating filter for truncating text
Vue.filter('truncate', function (text, length, suffix) {
  if (text.length > length) {
      return text.substring(0, length) + suffix;
  } else {
      return text;
  }
});

async function initialiseVue() {
  await store.dispatch('auth/fetchUser');
  new Vue({
    router,
    store,
    vuetify,
    render: h => h(App)
  }).$mount('#app');
}

initialiseVue()