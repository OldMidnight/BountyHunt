<template>
  <v-container class="h-100">
    <v-row class="h-100">
      <v-col cols="12" class="h-20">
        <p class="display-1 text-center">BountyHunt</p>
      </v-col>
      <v-col cols="12" class="h-80">
        <v-card :class="`${isMobile ? 'elevation-0' : 'w-25'} pa-6 px-10 mx-auto`">
          <slot />
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    }
  }
}
</script>

<style>
</style>