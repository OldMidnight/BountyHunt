<template>
  <main-layout :class="`${isMobile ? 'm-' : ''}bounty-container`">
    <v-container>
      <v-row>
        <v-col cols="12" class="d-flex flex-column">
          <div>
            <span class="display-1 mr-6">{{ bounty.title }}</span>
            <v-btn
              color="primary"
              text
              :href="`/bounty/${bounty.url}`"
              target="_blank"            
            >
              Bounty Page
              <v-icon x-small>mdi-open-in-new</v-icon>
            </v-btn>
          </div>
          <span clas="subtitle">{{ bounty.description }}</span>
        </v-col>
        <v-col cols="12">
          <v-divider></v-divider>
        </v-col>
        <v-col v-if="assigned_hunter" cols="12">
          <span class="font-weight-bold title">Assigned Hunter:</span>
          <router-link
            color="primary"
            text
            plain
            :to="`/u/${assigned_hunter.username}`"
            target="_blank"
            class="font-weight-bold title"
          >
            {{ assigned_hunter.username }}
            <v-icon small>mdi-open-in-new</v-icon>
          </router-link>
        </v-col>
        <v-col cols="12" md="6">
          <span class="title">Bounty Hunters</span>
          <v-data-iterator
            :items="applications"
            :items-per-page.sync="applications_per_page"
            :page.sync="applications_page"
            :search="applications_search"
            :sort-by="applications_sort_by.toLowerCase()"
            :sort-desc="applications_sort_desc"
            hide-default-footer
          >
            <template v-slot:header>
              <v-toolbar
                dark
                color="blue darken-3"
                class="mb-1"
              >
                <v-text-field
                  v-model="applications_search"
                  clearable
                  flat
                  solo-inverted
                  hide-details
                  prepend-inner-icon="mdi-magnify"
                  label="Search"
                ></v-text-field>
                <template v-if="$vuetify.breakpoint.mdAndUp">
                  <v-spacer></v-spacer>
                  <v-select
                    v-model="applications_sort_by"
                    flat
                    solo-inverted
                    hide-details
                    :items="applications_keys"
                    item-value="text"
                    :item-text="(item) => item.format_text ? item.format_text : item.text"
                    prepend-inner-icon="mdi-magnify"
                    label="Sort by"
                  ></v-select>
                  <v-spacer></v-spacer>
                  <v-btn-toggle
                    v-model="applications_sort_desc"
                    mandatory
                  >
                    <v-btn
                      large
                      depressed
                      color="blue"
                      :value="false"
                    >
                      <v-icon>mdi-arrow-up</v-icon>
                    </v-btn>
                    <v-btn
                      large
                      depressed
                      color="blue"
                      :value="true"
                    >
                      <v-icon>mdi-arrow-down</v-icon>
                    </v-btn>
                  </v-btn-toggle>
                </template>
              </v-toolbar>
            </template>

            <template v-slot:default="props">
              <v-row>
                <v-col
                  v-for="item in props.items"
                  :key="item.username"
                  md="6"
                  cols="12"
                >
                  <v-card>
                    <v-card-title class="subheading font-weight-bold">
                      <span v-if="bounty.is_submit && approval_data.decision_datetime === null">
                        {{ item.username }}<v-chip color="warning" class="ml-2" x-small>Submission pending</v-chip>
                      </span>
                      <span v-else>
                        {{ item.username }}
                        <v-chip
                          v-if="bounty.is_submit"
                          :color="approval_data.is_approved ? 'success' : 'error'"
                          class="ml-2"
                          x-small
                        >
                          {{ approval_data.is_approved ? 'Approved' : 'Denied' }} Submission
                        </v-chip>
                      </span>
                      <v-spacer></v-spacer>
                      <v-btn
                        color="primary"
                        text
                        :href="`/u/${item.username}`"
                        target="_blank"
                        small
                      >
                        Visit Profile <v-icon small>mdi-open-in-new</v-icon>
                      </v-btn>
                    </v-card-title>

                    <v-divider></v-divider>

                    <v-list dense>
                      <v-list-item
                        v-for="(key, index) in filteredApplicationsKeys"
                        :key="index"
                      >
                        <v-list-item-content
                          :class="{ 'blue--text': applications_sort_by === key.text }"
                        >
                          {{ key.format_text || key.text }}:
                        </v-list-item-content>
                        <v-list-item-content
                          class="align-end"
                          :class="{ 'blue--text': applications_sort_by === key.text }"
                        >
                          {{ item[key.text.toLowerCase()] }}
                        </v-list-item-content>
                      </v-list-item>
                    </v-list>

                    <v-divider></v-divider>
                    
                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn
                        v-if="bounty.is_submit && bounty.assigned_user_id === item.user_id && !approval_data"
                        color="primary"
                        @click="approve_submission_dialog = true"
                      >
                        View Submission
                      </v-btn>
                      <v-btn
                        color="primary"
                        @click.native.stop="
                          application_user = item;
                          assigning = true
                        "
                        :disabled="bounty.assigned_user_id !== null"
                      >
                        {{ bounty.assigned_user_id === item.user_id ? 'Assigned' : 'Assign' }}
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </template>

            <template v-slot:footer>
              <v-row
                class="mt-2"
                align="center"
                justify="center"
              >
                <span class="grey--text">Items per page</span>
                <v-menu offset-y>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      dark
                      text
                      color="primary"
                      class="ml-2"
                      v-bind="attrs"
                      v-on="on"
                    >
                      {{ applications_per_page }}
                      <v-icon>mdi-chevron-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item
                      v-for="(number, index) in per_page_options"
                      :key="index"
                      @click="updateApplicationsPerPage(number)"
                    >
                      <v-list-item-title>{{ number }}</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>

                <v-spacer></v-spacer>

                <span
                  class="mr-4
                  grey--text"
                >
                  Page {{ applications_page }} of {{ numberOfApplicationPages }}
                </span>
                <v-btn
                  icon
                  dark
                  color="blue darken-3"
                  class="mr-1"
                  @click="prevPage"
                >
                  <v-icon>mdi-chevron-left</v-icon>
                </v-btn>
                <v-btn
                  icon
                  dark
                  color="blue darken-3"
                  class="ml-1"
                  @click="nextPage"
                >
                  <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
              </v-row>
            </template>
          </v-data-iterator>
        </v-col>
        <v-col cols="12" md="6">
          <span class="title">Investors</span>
          <v-data-table
            :headers="investor_headers"
            :items="investments"
            :items-per-page="5"
          >
            <template v-slot:[`item.amount`]="{ item }">
              <span>€{{ convertCents(item.amount) }}</span>
            </template>
            <template v-slot:[`item.actions`]="{ item }">
              <v-btn
                color="primary"
                text
                :href="`/u/${item.username}`"
                target="_blank"
                small
              >
                View
                <v-icon x-small>mdi-open-in-new</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
    <v-dialog
      v-model="assigning"
      persistent
      width="300"
    >
      <v-card>
        <v-card-title>Assign Bounty</v-card-title>
        <v-card-text class="d-flex flex-column">
          <span>
            Are you sure you want to assign this bounty to: <b>{{ application_user.username }}</b>?
          </span>
          <span class="mt-2">Once assigned this bounty will be closed to other Bounty Hunters.</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue darken-1"
            text
            @click="handleAssignBounty()"
          >
            Assign Bounty
          </v-btn>
          <v-btn
            color="red darken-1"
            text
            @click="dialog = false"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog
      v-model="approve_submission_dialog"
      width="500"
    >
      <v-card>
        <v-card-title>Approve Submission</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-row>
            <v-col>
              <v-textarea
                filled
                :value="bounty.submission_description"
                label="Submission Description"
                readonly
                hint="Read only"
                persistent-hint
              ></v-textarea>
              <v-btn
                color="primary"
                :href="bounty.submission_link"
                target="_blank"
                small
              >
                <v-icon class="mr-2" small>mdi-open-in-new</v-icon>
                Submission Link
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
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
      </v-card>
    </v-dialog>
  </main-layout>
