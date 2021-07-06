<template>
  <validation-observer v-slot="{ invalid, reset }">
    <main-layout>
      <v-container :class="`${isMobile ? 'm-' : ''}bounty-container`">
        <v-row class="">
          <v-col cols="12" md="7" class="border rounded">
            <v-row class="px-3">
              <v-col cols="12" class="d-flex">
                <div v-if="user && user.user_id === bounty.user_id">
                  <v-btn color="primary" :to="bounty_url(bounty.url)" small>Manage Bounty</v-btn>
                </div>
                <div v-else>
                  <v-btn
                    v-if="bounty.assigned_user_id === null"
                    :disabled="has_application"
                    color="primary"
                    small
                    @click="handleApply"
                  >
                    {{ has_application ? 'Application Sent' : 'Apply For Bounty' }}
                    <v-icon  class="ml-2" v-if="has_application">
                      mdi-check
                    </v-icon>
                  </v-btn>
                  <v-btn v-else disabled small>
                    Assigned
                  </v-btn>
                </div>
              </v-col>
              <v-col cols="12">
                <div class="d-flex align-center">
                  <v-icon :color="currentIssue.state === 'open' ? 'success' : 'error'">
                    mdi-alert-circle-outline
                  </v-icon>
                  <span class="display-1 ml-2">{{ currentIssue.title }}</span>
                  <span class="title ml-2 text--secondary">#{{ currentIssue.number }}</span>
                </div>
                <span class="caption">
                  Created by: 
                  <a class="black--text" :href="currentIssue.user.html_url">
                    {{ currentIssue.user.login }}
                    <v-icon color="black" small>mdi-github</v-icon>
                  </a>
                </span>
              </v-col>
              <v-col cols="12" v-if="currentIssue.body.length > 0">
                <v-divider class="mb-3"></v-divider>
                <div v-html="compiledMarkdown(currentIssue.body)"></div>
              </v-col>
              <v-col>
                <v-divider></v-divider>
                <v-row>
                  <v-col
                    v-for="(comment, index) in currentIssueComments"
                    :key="index"
                    cols="12"
                    class="pb-0"
                  >
                    <v-row>
                      <v-col v-if="!isMobile" md="1" class="d-flex justify-end px-0 pt-0">
                        <v-avatar size="40">
                          <v-img :src="comment.user.avatar_url"></v-img>
                        </v-avatar>
                      </v-col>
                      <v-col cols="12" md="11" class="pt-0">
                        <div v-html="compiledMarkdown(comment.body)"></div>
                        <span class="caption text--secondary">posted by {{ comment.user.login }} {{ relativeTime(comment.created_at) }}</span>
                      </v-col>
                    </v-row>
                    <v-divider></v-divider>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-col>
          <v-col cols="12" md="3" :class="{'ml-12': !isMobile }">
            <span class="title font-weight-bold">Invest in this Bounty</span>
            <v-row class="invest-container">
              <v-row
                class="border rounded mt-3"
                :class="{ 'invest-container-disable': bounty.assigned_user_id !== null }"
              >
                <v-col cols="12" class="d-flex flex-column align-center">
                  <span class="display-1">€{{ convertCents(bounty.amount) }}</span>
                  <span class="green--text font-weight-bold">Bounty</span>
                  <v-expansion-panels class="mt-2" mandatory>
                    <v-expansion-panel>
                      <v-expansion-panel-header>
                        Investors
                      </v-expansion-panel-header>
                      <v-expansion-panel-content>
                        <v-divider></v-divider>
                        <v-list-item-group>
                          <v-list-item
                            v-for="i in investments"
                            :key="i.investment_id"
                            :to="`/u/${i.username}`"
                          >
                            <v-list-item-content>
                              <v-list-item-title>{{ i.username }}</v-list-item-title>
                            </v-list-item-content>
                            <v-list-item-action class="green--text text--darken-1">
                              €{{ convertCents(i.amount) }}
                            </v-list-item-action>
                          </v-list-item>
                        </v-list-item-group>
                      </v-expansion-panel-content>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-col>
                <v-col cols="12">
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="12" class="d-flex flex-column">
                  <v-item-group
                    v-model="investment.amount"
                    class="d-flex justify-space-around w-100"
                  >
                    <v-item
                      v-for="(amount, index) in default_amounts"
                      :key="index"
                      v-slot="{ active, toggle }"
                      class="ma-2"
                      :value="amount"
                    >
                      <v-btn
                        color="primary"
                        :outlined="!active"
                        :depressed="active"
                        small
                        @click="toggle"
                      >
                        {{ `${currency_symbol}${amount}` }}
                      </v-btn>
                    </v-item>
                  </v-item-group>
                  <span class="mx-auto font-weight-bold">- or -</span>
                  <v-row>
                    <v-col cols="12" class="pb-0">
                      <validation-provider
                        name="amount"
                        :rules="rules.amount"
                        v-slot="validationContext"
                      >
                        <v-text-field
                          :value="investment.amount"
                          v-model="investment.amount"
                          label="Bounty Amount"
                          outlined
                          dense
                          prefix="€"
                          :error="getValidationState(validationContext)"
                          :error-messages="validationContext.errors[0]"
                          :disabled="bounty.assigned_user_id !== null"
                        ></v-text-field>
                      </validation-provider>
                    </v-col>
                  </v-row>
                  <span class="font-weight-bold mb-2">Payment Details</span>
                  <validation-provider
                    name="first_name"
                    :rules="rules.names"
                    v-slot="validationContext"
                  >
                    <v-text-field
                      v-model="investment.first_name"
                      label="First Name"
                      outlined
                      dense
                      :error="getValidationState(validationContext)"
                      :error-messages="validationContext.errors[0]"
                      :disabled="bounty.assigned_user_id !== null"
                    ></v-text-field>
                  </validation-provider>
                  <validation-provider
                    name="last_name"
                    :rules="rules.names"
                    v-slot="validationContext"
                  >
                    <v-text-field
                      v-model="investment.last_name"
                      label="Last Name"
                      outlined
                      dense
                      :error="getValidationState(validationContext)"
                      :error-messages="validationContext.errors[0]"
                      :disabled="bounty.assigned_user_id !== null"
                    ></v-text-field>
                  </validation-provider>
                  <stripe-element-card
                    ref="cardRef"
                    :pk="pulishable_key"
                    :hidePostalCode="true"
                    :disabled="bounty.assigned_user_id !== null"
                  ></stripe-element-card>
                  <span class="caption mx-auto">
                    You will be charged €{{ investment.amount }}
                  </span>
                  <v-btn
                    color="primary"
                    depressed
                    :disabled="invalid || loading || bounty.assigned_user_id !== null"
                    :loading="loading"
                    @click="handleInvestBounty(reset)"
                  >
                    Confirm
                  </v-btn>
                </v-col>
              </v-row>
              <div v-if="bounty.assigned_user_id !== null" class="invest-overlay">
                <span class="invest-overlay-text font-weight-bold">Investing has been disabled for this bounty as it has been assigned to a bounty hunter. <router-link to="/support/faq">Learn more.</router-link></span>
              </div>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
      <v-dialog
        v-model="applying"
        persistent
        width="600"
      >
        <v-card>
          <v-card-title>Apply to bounty</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-form>
                  <v-textarea
                    v-model="application_text"
                    placeholder="Additional Information"
                    hint="optional"
                    persistent-hint
                  ></v-textarea>
                </v-form>
              </v-col>
              <v-col cols="12" md="6" class="d-flex flex-column align-center mt-2">
                <span>
                  By applying to this bounty, you agree to sharing your profile infomation with the creator of this bounty.
                </span>
                <div class="d-flex justify-space-around w-100 mt-7">
                  <v-btn
                    color="success"
                    @click="applyBounty"
                  >
                    Apply
                  </v-btn>
                  <v-btn
                    color="error"
                    @click="applying = false"
                  >
                    Cancel
                  </v-btn>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-dialog>
    </main-layout>
  </validation-observer>
