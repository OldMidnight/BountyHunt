<template>
  <v-snackbar
    v-model="show"
    :color="bar.color"
    right
    top
  >
    {{ bar.message }}
  </v-snackbar>
</template>

<script>
export default {
  data: () => ({
    show: false,
    bar: {}
  }),
  created() {
    this.$root.$on('showSnackbar', (bar) => {
      this.bar = bar
      this.show = true
    })
  },
  beforeDestroy() {
    this.$root.$off('showSnackbar')
  }
}
</script>

<style>

</style>