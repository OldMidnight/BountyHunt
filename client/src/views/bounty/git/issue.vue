<template>
  <main-layout>
    <validation-observer v-slot="{ invalid }">
      <v-container :class="`${isMobile ? 'm-' : ''}git-creation-container`">
        <v-row>
          <v-col cols="12" class="pa-0">
            <router-link class="text--secondary caption" to="/bounty/create/git">
              <v-icon small>mdi-arrow-left</v-icon>Back
            </router-link>
          </v-col>
          <v-col cols="12" md="7" class="border rounded">
            <v-row class="px-3">
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
              <v-col cols="12" v-if="currentIssue.body.length  > 0">
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
                      <v-col cols="1" class="d-flex justify-end px-0 pt-0">
                        <v-avatar size="40">
                          <v-img :src="comment.user.avatar_url"></v-img>
                        </v-avatar>
                      </v-col>
                      <v-col cols="11" class="pt-0">
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
          <v-col cols="12" md="3" :class="`${isMobile ? '' : 'ml-9'} d-flex flex-column pt-0`">
            <span class="title mb-2">Fund Bounty</span>
            <v-row class="border rounded">
              <v-col cols="12">
                <validation-provider
                  name="firstName"
                  :rules="rules.names"
                  v-slot="validationContext"
                >
                  <v-text-field
                    v-model="firstName"
                    filled
                    dense
                    label="First Name"
                    :error="getValidationState(validationContext)"
                    :error-messages="validationContext.errors[0]"
                    :loading="loading"
                  ></v-text-field>
                </validation-provider>
                <validation-provider
                  name="surname"
                  :rules="rules.names"
                  v-slot="validationContext"
                >
                  <v-text-field
                    v-model="lastName"
                    filled
                    dense
                    label="Surname"
                    :error="getValidationState(validationContext)"
                    :error-messages="validationContext.errors[0]"
                    :loading="loading"
                  ></v-text-field>
                </validation-provider>
                <v-divider></v-divider>
              </v-col>
              <v-col col="12" class="d-flex flex-column pt-0">
                <v-item-group
                  v-model="amount"
                  class="d-flex justify-space-around w-100"
                >
                  <v-item
                    v-for="(amount, index) in defaultAmounts"
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
                      €{{ amount }}
                    </v-btn>
                  </v-item>
                </v-item-group>
                <span class="mx-auto  overline">- or -</span>
                <v-row>
                  <v-col cols="12" class="py-0">
                    <validation-provider
                      name="amount"
                      :rules="rules.amount"
                      v-slot="validationContext"
                    >
                      <v-text-field
                        :value="amount"
                        v-model="amount"
                        label="Bounty Amount"
                        filled
                        dense
                        prefix="€"
                        :loading="loading"
                        :error="getValidationState(validationContext)"
                        :error-messages="validationContext.errors[0]"
                      ></v-text-field>
                    </validation-provider>
                    <v-divider></v-divider>
                  </v-col>
                </v-row>
              </v-col>
              <v-col cols="12" class="d-flex flex-column pt-0">
                <stripe-element-card
                  ref="cardRef"
                  :pk="pulishableKey"
                  :loading="loading"
                  :hidePostalCode="true"
                ></stripe-element-card>
                <span class="caption mx-auto">
                  You will be charged €{{ amount }}
                </span>
              </v-col>
              <v-col cols="12" class="d-flex justify-center">
                <v-btn
                  color="primary"
                  :disabled="invalid"
                  :loading="loading"
                  @click="handleCreateBounty"
                >Publish Bounty</v-btn>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </validation-observer>
  </main-layout>
</template>

<script>
import { relativeTime } from '@/helpers'
import { ValidationObserver, ValidationProvider } from 'vee-validate'
import { StripeElementCard } from '@vue-stripe/vue-stripe';
import MainLayout from '@/components/layouts/MainLayout'
import { mapActions, mapGetters } from 'vuex'
import marked from 'marked'
export default {
  components: { MainLayout, ValidationObserver, ValidationProvider, StripeElementCard },
  data: () => ({
    firstName: null,
    lastName: null,
    rules: {
      names: {
        required: true
      },
      amount: { 
        required: true,
        decimals: true,
        currency_decimal: true
      }
    },
    amount: 5,
    pulishableKey: process.env.VUE_APP_STRIPE_PUBLISHABLE_KEY,
    defaultAmounts: [2, 5, 20, 50],
    loading: false
  }),
  computed: {
    ...mapGetters({
      currentIssue: 'git/currentIssue',
      currentIssueComments: 'git/currentIssueComments'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    compiledMarkdown() {
      return (text) => marked(text, { breaks: true })
    }
  },
  methods: {
    ...mapActions({
      processPayment: 'payments/processPayment',
      createGitBounty: 'bounty/createGitBounty'
    }),
    relativeTime,
    getValidationState({ dirty, validated, valid = null}) {
      return dirty || validated ? !valid : false;
    },
    async handleCreateBounty() {
      const stripe = this.$refs.cardRef.stripe;
      const card = this.$refs.cardRef.element;
      this.loading = true;
      this.$refs.cardRef.submit()
      const clientSecret = await this.processPayment({
        amount: this.amount,
        currency: 'eur'
      });

      stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card,
          billing_details: {
            name: `${this.firstName} ${this.lastName}`
          }
        }
      }).then(async (result) => {
        if(result.error) {
          console.log(result.error)
          this.$root.$emit('showSnackbar', { color: 'error', message: result.error.message })
        } else {
          console.log(result)
          if (result.paymentIntent.status === 'succeeded') {
            await this.createGitBounty(this.amount);
            this.$root.$emit('showSnackbar', { color: 'success', message: 'Bounty Published!' })
          }
        }
        this.loading = false
      })
    }
  }
}
</script>

<style>

</style>
