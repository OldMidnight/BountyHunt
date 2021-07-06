<template>
  <v-row>
    <v-col cols="12" class="d-flex">
      <div class="d-flex">
        <p class="mr-4 mb-0">{{ category.name }}</p>
        <router-link to="/" class="caption">View more</router-link>
      </div>
    </v-col>
    <v-col cols="12">
      <v-slide-group
        show-arrows
      >
        <v-slide-item
          v-for="bounty in category.bounties"
          :key="bounty.bounty_id"
          v-slot="{ active, toggle }"
        >
          <v-card
            class="ma-4 bounty-item d-flex flex-column justify-center"
            width="400"
            outlined
            @mouseenter="toggle"
            @mouseleave="toggle"
          >
            <router-link
              :to="bounty_url(bounty.url)"
              :class="{ 'bounty-link-inactive': !active  }"
            >
              <v-card-title>
                {{ bounty.title }}
              </v-card-title>
              <v-card-text class="pb-0 text--primary">
                <p>
                  {{ bounty.description | truncate(150, '...') }}
                </p>
              </v-card-text>
            </router-link>
            <v-card-subtitle class="d-flex align-center">
              By {{ bounty.author }}
              <v-icon x-small>mdi-menu-right</v-icon>
              <span>Created {{ relativeTime(bounty.created) }}</span>
            </v-card-subtitle>
          </v-card>
        </v-slide-item>
      </v-slide-group>
    </v-col>
  </v-row>
</template>

<script>
import { relativeTime } from '@/helpers'
export default {
  props: {
    category: {
      type: Object,
      required: true,
      default: () => ({})
    }
  },
  computed: {
    bounty_url() {
      return (url) => { 
        return `/bounty/${url}`
      }
    }
  },
  methods: {
    relativeTime
  }
}
</script>

<style lang="scss" scoped>
.bounty-item {
  cursor: pointer;
}

.bounty-link-inactive {
  text-decoration: none;
  color: inherit;
}
</style>