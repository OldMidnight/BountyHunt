<template>
  <validation-observer v-slot="{ invalid }">
    <main-layout>
      <v-container>
        <v-row>
          <v-col cols="12" md="7" class="border rounded">
            
            <v-row class="px-3">
              <v-col cols="12">
                <div class="d-flex align-center">
                  <v-icon :color="currentIssue.state === 'open' ? 'success' : 'error'">
                    mdi-alert-circle-outline
                  </v-icon>
                  <span :class="`${isMobile ? 'body-1' : 'display-1'} ml-2`">
                    {{ currentIssue.title }}
                  </span>
                  <span :class="`${isMobile ? 'subtitle-2' : 'title'} ml-2 text--secondary`">
                    #{{ currentIssue.number }}
                  </span>
                  <v-btn
                    v-if="!bounty.is_submit"
                    color="primary"
                    class="ml-auto"
                    outlined
                    :x-small="isMobile"
                    @click="turning_in = true"
                  >
                    Turn In
                  </v-btn>
                  <v-btn
                    v-else
                    color="primary"
                    class="ml-auto"
                    outlined
                    :x-small="isMobile"
                    @click="turning_in = true"
                  >
                    View submission details
                  </v-btn>
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
          <v-col cols="12" md="3" :class="{ 'ml-12': !isMobile }">
            <v-row class="border rounded px-8">
              <v-col cols="12">
                <div>
                  <h1 class="display-3 text-center">€{{ convertCents(bounty.amount) }}</h1>
                </div>
                <div class="d-flex justify-center">
                  <span class="mr-3 overline">Duration: {{ duration }} days</span>
                  <span class="ml-3 overline">
                    Author: <router-link :to="`/u/${bounty.author}`" class="td-none">{{ bounty.author }}</router-link>
                  </span>
                </div>
              </v-col>
              <v-col cols="12" class="d-flex flex-column">
                <span class="overline text-center">Investors</span>
                <v-divider></v-divider>
                <v-list>
                  <v-list-item-group>
                    <v-list-item
                      v-for="i in investments"
                      :key="i.investment_id"
                      :to="`/u/${i.username}`"
                    >
                      <v-list-item-content>
                        <v-list-item-title class="font-weight-bold">
                          {{ i.username }} - <v-chip small :color="approval_color(i.approval_data)">{{ approval_text(i.approval_data) }}</v-chip>
                        </v-list-item-title>
                      </v-list-item-content>
                      <v-list-item-action class="green--text text--darken-1 font-weight-bold">
                        €{{ convertCents(i.amount) }}
                      </v-list-item-action>
                    </v-list-item>
                  </v-list-item-group>
                </v-list>
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12" class="d-flex justify-center">
                <span class="overline font-weight-bold">Status: {{ bounty_status }}</span>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
      <v-dialog
        v-model="turning_in"
        fullscreen
      >
        <v-card>
          <v-toolbar
            dark
            color="primary"
          >
            <v-btn
              icon
              dark
              @click="turning_in = false"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
            <v-toolbar-title>{{ bounty.title }}</v-toolbar-title>
          </v-toolbar>
          <v-container>
            <v-row class="d-flex justify-center">
              <v-col cols="11" md="6">
                <h3 class="title mb-4">Turn in Bounty</h3>
                <v-form>
                  <div>
                    <span class="subtitle-2">
                      Use the below space to write a brief description of the bounty deliverable. Cover any issues that may arise as well as a brief how-to if neccessary
                    </span>
                    <v-textarea
                      v-if="bounty.is_submit && !editing"
                      filled
                      counter="1000"
                      label="Description"
                      :value="bounty.submission_description"
                      disabled
                    ></v-textarea>
                    <validation-provider
                      v-else
                      name="description"
                      :rules="rules.description"
                      v-slot="validationContext"
                    >
                      <v-textarea
                        v-model="submission.description"
                        filled
                        counter="1000"
                        label="Description"
                        :error="getValidationState(validationContext)"
                        :error-messages="validationContext.errors[0]"
                        :disabled="loading"
                      ></v-textarea>
                    </validation-provider>
                  </div>
                  <div>
                    <span class="subtitle-2">
                      Enter a link to the bounty deliverable
                    </span>
                    <v-text-field
                      v-if="bounty.is_submit && !editing"
                      filled
                      label="Link"
                      :value="bounty.submission_link"
                      disabled
                    ></v-text-field>
                    <validation-provider
                      v-else
                      name="link"
                      :rules="rules.link"
                      v-slot="validationContext"
                    >
                      <v-text-field
                        v-model="submission.link"
                        filled
                        label="Link"
                        :error="getValidationState(validationContext)"
                        :error-messages="validationContext.errors[0]"
                        :disabled="loading"
                      ></v-text-field>
                    </validation-provider>
                  </div>
                  <p class="caption">
                    After turning in this bounty, the bounty investors will be made aware that it has been submitted and will vote on whether it works as expected. If there are any issues, a BountyHunt representative will get in touch to organise a second version.
                  </p>
                  <v-btn
                    v-if="bounty.is_submit && !editing"
                    color="primary"
                    :disabled="invalid || bounty.completed"
                    :loading="loading"
                    @click="handleEditBounty"
                  >
                    Edit
                  </v-btn>
                  <v-btn
                    v-else
                    color="primary"
                    :disabled="invalid || bounty.completed"
                    :loading="loading"
                    @click="handleSubmitBounty"
                  >
                    Submit
                  </v-btn>
                </v-form>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-dialog>
    </main-layout>
  </validation-observer>
