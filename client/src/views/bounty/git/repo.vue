<template>
  <main-layout>
    <v-container :class="`${isMobile ? 'm-' : ''}git-creation-container`">
      <v-row>
        <v-col cols="12" class="pa-0">
          <router-link class="text--secondary caption" to="/bounty/create/git">
            <v-icon small>mdi-arrow-left</v-icon>Back
          </router-link>
        </v-col>
        <v-col cols="12" md="4" class="border rounded d-flex flex-column pa-0">
          <div class="pa-3 d-flex flex-column">
            <span class="subtitle-2">{{ repoNameSplit[0] }}/</span>
            <span class="display-2">
              {{ repoNameSplit[1] }} <v-icon color="black" large>mdi-github</v-icon>
            </span>
            <span class="mt-3">{{ currentRepo.description }}</span>
            <div class="mt-3 mb-4">
              <span class="overline mr-2">Owner:</span>
              <a :href="currentRepo.owner.url">
                <v-avatar size="30" class="border">
                  <v-img :src="currentRepo.owner.avatar_url"></v-img>
                </v-avatar>
              </a>
            </div>
          </div>
          <v-divider></v-divider>
          <div class="d-flex flex-column my-4 justify-center align-center">
            <span class="display-2">€{{ convertCents(currentRepo.amount) }}</span>
            <span class="mt-3">EUR Raised</span>
          </div>
        </v-col>
        <v-col cols="12" md="8">
          <div class="d-flex w-50">
            <v-text-field
              v-model="issueSearchString"
              outlined
              dense
              label="Search Issues..."
              :loading="loading"
              @keypress.enter="searchIssues"
            ></v-text-field>
          </div>
          <v-data-iterator
            :items="currentRepoIssues"
            :items-per-page.sync="issuesPerPage"
            :page.sync="issuePage"
            :loading="loading"
            hide-default-footer
          >
            <template v-slot:default="props">
              <v-container>
                <v-row
                  v-for="(item, index) in props.items"
                  :key="index"
                  class="border"
                >
                  <v-col v-if="!isMobile" md="1">
                    <v-avatar>
                      <v-img :src="item.user.avatar_url"></v-img>
                    </v-avatar>
                  </v-col>
                  <v-col cols="11" md="">
                    <div>
                      <v-icon color="success" small class="mr-1">
                        mdi-alert-circle-outline
                      </v-icon>
                      <router-link class="body-1" :to="issueRoute(item)">{{ item.title }}</router-link>
                    </div>
                    <div>
                      <v-chip label x-small class="font-weight-bold" :color="item.is_bounty ? 'success' : ''">
                        {{ item.is_bounty ? 'Bounty Created' : 'No Bounty' }}
                      </v-chip>
                      <span class="caption mx-1">#{{ item.number }}</span>
                      <span class="caption">created by {{ item.user.login | truncate(11, '...') }}</span>
                    </div>
                  </v-col>
                  <v-col cols="1" md="" class="d-flex justify-end align-center">
                    <span class="title mr-5">
                      €{{ item.is_bounty ? `${convertCents(item.bounty_amount)}` : '0' }}
                    </span>
                  </v-col>
                </v-row>
              </v-container>
            </template>
            <template v-slot:footer>
              <v-row
                class="ml-2"
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
                      {{ issuesPerPage }}
                      <v-icon>mdi-chevron-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item
                      v-for="(number, index) in issuesPerPageArray"
                      :key="index"
                      @click="updateItemsPerPage(number)"
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
                  Page {{ issuePage }} of {{ numberOfIssuePages }}
                </span>
                <v-btn
                  icon
                  small
                  dark
                  color="blue darken-3"
                  class="mr-1"
                  :disabled="issuePage === numberOfIssuePages"
                  @click="formerPage"
                >
                  <v-icon>mdi-chevron-left</v-icon>
                </v-btn>
                <v-btn
                  icon
                  small
                  dark
                  color="blue darken-3"
                  class="ml-1"
                  :disabled="issuePage === numberOfIssuePages"
                  @click="nextPage"
                >
                  <v-icon>mdi-chevron-right</v-icon>
                </v-btn>
              </v-row>
            </template>
          </v-data-iterator>
        </v-col>
      </v-row>
    </v-container>
  </main-layout>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import MainLayout from '@/components/layouts/MainLayout';
import { convertCents } from '@/helpers'
export default {
  components: {
    MainLayout
  },
  data: () => ({
    issuesPerPageArray: [10, 25, 50],
    issuePage: 1,
    issuesPerPage: 10,
    issueSearchString: '',
    loading: false
  }),
  computed: {
    ...mapGetters({
      currentRepo: 'git/currentRepo',
      currentRepoIssues: 'git/currentRepoIssues',
      currentRepoIssuesCount: 'git/currentRepoIssuesCount'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    repoNameSplit() {
      return this.currentRepo.full_name.split('/')
    },
    issueRoute() {
      return (issue) => issue.is_bounty ? 
        `/bounty/git/${this.currentRepo.full_name}/issues/${issue.number}` :
        `/bounty/create/git/${this.currentRepo.full_name}/issues/${issue.number}`
    },
    numberOfIssuePages() {
      return Math.ceil(this.currentRepoIssuesCount / this.issuesPerPage)
    }
  },
  methods: {
    ...mapActions({
      githubSearchIssues: 'git/githubSearchIssues'
    }),
    convertCents,
    async searchIssues() {
      this.loading = true
      await this.githubSearchIssues({
        repo: this.currentRepo.full_name,
        searchString: this.issueSearchString
      })
      this.loading = false
    },
    nextPage () {
      if (this.repoPage + 1 <= this.numberOfGitRepoPages) this.repoPage += 1
    },
    formerPage () {
      if (this.repoPage - 1 >= 1) this.repoPage -= 1
    },
    updateItemsPerPage (number) {
      this.reposPerPage = number
    }
  }
};
</script>

<style>

</style>