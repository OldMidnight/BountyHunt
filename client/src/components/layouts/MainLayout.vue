<template>
  <v-app>
    <v-app-bar
        app
        flat
        underline
        class="bar-underline white"
      >
        <v-container class="pa-0">
          <v-row>
            <v-col md="9" sm="6" class="d-flex align-center">
              <v-app-bar-nav-icon v-if="isMobile" @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
              <v-btn v-if="$route.name !== 'createBounty'" color="primary" text to="/bounty/create">Create a Bounty</v-btn>
            </v-col>
            <v-col v-if="isMobile" class="d-flex align-center justify-end">
              <v-btn
                v-if="user.authenticated"
                color="error"
                depressed
                @click="logout"
              >
                Logout
              </v-btn>
              <v-btn v-else text to="/auth/login">Login</v-btn>
            </v-col>
            <v-col v-if="!isMobile" md="3" sm="6" class="d-flex align-center">
              <v-text-field
                placeholder="Search..."
                class="bh-search rounded-lg mx-2"
                :style="{ maxWidth: '450px' }"
                hide-details
                dense
                prepend-inner-icon="mdi-magnify"
                :filled="!searchFocussed"
                :solo="searchFocussed"
                @focus="searchFocussed = true"
                @blur="searchFocussed = false"
              >
              </v-text-field>
              <div v-if="user.authenticated" class="d-flex align-center">
                <v-btn depressed color="error" @click="logout">Logout</v-btn>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      icon
                      color="primary"
                      class="ml-2"
                      v-bind="attrs"
                      v-on="on"
                    >
                      <v-icon>mdi-account</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ user.username }}</span>
                </v-tooltip>
              </div>
              <div v-else class="d-flex">
                <v-btn depressed outlined class="mx-2" color="primary" to="/auth/login">Login</v-btn>
                <v-btn depressed color="primary" to="/auth/register">Register</v-btn>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-app-bar>

      <v-navigation-drawer v-model="drawer" app floating class="bh-nav">
        <template v-slot:prepend>
          <v-toolbar flat class="bar-underline">
            <v-list-item class="pa-0 mx-n1">BountyHunt</v-list-item>
          </v-toolbar>
        </template>

        <v-list
          dense
          nav
        >
          <v-list-item
            v-for="item in nav_items"
            :key="item.title"
            :to="item.to"
            link
          >
            <v-list-item-icon>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>

            <v-list-item-content>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-main class="bh-main">
        <slot />
      </v-main>
  </v-app>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
export default {
  data: () => ({
    searchFocussed: false,
    drawer: false
  }),
  computed: {
    ...mapGetters({
      user: 'auth/user'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    nav_items() {
      const items = [
        { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/' },
        {
          title: 'My Bounties',
          icon: 'mdi-image',
          to: this.user.authenticated ? '/u/' + this.user.username : '/auth/login'
        }
      ]
      return items
    }
  },
  created() {
    this.drawer = !this.isMobile
  },
  methods: {
    ...mapActions({
      logoutUser: 'auth/logoutUser'
    }),
    async logout() {
      await this.logoutUser()
        .then(() => { if (this.$route.name !== 'home') this.$router.push('/') })
    }
  }
}
</script>

<style>
</style>