</template>

<script>
import { ValidationObserver, ValidationProvider } from 'vee-validate'
import MainLayout from '@/components/layouts/MainLayout.vue'
import { mapActions, mapGetters } from 'vuex'
import { convertCents, relativeTime } from '@/helpers'
import marked from 'marked'
export default {
  components: { MainLayout, ValidationObserver, ValidationProvider },
  data: () => ({
    loading: false,
    editing: false,
    submission: {
      description: null,
      link: null
    },
    turning_in: false,
    rules: {
      description: {
        required: true,
        max: 1000
      },
      link: {
        required: true,
        regex: /(?:http|Http|Https|https):\/\/[a-zA-Z0-9\-.]+\.[a-zA-Z]{2,3}(\/\S*)?/
      }
    },
    investments: [],
    duration: 0
  }),
  computed: {
    ...mapGetters({
      bounty: 'bounty/bounty',
      currentIssue: 'git/currentIssue',
      currentIssueComments: 'git/currentIssueComments'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    approval_color() {
      return (approval_data) => approval_data && approval_data.decision_datetime ? approval_data.is_approved ? 'success' : 'error' : ''
    },
    approval_text() {
      return (approval_data) => approval_data && approval_data.decision_datetime ? approval_data.is_approved ? 'Approved' : 'Denied' : 'Pending'
    },
    bounty_status() {
      return this.bounty.completed ? 'Completed' : this.bounty.is_submit ? 'Submission Pending Approval' : 'In Progress'
    },
    compiledMarkdown() {
      return (text) => marked(text, { breaks: true })
    }
  },
  async created() {
    this.sortInvestments()

    const created_date = new Date(this.bounty.created)
    const today = new Date(Date.now())
    const difference_ms = today.getTime() - created_date.getTime()

    this.duration = Math.round(difference_ms/(1000*60*60*24))
  },
  methods: {
    convertCents,
    relativeTime,
    ...mapActions({
      fetchGitBounty: 'bounty/fetchGitBounty',
      submitBounty: 'bounty/submitBounty',
      fetchUserApproval: 'bounty/fetchUserApproval'
    }),
    async sortInvestments() {
      const sorted_investments = this.bounty.investments.sort((inv_a, inv_b) => inv_a.amount - inv_b.amount)
      const investments = {}

      sorted_investments.forEach((investment) => {
        if (investments[investment.user_id]) {
          investments[investment.user_id].amount += investment.amount
        } else {
          investments[investment.user_id] = investment
        }
      })

      for (const user of Object.keys(investments)) {
        const approval_data = await this.fetchUserApproval({
          bounty_url: this.bounty.url,
          username: investments[user].username
        })
        investments[user].approval_data = approval_data
      }

      this.investments = investments
    },
    handleEditBounty() {
      this.submission.description = this.bounty.submission_description
      this.submission.link = this.bounty.submission_link
      this.editing = true
    },
    async handleSubmitBounty() {
      this.loading = true
      const response = await this.submitBounty({
        bounty_url: this.bounty.url,
        submission: this.submission
      })

      switch (response.status) {
        case 403, 400:
          this.$root.$emit('showSnackbar', { color: 'error', message: response.data.msg });
          break;

        case 200:
          this.turning_in = false
          this.$root.$emit('showSnackbar', { color: 'success', message: response.data.msg });
          break;
      
        default:
          this.$root.$emit('showSnackbar', { color: 'error', message: 'An error has occurred' });
          break;
      }

      await this.fetchGitBounty(this.bounty.url);
      this.loading = false
    },
    getValidationState({ dirty, validated, valid = null}) {
      return dirty || validated ? !valid : false;
    }
  }
}
</script>

<style>

</style>