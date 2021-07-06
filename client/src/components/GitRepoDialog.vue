<template>
  <v-card>
    <v-toolbar
      v-if="isMobile"
      dark
      color="primary"
    >
      <v-btn
        icon
        dark
        @click="$emit('reposAdded')"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-toolbar>
    <v-card-title>Add Git Repositories</v-card-title>
    <v-card-subtitle>
      Add your git repositories to BountyHunt so others can create bounties using them
    </v-card-subtitle>
    <v-divider></v-divider>
    <v-card-text>
      <v-row>
        <v-col v-if="user.github_access_token" cols="12">
          <v-data-iterator
            :items="gitRepos"
            :search="search"
            disable-pagination
            hide-default-footer
            :loading="loading"
          >
            <template v-slot:header>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="search"
                    prepend-inner-icon="mdi-magnify"
                    label="Search"
                    clearable
                    outlined
                    dense
                  ></v-text-field>
                </v-col>
                <v-col cols="6" class="d-flex justify-end align-center">
                  <v-checkbox
                    :label="selectionText"
                    @change="selectAllRepos($event)"
                  ></v-checkbox>
                  <v-btn
                    color="primary"
                    class="ml-3"
                    :disabled="selectedRepos.length === 0"
                    @click="addRepos"
                  >
                    Add {{ selectedRepos.length }}
                  </v-btn>
                </v-col>
              </v-row>
            </template>
            <template v-slot:default="props">
              <v-container class="pt-0">
                <v-row
                  v-for="(item, index) in props.items"
                  :key="index"
                  class="border"
                >
                  <v-col cols="8" md="10" class="d-flex align-center py-0">
                    <v-avatar size="30" v-if="!isMobile">
                      <v-img :src="item.owner.avatar_url"></v-img>
                    </v-avatar>
                    <div :class="`d-flex ${isMobile ? 'flex-column' : 'align-center'}`">
                      <a
                        v-if="repoAdded(item.full_name)"
                        :class="`ml-3 ${isMobile ? 'caption' : 'title'}`"
                        :href="`/bounty/create?repo=${item.full_name}`"
                      >
                        {{ item.full_name }}
                      </a>
                      <span v-else :class="`ml-3 ${isMobile ? 'caption' : 'title'}`">
                        {{ item.full_name }}
                      </span>
                      <div>
                        <v-chip v-if="item.language" x-small class="mx-2">
                          {{ item.language }}
                        </v-chip>
                        <span>
                          (<v-icon small>mdi-star</v-icon>{{ item.stargazers_count }}, <v-icon small>mdi-eye</v-icon>{{ item.watchers_count }})
                        </span>
                      </div>
                    </div>
                  </v-col>
                  <v-col cols="4" md="2" class="d-flex align-center justify-end py-0">
                    <v-chip
                      v-if="repoAdded(item.full_name)"
                      color="success"
                      x-small
                    >
                      Added
                    </v-chip>
                    <v-checkbox
                      :input-value="repoSelected(item)"
                      value
                      :disabled="repoAdded(item.full_name)"
                      @click="selectRepo(item)"
                    ></v-checkbox>
                  </v-col>
                </v-row>
              </v-container>
            </template>
          </v-data-iterator>
        </v-col>
        <v-col v-else cols="12" class="d-flex justify-center">
          <a :href="githubAuthUrl" class="overline">Connect Github Account</a>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
export default {
  data: () => ({
    search: null,
    selectedRepos: [],
    selectionText: 'Select All',
    loading: false
  }),
  computed: {
    ...mapGetters({
      user: 'auth/user',
      repos: 'git/repos',
      gitRepos: 'git/gitRepos'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    repoSelected() {
      return (repo) => {
        return this.repoAdded(repo.full_name) ? true : this.selectedRepos.includes(repo)
      }
    },
    repoAdded() {
      return (name) => {
        return this.repos.items.find(({ full_name }) => {
          return full_name === name
        }) ? true : false
      }
    },
    githubAuthUrl() {
      const clientId = process.env.VUE_APP_GITHUB_APP_CLIENT_ID
      const prodRoute = process.env.NODE_ENV === 'production' ? '/bountyhunt' : ''
      const redirectUri = `${location.origin}${prodRoute}/auth/github/callback`
      return `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}`
    }
  },
  methods: {
    ...mapActions({
      addGithubRepositories: 'git/addGithubRepositories'
    }),
    selectRepo(repo) {
      if (this.selectedRepos.includes(repo)) {
        const index = this.selectedRepos.indexOf(repo)
        this.selectedRepos.splice(index, 1)
      } else {
        this.selectedRepos.push(repo)
      }
    },
    selectAllRepos(isSelected) {
      if (isSelected) {
        this.selectionText = 'Deselect All'
        const selectedRepos = this.gitRepos.filter(({ full_name }) => !this.repoAdded(full_name))
        this.selectedRepos = selectedRepos
      } else {
        this.selectionText = 'Select All'
        this.selectedRepos = []
      }
    },
    async addRepos() {
      this.loading = true
      const response = await this.addGithubRepositories(this.selectedRepos)

      switch (response.status) {
        case 400:
          this.$root.$emit('showSnackbar', { color: 'error', message: response.data.msg });
          break;

        case 201:
          this.$root.$emit('showSnackbar', { color: 'success', message: response.data.msg });
          this.$emit('reposAdded')
          this.selectionText = 'Select All'
          this.selectedRepos = []
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

<style>

</style>