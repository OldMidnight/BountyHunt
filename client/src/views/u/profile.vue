<template>
  <main-layout>
    <v-container>
      <v-row>
        <v-col v-if="current_bounty" cols="12" :class="{ 'caption': isMobile }">
          <div class="d-flex align-center">
            <h3 class="title">Current Bounty: </h3>
          </div>
          <v-row class="rounded border pa-2">
            <v-col cols="4" md="" :class="{ 'pb-0': isMobile }">
              <router-link
                :to="`/bounty/git/${current_bounty.url}`"
                target="_blank"
                class="font-weight-bold td-none"
              >
                {{ current_bounty.title }}
                <v-icon small>mdi-open-in-new</v-icon>
              </router-link>
            </v-col>
            <v-col v-if="!isMobile">
              <v-icon>mdi-account</v-icon>
              <router-link :to="`/u/${current_bounty.author}`" class="td-none">
                Creator: {{ current_bounty.author }}
              </router-link>
            </v-col>
            <v-col cols="3" md="" :class="{ 'pb-0 px-0': isMobile }">
              <span class="font-weight-bold">
                Bounty: <span class="green--text text--darken-1">€{{ convertCents(current_bounty.amount) }}</span>
              </span>
            </v-col>
            <v-col cols="4" md="" :class="{ 'pb-0 px-0': isMobile }">
              <span><b>Created</b>: {{ relativeTime(current_bounty.created) }}</span>
            </v-col>
            <v-col :class="{ 'py-0': isMobile }">
              <span><b>Assigned for</b>: {{ duration }} Day(s)</span>
            </v-col>
            <v-col cols="12" md="" :class="{ 'py-0': isMobile }">
              <router-link
                v-if="user.username === $route.params.user"
                :to="`${bountyViewURL(current_bounty)}/hunter`"
                class="td-none"
              >
                Manage
              </router-link>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12">
          <v-divider></v-divider>
        </v-col>
        <v-col cols="12">
          <div class="d-flex flex-column">
            <span class="title">My Bounties</span>
            <span class="subtitle-2">Your own creations. Bounties you made to complete an itch you had</span>
          </div>
          <v-row v-if="user_bounties.length > 0">
            <v-col
              v-for="bounty in user_bounties"
              :key="bounty.title"
              :class="{'caption': isMobile }"
              md="6"
              cols="12"
            >
              <v-row class="border rounded mx-2">
                <v-col cols="" class="d-flex pl-6 align-center">
                  <v-icon v-if="bounty.is_git_bounty" color="black" class="mr-2">mdi-github</v-icon>
                  <router-link :to="bountyViewURL(bounty)" class="td-none">{{ bounty.title | truncate(15, '...') }}</router-link>
                </v-col>
                <v-col class="d-flex justify-center align-center">
                  <span>Created: {{ relativeTime(bounty.created) }}</span>
                </v-col>
                <v-col class="d-flex justify-center align-center">
                  <span>
                    Bounty: <span class="green--text text--darken-1">€{{ convertCents(bounty.amount) }}</span>
                  </span>
                </v-col>
                <v-col class="d-flex align-center justify-end">
                  <v-btn
                    v-if="user.username === $route.params.user"
                    color="primary"
                    text
                    small
                    :to="`${bountyViewURL(bounty)}/manage`"
                  >
                    Manage
                  </v-btn>
                  <v-btn
                    v-if="user.username === $route.params.user"
                    color="primary"
                    class="mx-1"
                    outlined
                    small
                    @click="handleManageInvestment(bounty)"
                  >
                    View Submission
                  </v-btn>
                  <v-tooltip
                    v-if="!bounty.decision_datetime && bounty.is_submit && user.username === $route.params.user"
                    top
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon
                        color="warning"
                        class="ml-2"
                        v-bind="attrs"
                        v-on="on"
                      >
                        mdi-alert-circle
                      </v-icon>
                    </template>
                    Submission Pending Approval
                  </v-tooltip>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          <v-row v-else>
            <v-col cols="12">
              <v-btn color="primary" text to="/bounty/create">Create A Bounty</v-btn>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" v-if="invested_bounties.length > 0">
          <div class="d-flex flex-column">
            <span class="title">Investments</span>
            <span class="subtitle-2">Bounties you have invested in</span>
          </div>
          <v-row>
            <v-col
              v-for="bounty in invested_bounties"
              :key="bounty.title"
              class="py-0"
              :class="{'caption my-1': isMobile }"
              cols="12"
              md="6"
            >
              <v-row class="border rounded mx-2">
                <v-col cols="3" class="d-flex pl-6 align-center">
                  <v-icon v-if="bounty.is_git_bounty" color="black" class="mr-2">mdi-github</v-icon>
                  <router-link :to="bountyViewURL(bounty)" class="td-none">{{ bounty.title }}</router-link>
                </v-col>
                <v-col v-if="!isMobile" class="d-flex justify-center align-center">
                  <span>Created: {{ relativeTime(bounty.created) }}</span>
                </v-col>
                <v-col class="d-flex justify-center align-center">
                  <span>
                    Bounty: <span class="green--text text--darken-1">€{{ convertCents(bounty.amount) }}</span>
                  </span>
                </v-col>
                <v-col class="d-flex align-center justify-end">
                  <v-btn
                    v-if="user.username === $route.params.user"
                    color="primary"
                    class="mx-1"
                    outlined
                    small
                    @click="handleManageInvestment(bounty)"
                  >
                    View Submission
                  </v-btn>
                  <v-tooltip
                    v-if="!bounty.decision_datetime && bounty.is_submit && user.username === $route.params.user"
                    top
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon
                        color="warning"
                        class="ml-2"
                        v-bind="attrs"
                        v-on="on"
                      >
                        mdi-alert-circle
                      </v-icon>
                    </template>
                    Submission Pending Approval
                  </v-tooltip>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" v-if="completed_bounties.length > 0">
          <div class="d-flex flex-column">
            <span class="title">Completed Bounties</span>
            <span class="subtitle-2">Bounties that you have completed as a Bounty Hunter</span>
          </div>
          <v-row>
            <v-col
              v-for="bounty in completed_bounties"
              :key="bounty.title"
              class="py-0"
              :class="{'caption my-1': isMobile }"
              cols="12"
              md="6"
            >
              <v-row class="border rounded mx-2">
                <v-col cols="3" class="d-flex pl-6 align-center">
                  <v-icon v-if="bounty.is_git_bounty" color="black" class="mr-2">mdi-github</v-icon>
                  <router-link :to="bountyViewURL(bounty)" class="td-none">{{ bounty.title }}</router-link>
                </v-col>
                <v-col class="d-flex justify-center align-center">
                  <span>Created: {{ relativeTime(bounty.created) }}</span>
                </v-col>
                <v-col class="d-flex justify-center align-center">
                  <span>
                    Bounty: <span class="green--text text--darken-1">€{{ convertCents(bounty.amount) }}</span>
                  </span>
                </v-col>
                <v-col class="d-flex align-center justify-end">
                  <v-btn
                    v-if="user.username === $route.params.user"
                    color="primary"
                    class="mx-1"
                    text
                    small
                    :to="`${bountyViewURL(bounty)}/hunter`"
                  >
                    Manage
                  </v-btn>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
    <v-dialog
      v-model="manage_investment"
      :width="selected_bounty.is_submit ? 500 : 300"
    >
      <v-card>
        <v-card-title>Manage Investment</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <span class="font-weight-bold">
                Invested: <span class="green--text text--darken-2">€{{ convertCents(amount_invested) }}</span>
              </span>
            </v-col>
            <v-col cols="12">
              <span v-if="!selected_bounty.is_submit">No Pending Submission</span>
              <v-row v-else-if="!selected_bounty.decision_datetime">
                <v-col>
                  <v-textarea
                    filled
                    :value="selected_bounty.submission_description"
                    label="Submission Description"
                    readonly
                    hint="Read only"
                    persistent-hint
                  ></v-textarea>
                  <v-btn
                    color="primary"
                    :href="selected_bounty.submission_link"
                    target="_blank"
                    small
                  >
                    <v-icon class="mr-2" small>mdi-open-in-new</v-icon>
                    Submission Link
                  </v-btn>
                </v-col>
              </v-row>
              <span v-else>Submission {{ selected_bounty.is_approved ? 'Approved' : 'Denied' }}</span>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions v-if="!selected_bounty.decision_datetime && selected_bounty.is_submit">
          <v-spacer></v-spacer>
          <v-btn
            color="blue darken-1"
            text
            :loading="loading"
            @click="handleSubmission(true)"
          >
            Approve
          </v-btn>
          <v-btn
            color="red darken-1"
            text
            :loading="loading"
            @click="handleSubmission(false)"
          >
            Decline
          </v-btn>
        </v-card-actions>
        <v-card-actions v-else>
          <v-spacer></v-spacer>
          <v-btn
            color="blue darken-1"
            text
            @click="manage_investment = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </main-layout>
