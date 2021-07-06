<template>
  <main-layout>
    <v-container :class="`${isMobile ? 'm-' : ''}git-creation-container`">
      <v-row class="d-flex justify-center">
        <v-col md="5" cols="12" class="d-flex flex-column align-center">
          <span class="display-1">Select Repository</span>
          <div class="d-flex align-center">
            <v-text-field
              v-model="github_search_string"
              label="Repository Name"
              class="mt-4"
              filled
              @keydown.enter="searchRepository"
            ></v-text-field>
            <v-btn
              fab
              small
              color="primary"
              class="mb-2 ml-2"
              @click="searchRepository"
            >
              <v-icon>mdi-arrow-right</v-icon>
            </v-btn>
          </div>
          <span class="overline mb-3">- or -</span>
          <v-btn color="primary" @click="showRepoDialog = true">
            Add your Repositories
          </v-btn>
        </v-col>
        <v-col cols="12">
          <div>
            <v-data-iterator
              :items="repos.items"
              :items-per-page.sync="reposPerPage"
              :page.sync="repoPage"
              hide-default-footer
              :loading="loading"
            >
              <template v-slot:default="props">
                <v-container>
                  <v-row
                    v-for="(item, index) in props.items"
                    :key="index"
                    class="border"
                  >
                    <v-col cols="2" md="1">
                      <v-img :src="item.owner_avatar_url" :width="isMobile ? '50px' : ''"></v-img>
                    </v-col>
                    <v-col cols="10" md="9" class="d-flex flex-column justify-center">
                      <a
                        :href="isMobile ? `/bounty/create/git/${item.full_name}` : item.html_url"
                        :target="isMobile ? '' : '_blank'"
                        :class="`${isMobile ? 'caption' : 'title'}`"
                      >
                        {{ item.full_name }} <v-chip class="ml-2" :small="!isMobile" :x-small="isMobile">{{ item.language }}</v-chip>
                      </a>
                      <span class="caption">{{ item.description }}</span>
                    </v-col>
                    <v-col v-if="!isMobile" md="2" class="d-flex align-center">
                      <v-btn
                        tile
                        color="primary"
                        @click="selectRepo(item)"
                      >Select</v-btn>
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
                        {{ reposPerPage }}
                        <v-icon>mdi-chevron-down</v-icon>
                      </v-btn>
                    </template>
                    <v-list>
                      <v-list-item
                        v-for="(number, index) in reposPerPageArray"
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
                    Page {{ repoPage }} of {{ numberOfRepoPages }}
                  </span>
                  <v-btn
                    icon
                    small
                    dark
                    color="blue darken-3"
                    class="mr-1"
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
                    @click="nextPage"
                  >
                    <v-icon>mdi-chevron-right</v-icon>
                  </v-btn>
                </v-row>
              </template>
            </v-data-iterator>
          </div>
        </v-col>
      </v-row>
    </v-container>
    <v-dialog
      v-model="showRepoDialog"
      max-width="800"
      :fullscreen="isMobile"
    >
      <git-repo-dialog @reposAdded="handleReposAdded"></git-repo-dialog>
    </v-dialog>
  </main-layout>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import MainLayout from '@/components/layouts/MainLayout';
import GitRepoDialog from '@/components/GitRepoDialog';
export default {
  components: {
    MainLayout,
    GitRepoDialog
  },
  data: () => ({
    github_search_string: '',
    reposPerPageArray: [10, 25, 50],
    repoPage: 1,
    reposPerPage: 10,
    showRepoDialog: false,
    loading: false
  }),
  computed: {
    ...mapGetters({
      repos: 'git/repos',
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    numberOfRepoPages() {
      return Math.ceil(this.repos.total / this.reposPerPage)
    }
  },
  async mounted() {
    this.loading = true
    await this.githubSearchRepos({
      q: this.github_search_string,
      page: this.repoPage,
      perPage: this.reposPerPage
    })
    this.loading = false
  },
  methods: {
    ...mapActions({
      githubSearchRepos: 'git/githubSearchRepos',
      fetchCurrentRepo: 'git/fetchCurrentRepo'
    }),
    async searchRepository() {
      this.loading = true
      await this.githubSearchRepos({
        q: this.github_search_string,
        page: this.repoPage,
        perPage: this.reposPerPage
      })
        .then(() => this.loading = false)
    },
    nextPage () {
      if (this.repoPage + 1 <= this.numberOfGitRepoPages) this.repoPage += 1
    },
    formerPage () {
      if (this.repoPage - 1 >= 1) this.repoPage -= 1
    },
    updateItemsPerPage (number) {
      this.reposPerPage = number
    },
    selectRepo(repo) {
      this.$router.push(`/bounty/create/git/${repo.full_name}`)
    },
    async handleReposAdded() {
      await this.searchRepository()
      this.showRepoDialog = false
    }
  }
};
</script>

<style lang="scss" scoped>
</style>