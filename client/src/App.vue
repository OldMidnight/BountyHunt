<template>
  <v-app>
    <router-view/>
    <snackbar></snackbar>
  </v-app>
</template>

<script>
import snackbar from '@/components/helpers/Snackbar'
export default {
  name: 'App',
  components: { snackbar }
};
</script>

<style lang="scss">
html, body {
  height: 100%;
}

#app .bar-underline {
  border-width: 0 0 thin;
  border-style: solid;
  border-bottom-color: rgba(0,0,0,.12) !important;
}

.bh-search.v-text-field>.v-input__control>.v-input__slot:before {
  border-style: none;
}
</style>
