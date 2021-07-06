<template>
  <validation-observer v-slot="{ invalid }">
    <v-row class="d-flex justify-center">
      <v-col md="6" cols="12">
        <v-card>
          <v-card-title class="display-1 mb-2">
            {{ bounty.title }}
          </v-card-title>
          <v-card-subtitle class="subtitle">
            {{ bounty.description }}
          </v-card-subtitle>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="">
                  <span class="title">Categories</span>
                  <div class="d-flex flex-row">
                    <v-chip v-for="(category, index) in bounty.selected_categories" :key="index" class="mx-2" label>
                      {{ category[0] }}
                    </v-chip>
                  </div>  
                </v-col>
                <v-col cols="">
                  <span class="title">Reward: <b>{{ formatAmount }}</b></span>
                </v-col>
                <v-col cols="12" v-if="bounty.external_links.length > 0">
                  <span class="title">External Links</span>
                  <v-simple-table>
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th class="text-left">
                            URL
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="(link, index) in bounty.external_links"
                          :key="index"
                        >
                          <td>{{ link.url }}</td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </v-col>
                <v-col cols="12">
                  <span class="title">Bounty Options</span>
                  <v-checkbox
                    :input-value="allow_multiple_investors"
                    value
                    label="Allow Multiple Investors"
                    disabled
                  ></v-checkbox>
                </v-col>
                <v-col cols="12" class="pa-0">
                  <v-divider></v-divider>
                </v-col>
                <v-col cols="12" class="pb-0">
                  <span class="subtitle-1">
                    Bounty issued by: <b>{{ user.username }}</b>
                  </span>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col md="6" cols="11" :class="{'mt-3': isMobile}">
        <span>Payment details</span>
        <v-form>
          <v-row>
            <v-col cols="6" class="pb-0">
              <validation-provider
                name="first_name"
                :rules="rules.names"
                v-slot="validationContext"
              >
                <v-text-field
                  v-model="first_name"
                  label="First Name"
                  outlined
                  dense
                  :error="getValidationState(validationContext)"
                  :error-messages="validationContext.errors[0]"
                ></v-text-field>
              </validation-provider>
            </v-col>
            <v-col cols="6" class="pb-0">
              <validation-provider
                name="last_name"
                :rules="rules.names"
                v-slot="validationContext"
              >
                <v-text-field
                  v-model="last_name"
                  label="Last Name"
                  outlined
                  dense
                  :error="getValidationState(validationContext)"
                  :error-messages="validationContext.errors[0]"
                ></v-text-field>
              </validation-provider>
            </v-col>
            <v-col cols="12" class="py-0">
              <v-switch v-model="allow_multiple_investors" label="Allow user contribution"></v-switch>
              <validation-provider
                name="amount"
                :rules="rules.amount"
                v-slot="validationContext"
              >
                <v-text-field
                  v-model="amount"
                  label="Bounty Amount"
                  outlined
                  dense
                  prefix="€"
                  type="number"
                  :error="getValidationState(validationContext)"
                  :error-messages="validationContext.errors[0]"
                ></v-text-field>
              </validation-provider>
            </v-col>
            <v-col cols="12">
              <stripe-element-card
                ref="cardRef"
                :pk="pulishable_key"
                :hidePostalCode="true"
              ></stripe-element-card>
              <div>
                <v-btn
                  color="info"
                  class="mx-2"
                  depressed
                  :disabled="loading || invalid"
                  :loading="loading"
                  @click="handleCreateBounty"
                >
                  Publish
                </v-btn>
                <v-btn
                  color="info"
                  class="mx-2"
                  depressed
                  :disabled="loading"
                  :loading="loading"
                  @click="editBounty"
                >
                  Edit
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-form>
      </v-col>
    </v-row>
  </validation-observer>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import { ValidationProvider, ValidationObserver } from 'vee-validate';
import { StripeElementCard } from '@vue-stripe/vue-stripe';
export default {
  name: 'BountyPreview',
  components: { StripeElementCard, ValidationProvider, ValidationObserver },
  data() {
    return {
      loading: false,
      first_name: null,
      last_name: null,
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
      allow_multiple_investors: true,
      pulishable_key: process.env.VUE_APP_STRIPE_PUBLISHABLE_KEY
    }
  },
  computed: {
    ...mapGetters({
      bounty: 'bounty/bounty',
      user: 'auth/user',
      currencies: 'bounty/currencies'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    formatAmount() {
      const currency = this.currencies.find(({ code }) => code === this.bounty.currency_code)
      return `${currency.symbol}${this.amount}`;
    },
  },
  methods: {
    ...mapActions({
      createBounty: 'bounty/createBounty',
      processPayment: 'payments/processPayment'
    }),
    editBounty() {
      this.$emit('reset');
    },
    async handleCreateBounty() {
      const stripe = this.$refs.cardRef.stripe;
      const card = this.$refs.cardRef.element;
      this.loading = true;
      this.$refs.cardRef.submit()
      const client_secret = await this.processPayment({
        amount: this.bounty.amount,
        currency: this.bounty.currency_code.toLowerCase()
      });

      stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card,
          billing_details: {
            name: `${this.first_name} ${this.last_name}`
          }
        }
      }).then(async (result) => {
        if(result.error) {
          console.log(result.error)
          this.$root.$emit('showSnackbar', { color: 'error', message: result.error.message })
        } else {
          console.log(result)
          if (result.paymentIntent.status === 'succeeded') {
            await this.createBounty({
              amount: this.amount,
              allow_multiple_investors: this.allow_multiple_investors
            });
            this.$root.$emit('showSnackbar', { color: 'success', message: 'Bounty Published!' })
          }
        }
        this.loading = false
      })
    },
    getValidationState({ dirty, validated, valid = null}) {
      return dirty || validated ? !valid : false;
    }
  }
}
</script>

<style>

</style>