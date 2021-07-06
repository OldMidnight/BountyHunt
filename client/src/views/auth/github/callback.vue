<template>
  <p>Redirecting...</p>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  async created() {
    if (this.$route.query.code) {
      await this.createGithubAccessToken(this.$route.query.code)
    }
    this.$router.push('/')
  },
  methods: {
    ...mapActions({
      createGithubAccessToken: 'auth/createGithubAccessToken'
    })
  }
}
</script>

<style>

</style>