</template>

<script>
import MainLayout from '@/components/layouts/MainLayout'
import { mapActions, mapGetters } from 'vuex';
import { convertCents } from '@/helpers'
export default {
  components: { MainLayout },
  data: () => ({
    applications: [],
    application_user: {},
    assigned_hunter: null,
    assigning: false,
    investments: [],
    applications_search: '',
    applications_sort_desc: false,
    applications_page: 1,
    applications_per_page: 2,
    per_page_options: [2, 4, 8],
    applications_sort_by: 'username',
    applications_keys: [
      { text: 'Username' },
      { text: 'Created', format_text: 'Applied' },
      { text: 'Application_Text', format_text: 'Application Message' }
    ],
    investor_headers: [
      {
        text: 'Investor',
        value: 'username'
      },
      {
        text: 'Amount',
        value: 'amount'
      },
      {
        text: 'Profile',
        value: 'actions',
        sortable: false
      }
    ],
    loading: false,
    approve_submission_dialog: false,
    approval_data: null
  }),
  computed: {
    ...mapGetters({
      bounty: 'bounty/bounty',
      user: 'auth/user'
    }),
    numberOfApplicationPages () {
      return this.applications ? Math.ceil(this.applications.length / this.applications_per_page) : 1
    },
    filteredApplicationsKeys () {
      return this.applications_keys.filter(key => key.text !== 'Username')
    }
  },
  async created() {
    await this.fetchBountyData();
    const approval_data = await this.fetchUserApproval({
      bounty_url: this.bounty.url,
      username: this.user.username
    })
    this.approval_data = approval_data

    this.applications = [...this.bounty.applications]
  },
  methods: {
    ...mapActions({
      fetchGitBounty: 'bounty/fetchGitBounty',
      assignBounty: 'bounty/assignBounty',
      fetchAssignedHunter: 'bounty/fetchAssignedHunter',
      approveBounty: 'bounty/approveBounty',
      fetchUserApproval: 'bounty/fetchUserApproval'
    }),
    convertCents,
    nextPage () {
      if (this.applications_page + 1 <= this.numberOfApplicationPages) this.applications_page += 1
    },
    prevPage () {
      if (this.applications_page - 1 >= 1) this.applications_page -= 1
    },
    updateApplicationsPerPage (number) {
      this.applications_per_page = number
    },
    sortInvestments() {
      const sorted_investments = {}
      const investments = []

      this.bounty.investments.forEach((investment) => {
        if (sorted_investments[investment.user_id]) {
          sorted_investments[investment.user_id].amount += investment.amount
        } else {
          sorted_investments[investment.user_id] = investment
        }
      })

      for (const investor_id of Object.keys(sorted_investments)) {
        investments.push(sorted_investments[investor_id])
      }
      this.investments = investments
    },
    async handleAssignBounty() {
      const response = await this.assignBounty({
        bounty_url: this.bounty.url,
        assigned_user_id: this.application_user.user_id
      })
      const status = response.status;

      switch (status) {
        case 400:
          this.$root.$emit('showSnackbar', { color: 'error', message: response.data.msg });
          break;

        case 200:
          this.$root.$emit('showSnackbar', { color: 'success', message: response.data.msg });
          break;
      
        default:
          this.$root.$emit('showSnackbar', { color: 'error', message: 'An error has occurred' });
          break;
      }

      await this.fetchBountyData();
      this.assigning = false
    },
    async fetchBountyData() {
      this.fetchGitBounty(this.bounty.url)
      if (this.bounty.assigned_user_id !== null) {
        const hunter_data = await this.fetchAssignedHunter(this.bounty.url);
        this.assigned_hunter = hunter_data;
      }
      this.sortInvestments()
    },
    async handleSubmission(is_approved) {
      this.loading = true
      const response = await this.approveBounty({
        bounty_url: this.bounty.url,
        is_approved
      })

      switch (response.status) {
        case 400:
          this.$root.$emit('showSnackbar', { color: 'error', message: response.data.msg });
          break;

        case 201:
          this.$root.$emit('showSnackbar', { color: 'success', message: response.data.msg });
          this.approve_submission_dialog = false
          break;
      
        default:
          this.$root.$emit('showSnackbar', { color: 'error', message: 'An error has occurred' });
          break;
      }
      this.loading = false
    }
  }
}
</script>

<style lang="scss" scoped>
a {
  text-decoration: none;
}
</style>