</template>

<script>
import MainLayout from '@/components/layouts/MainLayout'
import { mapActions, mapGetters } from 'vuex'
import { convertCents, relativeTime } from '@/helpers'
export default {
  components: { MainLayout },
  data: () =>({
    duration: 0,
    user_bounties: [],
    invested_bounties: [],
    completed_bounties: [],
    manage_investment: false,
    selected_bounty: {},
    amount_invested: 0,
    loading: false
  }),
  computed: {
    ...mapGetters({
      current_bounty: 'bounty/current_bounty',
      categories: 'bounty/categories',
      user: 'auth/user'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    bountyViewURL() {
      return (bounty) => bounty.is_git_bounty ? `/bounty/git/${bounty.url}` : `/bounty/${bounty.url}`
    }
  },
  async beforeMount() {
    await this.loadPageData(this.$route.params.user)
  },
  watch: {
    async $route(to) {
      await this.loadPageData(to.params.user)
    }
  },
  methods: {
    convertCents,
    relativeTime,
    ...mapActions({
      fetchCurrentBounty: 'bounty/fetchCurrentBounty',
      fetchBountyList: 'bounty/fetchBountyList',
      fetchUserBountyInvestment: 'bounty/fetchUserBountyInvestment',
      approveBounty: 'bounty/approveBounty',
      fetchUserApproval: 'bounty/fetchUserApproval'
    }),
    async loadPageData(user) {
      await this.getUserCurrentBounty()
      await this.getUserBounties(user)
    },
    async getUserCurrentBounty() {
      if (this.current_bounty) {
        const created_date = new Date(this.current_bounty.created)
        const today = new Date(Date.now())
        const difference_ms = today.getTime() - created_date.getTime()

        this.duration = Math.round(difference_ms/(1000*60*60*24))
      }
    },
    async getUserBounties(user) {
      const user_bounties = []
      let invested_bounties = []
      const completed_bounties = []

      const options = {
        u: user,
        count: 12,
        page: 1
      }
      let bounties = await this.fetchBountyList(options)
      bounties.forEach(async (bounty) => {
        const approval_data = await this.fetchUserApproval({
          bounty_url: bounty.url,
          username: this.user.username
        })
        user_bounties.push({...bounty, ...approval_data})
      })

      bounties = await this.fetchBountyList({...options, completed: true})
      completed_bounties.push(...bounties)

      bounties = await this.fetchBountyList({...options, i: true})

      bounties.forEach(async (bounty) => {
        const approval_data = await this.fetchUserApproval({
          bounty_url: bounty.url,
          username: this.user.username
        })
        if (bounty.user_id !== this.user.user_id) {
          invested_bounties.push({...bounty, ...approval_data})
        }
      })

      this.user_bounties = user_bounties
      this.invested_bounties = invested_bounties
      this.completed_bounties = completed_bounties
    },
    async handleManageInvestment(bounty) {
      this.selected_bounty = bounty
      const amount = await this.fetchUserBountyInvestment(bounty.url)
      this.amount_invested = amount
      this.manage_investment = true
    },
    async handleSubmission(is_approved) {
      this.loading = true
      const response = await this.approveBounty({
        bounty_url: this.selected_bounty.url,
        is_approved
      })

      switch (response.status) {
        case 400:
          this.$root.$emit('showSnackbar', { color: 'error', message: response.data.msg });
          break;

        case 201:
          this.$root.$emit('showSnackbar', { color: 'success', message: response.data.msg });
          this.manage_investment = false
          this.selected_bounty = {}
          break;
      
        default:
          this.$root.$emit('showSnackbar', { color: 'error', message: 'An error has occurred' });
          break;
      }
      this.loading = false
      await this.loadPageData(this.$route.params.user)
    }
  }
}
</script>

<style lang="scss" scoped>

</style>