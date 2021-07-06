<template>
  <main-layout>
    <v-container>
      <v-row>
        <v-col md="8" cols="12" class="px-16">
          <p class="overline">Featured bounties</p>
          <div class="d-flex justify-space-between">
            <v-card v-for="bounty in featured_bounties" :key="bounty.id" :width="isMobile ? '100%' : '45%'" outlined>
              <v-img
                class="white--text align-end"
                height="200px"
                :src="bounty.img"
              ></v-img>
              <v-card-title>
                {{ bounty.title }}
              </v-card-title>
              <v-card-text class="pb-0 text--primary">
                <p>
                  {{ bounty.description }}
                </p>
              </v-card-text>
              <v-card-subtitle>
                {{ bounty.author }}
              </v-card-subtitle>
            </v-card>
          </div>
        </v-col>
        <v-divider vertical class="rec-feat-bounty-divider"></v-divider>
        <v-col md="4" cols="12" :class="`${isMobile ? '' : 'pl-13'}`">
          <p class="overline">Recommended For You</p>
          <v-list class="rec-bounty-list">
            <template v-for="bounty in recommended_bounties_divided">
              <v-divider v-if="bounty.divider" :key="bounty.id"></v-divider>
              <v-list-item
                v-else
                :key="bounty.id"
              >
                <v-list-item-content>
                  <v-row class="w-100">
                    <v-col cols="4">
                      <v-img
                        class="white--text align-end"
                        height="80px"
                        :src="bounty.img"
                      ></v-img>
                    </v-col>
                    <v-col cols="8">
                      <div class="rec-bounty-title pb-2">{{ bounty.title }}</div>
                      <div class="rec-bounty-amount py-0 green--text text--darken-4 font-weight-bold">€{{ bounty.amount }}</div>
                      <div class="rec-bounty-author py-0 font-weight-light">By {{ bounty.author }}</div>
                    </v-col>
                  </v-row>
                </v-list-item-content>
              </v-list-item>
            </template>
          </v-list>
          <v-pagination
            v-model="recommended_bounties_page"
            :length="recommended_bounties_pagination"
          ></v-pagination>
        </v-col>
        <v-col cols="12" class="pa-0">
          <v-divider></v-divider>
        </v-col>
        <v-col cols="12" v-for="category in category_bounties" :key="category.id">
          <div v-if="category.name !== 'Git'">
            <category-bounty-slider :category="category"></category-bounty-slider>
          </div>
          <div v-else>
            <git-bounty-slider :category="category"></git-bounty-slider>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </main-layout>
</template>

<script>
import MainLayout from '@/components/layouts/MainLayout';
import CategoryBountySlider from '@/components/Dashboard/CategoryBountySlider.vue';
import GitBountySlider from '@/components/Dashboard/GitBountySlider.vue';
import { mapActions, mapGetters } from 'vuex';
export default {
  name: 'Home',
  components: { MainLayout, CategoryBountySlider, GitBountySlider },
  data: () => ({
    bounties: [
      {
        id: 1,
        title: 'Add Magic Brush to Gimp',
        description: "I'm looking for someone to add the magic brush feature to GIMP, similar to how it is in photoshop.",
        author: 'thanos1',
        img: `${process.env.BASE_URL}images/gimp.png`
      },
      {
        id: 2,
        title: "Plato's The Republic - Maori Translation",
        description: 'Looking for a translation of The Rebublic by Plato. Its available for free on the gutenburg project website.',
        author: 'BilboBaggins',
        img: `${process.env.BASE_URL}images/plato_the_republic.jpeg`
      }
    ],
    recommended_bounties: [
      {
        id: 1,
        title: 'Create Udemy Course on How To Draw Anime',
        amount: '27.50',
        author: 'robo_cop',
        img: `${process.env.BASE_URL}images/draw_fight.jpeg`
      },
      {
        id: 2,
        title: 'Fix typo in firefox',
        amount: '4.50',
        author: 'gandalfthegrey',
        img: `${process.env.BASE_URL}images/firefox.jpeg`
      },
      {
        id: 3,
        title: 'Translate 1984 - Zulu',
        amount: '198',
        author: 'patience_27',
        img: `${process.env.BASE_URL}images/1984.jpeg`
      },
      {
        id: 4,
        title: 'Add browser containers to chromium',
        amount: '1923.55',
        author: 'chromium_lover_122',
        img: `${process.env.BASE_URL}images/chromium.png`
      },
      {
        id: 5,
        title: 'Create 3D printing Schematic for titanic',
        amount: '50',
        author: 'elevensies',
        img: `${process.env.BASE_URL}images/titanic.jpeg`
      },
      {
        id: 1,
        title: 'Create Udemy Course on How To Draw Anime',
        amount: '27.50',
        author: 'robo_cop',
        img: `${process.env.BASE_URL}images/draw_fight.jpeg`
      }
    ],
    recommended_bounties_page: 1,
    category_bounties: []
  }),
  computed: {
    ...mapGetters({
      categories: 'bounty/categories'
    }),
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    recommended_bounties_pagination() {
      const bounties = this.recommended_bounties.filter((bounty) => {
        return !bounty.divider;
      });
      return Math.ceil(bounties.length / 3);
    },
    recommended_bounties_divided() {
      const bounties = this.recommended_bounties.slice(
        3 * (this.recommended_bounties_page - 1),
        3 * this.recommended_bounties_page
      );
      const divider = { divider: true };
      return bounties.reduce((updated_list, bounty) => updated_list.concat(bounty, divider), []);
    },
    featured_bounties() {
      return this.isMobile ? [this.bounties[0]] : this.bounties
    }
  },
  async created() {
    await this.fetchCategories();
    const category_bounties = []
    for (const category of this.categories) {
      const options = {
        count: 12,
        page: 1,
        category: category[1]
      }
      const bounties = await this.fetchBountyList(options);
      if (bounties.length > 0) {
        category_bounties.push({ id: category[1], name: category[0], bounties})
      }
    }
    this.category_bounties = category_bounties;
  },
  methods: {
    ...mapActions({
      fetchCategories: 'bounty/fetchCategories',
      fetchBountyList: 'bounty/fetchBountyList'
    })
  }
}
</script>

<style lang="scss" scoped>
.rec-bounty-list {
  background-color: inherit;
}

.rec-bounty-title {
  font-size: 1.1rem;
}

.rec-bounty-amount {
  font-size: 0.9rem;
}

.rec-bounty-author {
  font-size: 0.9rem;
}

.rec-feat-bounty-divider {
  margin: 0 -1px;
}
</style>