</template>

<script>
import MainLayout from '@/components/layouts/MainLayout';
import { mapActions, mapGetters } from 'vuex';
import { ValidationProvider, ValidationObserver } from 'vee-validate';
import { StripeElementCard } from '@vue-stripe/vue-stripe';
import { convertCents, relativeTime } from '@/helpers'
import marked from 'marked'
export default {
  components: { MainLayout, ValidationProvider, ValidationObserver, StripeElementCard },
  data: () => ({
    applying: false,
    application_text: null,
    default_amounts: [2, 5, 20, 50],
    investment: {
      currency_code: 'EUR',
      amount: 2,
      first_name: null,
      last_name: null
    },
    rules: {
      names: { required: true },
      amount: {
        required: true,
        decimals: true,
        currency_decimal: true,
        min_value: 1
      },
    },
    pulishable_key: process.env.VUE_APP_STRIPE_PUBLISHABLE_KEY,
    loading: false,
    investments: {}
  }),
  computed: {
    ...mapGetters({
      user: 'auth/user',
      currencies: 'bounty/currencies',
      bounty: 'bounty/bounty',
      has_application: 'bounty/has_application',
      currentIssue: 'git/currentIssue',
      currentIssueComments: 'git/currentIssueComments'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    bounty_url() {
      return (url) => { 
        return `/bounty/git/${url}/manage`
      }
    },
    currency_symbol(){
      const currency = this.currencies.find(({ code }) => code === this.investment.currency_code)
      return currency.symbol
    },
    compiledMarkdown() {
      return (text) => marked(text, { breaks: true })
    }
  },
  created() {
    this.sortInvestments()
  },
  methods: {
    ...mapActions({
      applyToBounty: 'bounty/applyToBounty',
      processPayment: 'payments/processPayment',
      investBounty: 'bounty/investBounty',
      fetchGitBounty: 'bounty/fetchGitBounty'
    }),
    convertCents,
    relativeTime,
    sortInvestments() {
      const sorted_investments = this.bounty.investments.sort((inv_a, inv_b) => inv_a.amount - inv_b.amount)
      const investments = {}

      sorted_investments.forEach((investment) => {
        if (investments[investment.user_id]) {
          investments[investment.user_id].amount += investment.amount
        } else {
          investments[investment.user_id] = investment
        }
      })
      this.investments = investments
    },
    async applyBounty() {
      const response = await this.applyToBounty({
        bounty_url: this.bounty.url,
        application_text: this.application_text
      });
      const status = response.status;

      switch (status) {
        case 409:
          this.$root.$emit('showSnackbar', { color: 'error', message: response.data.msg });
          break;

        case 201:
          this.$root.$emit('showSnackbar', { color: 'success', message: 'Successfully applied to bounty' });
          break;
      
        default:
          this.$root.$emit('showSnackbar', { color: 'error', message: 'An error has occurred' });
          break;
      }
      await this.fetchGitBounty(this.bounty.url)
      this.sortInvestments()
      this.applying = false;
    },
    handleApply() {
      if (this.user.authenticated) {
        this.applying = true
      } else {
        this.$router.push({
          path: '/auth/login',
          query: { redirect: this.$route.fullPath }
        })
      }
    },
    getValidationState({ dirty, validated, valid = null}) {
      return dirty || validated ? !valid : false;
    },
    async handleInvestBounty(reset_fn) {
      const stripe = this.$refs.cardRef.stripe;
      const card = this.$refs.cardRef.element;
      this.loading = true;
      this.$refs.cardRef.submit()
      const client_secret = await this.processPayment({
        amount: this.investment.amount,
        currency: this.investment.currency_code.toLowerCase()
      });

      stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card,
          billing_details: {
            name: `${this.investment.first_name} ${this.investment.last_name}`
          }
        }
      }).then(async (result) => {
        if(result.error) {
          console.log(result.error)
          this.$root.$emit('showSnackbar', { color: 'error', message: result.error.message })
        } else {
          console.log(result)
          if (result.paymentIntent.status === 'succeeded') {
            await this.investBounty({
              bounty_url: this.bounty.url,
              investment: this.investment
            })
            this.$root.$emit('showSnackbar', { color: 'success', message: 'Bounty Invested!' })
          }
        }
        await this.fetchGitBounty(this.bounty.url);
        this.sortInvestments();
        this. investment = {
          currency_code: 'EUR',
          amount: 2,
          first_name: null,
          last_name: null
        }
        reset_fn();
        this.loading = false;
      })
    }
  }
}
</script>

<style lang="scss" scoped>

</style>