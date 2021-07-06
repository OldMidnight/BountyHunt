<template>
  <main-layout>
    <validation-observer v-slot="{ invalid }">
      <v-container fluid>
        <v-row key="0" v-if="creation_step === 0" class="d-flex justify-center">
          <v-col cols="12" md="5" class="d-flex flex-column align-center">
            <span class="display-1">Bounty Template</span>
            <v-select
              :items="bounty_types"
              v-model="selected_bounty_type"
              class="mt-4"
              label="Bounty Type"
              filled
            ></v-select>
          </v-col>
          <v-col cols="12">
            <div class="d-flex justify-center" v-if="selected_bounty_type === 'default'">
              <span class="overline text-center">The default bounty template. Suitable for all needs.</span>
            </div>
            <div class="d-flex flex-column justify-center align-center" v-else-if="selected_bounty_type === 'git'">
              <span class="overline text-center">
                A template for creating bounties from Git issues. Add your repositories to start working with them
              </span>
              <span class="overline">
                Supports:
                <v-icon color="black">mdi-github</v-icon>
              </span>
            </div>
          </v-col>
          <v-col cols="12" class="d-flex justify-center">
            <v-btn color="primary" @click="nextStep">Next</v-btn>
          </v-col>
        </v-row>
        <v-row v-if="creation_step > 0" class="d-flex justify-center">
          <v-col cols="11" md="7">
            <h2 class="my-2">Create a Bounty</h2>
            <v-progress-linear :value="creationProgress"></v-progress-linear>
            <v-btn text small @click="creation_step--" color="primary">
              <v-icon>mdi-arrow-left</v-icon>
              Back
            </v-btn>
          </v-col>
          <v-col cols="12" md="7">
            <transition
              enter-active-class="animate__animated animate__fadeIn animate__faster"
              leave-active-class="animate__animated animate__fadeOut animate__faster"
              mode="out-in"
            >
              <v-card key="2" v-if="creation_step === 1" :class="{'elevation-0': isMobile}">
                <v-card-title>Bounty Title</v-card-title>
                <v-card-subtitle>This is how people will find your bounty</v-card-subtitle>
                <v-form
                  class="px-5 py-6"
                  @submit.prevent
                >
                  <validation-provider name="title" :rules="rules.title" v-slot="validationContext">
                    <v-text-field
                      v-model="bounty.title"  
                      label="Title"
                      placeholder="My First Bounty"
                      :error="getValidationState(validationContext)"
                      :error-messages="validationContext.errors[0]"
                      required
                      @keypress.enter.prevent="!invalid && creation_step++"
                    ></v-text-field>
                  </validation-provider>
                </v-form>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="info"
                    text
                    :disabled="invalid"
                    @click="creation_step++"
                  >
                    Next
                  </v-btn>
                </v-card-actions> 
              </v-card>

              <v-card key="2" v-if="creation_step === 2" :class="{'elevation-0': isMobile}">
                <v-card-title>Description</v-card-title>
                <v-card-subtitle>
                  This is how Bounty Hunters will learn about your bounty. Make it as enticing as possible!
                </v-card-subtitle>
                <v-form
                  class="px-5 py-6"
                  @submit.prevent
                >
                  <validation-provider
                    name="description"
                    :rules="rules.description"
                    v-slot="validationContext"
                  >
                    <v-textarea
                      v-model="bounty.description"
                      label="Description"
                      :error="getValidationState(validationContext)"
                      :error-messages="validationContext.errors[0]"
                      required
                      no-resize
                    ></v-textarea>
                  </validation-provider>
                  <v-row>
                    <v-col cols="12" class="py-0">
                      <h4>External Links</h4>
                    </v-col>
                    <v-col cols="7" class="py-0">
                      <v-simple-table>
                        <template v-slot:default>
                          <thead>
                            <tr>
                              <th class="text-left">
                                URL
                              </th>
                              <th class="text-left"></th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr
                              v-for="(link, index) in bounty.external_links"
                              :key="index"
                            >
                              <td>{{ link.url }}</td>
                              <td>
                                <v-btn
                                  color="error"
                                  small
                                  icon
                                  @click="
                                    deleteExternalURLindex = index;
                                    deleteExternalURLModal = true
                                  "
                                >
                                  <v-icon>mdi-delete</v-icon>
                                </v-btn>
                              </td>
                            </tr>
                          </tbody>
                        </template>
                      </v-simple-table>
                      <v-btn
                        small
                        text
                        color="primary"
                        @click="addExternalURLModal = true"
                      >
                        Add external link
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-form>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="info"
                    text
                    :disabled="invalid"
                    @click="creation_step++"
                  >
                    Next
                  </v-btn>
                  <v-btn color="info" @click="creation_step--" text>Back</v-btn>
                </v-card-actions>
              </v-card>
              
              <v-card key="3" v-if="creation_step === 3" :class="{'elevation-0': isMobile}">
                <v-card-title>Categories</v-card-title>
                <v-card-subtitle>
                  Select different categories by which Bounty Hunters can find your bounty
                </v-card-subtitle>
                <v-form
                  class="px-5 py-6"
                  @submit.prevent
                >
                  <validation-provider
                    name="categories"
                    :rules="rules.categories"
                    v-slot="validationContext"
                  >
                    <v-select
                      v-model="bounty.selected_categories"
                      :items="filteredCategories"
                      :item-text="category => category[0]"
                      :item-value="category => category"
                      label="Categories"
                      multiple
                      chips
                      hint="What categories is this bounty applicable to?"
                      item-color="primary"
                      :error="getValidationState(validationContext)"
                      :error-messages="validationContext.errors[0]"
                      persistent-hint
                    ></v-select>
                  </validation-provider>
                </v-form>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn
                    color="info"
                    text
                    :disabled="invalid"
                    @click="creation_step++"
                  >
                    Next
                  </v-btn>
                  <v-btn color="info" @click="creation_step--" text>Back</v-btn>
                </v-card-actions>
              </v-card>
              <bounty-preview
                v-if="creation_step === 4"
                key="4"
                @reset="creation_step = 0"
              ></bounty-preview>
            </transition>
          </v-col>
        </v-row>
        <v-dialog v-model="addExternalURLModal" persistent width="500">
          <v-card>
            <v-card-title>Add External Link</v-card-title>
            <v-card-text>
              <v-container>
                <v-row>
                  <v-col>
                    <validation-provider name="external link" :rules="rules.url" v-slot="validationContext">
                      <v-text-field
                        v-model="newExternalURL"
                        label="URL"
                        placeholder="https://..."
                        :error="getValidationState(validationContext)"
                        :error-messages="validationContext.errors[0]"
                      ></v-text-field>
                    </validation-provider>
                  </v-col>
                </v-row>
              </v-container>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn text color="green darken-1" @click="clearExternalURL">Close</v-btn>
              <v-btn
                text
                color="green darken-1"
                :disabled="invalid  "
                @click="addExternalURL"
              >
                Add
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-dialog
          v-model="deleteExternalURLModal"
          persistent
          max-width="290"
        >
          <v-card>
            <v-card-title class="headline">
              Delete External Link?
            </v-card-title>
            <v-card-text>Delete <b>{{ externalURLToDelete.url }}?</b></v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="green darken-1"
                text
                @click="clearExternalURL"
              >
                No
              </v-btn>
              <v-btn
                color="green darken-1"
                text
                @click="deleteExternalURL"
              >
                Yes
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-container>
    </validation-observer>
  </main-layout>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { ValidationProvider, ValidationObserver } from 'vee-validate';
import BountyPreview from '@/components/BountyPreview';
import MainLayout from '@/components/layouts/MainLayout';
export default {
  components: {
    ValidationProvider,
    ValidationObserver,
    BountyPreview,
    MainLayout
  },
  data: () => ({
    bounty_types: ['default', 'git'],
    selected_bounty_type: 'default',
    creation_step: 0,
    bounty: {
      selected_categories: [],
      external_links: [],
      currency_code: 'EUR',
      title: null,
      description: null,
      amount: 5,
      allow_multiple_investors: false,
      created: null,
      last_edited: null
    },
    addExternalURLModal: false,
    newExternalURL: null,
    deleteExternalURLModal: false,
    deleteExternalURLindex: null,
    rules: {
      title: {
        required: true
      },
      description: { required: true },
      categories: { required: true },
      amount: { 
        required: true,
        decimals: true,
        currency_decimal: true
      },
      url: {
        regex: /(?:http|Http|Https|https):\/\/[a-zA-Z0-9\-.]+\.[a-zA-Z]{2,3}(\/\S*)?/
      }
    },
    loading: false
  }),
  computed: {
    ...mapGetters({
      categories: 'bounty/categories',
      currencies: 'bounty/currencies'
    }),
    filteredCategories() {
      return this.categories.filter(([name]) => {
        return name !== 'Git'
      })
    },
    isMobile() {
      return this.$vuetify.breakpoint.mobile
    },
    currencyText() {
      const currency = this.currencies.find(({ code }) => code === this.bounty.currency_code)
      return `${currency.symbol}-${currency.code}`;
    },
    creationProgress() {
      return this.creation_step / 4 * 100;
    },
    externalURLToDelete() {
      if (this.deleteExternalURLindex !== null) {
        return this.bounty.external_links.find((_, index) => {
          return index === this.deleteExternalURLindex;
        });
      } else {
        return '';
      }
    }
  },
  watch: {
    async creation_step() {
      if (this.selected_bounty_type === 'default') {
        this.editStateBounty(this.bounty);
      }
    }
  },
  async mounted() {
    this.loading = true
    await this.fetchCategories();
    this.loading = false
  },
  methods: {
    ...mapActions({
      editStateBounty: 'bounty/editStateBounty',
      fetchCategories: 'bounty/fetchCategories'
    }),
    clearExternalURL() {
      this.newExternalURL = null;
      this.addExternalURLModal = false;
      this.deleteExternalURLModal = false;
      this.deleteExternalURLindex = null;
    },
    addExternalURL() {
      this.bounty.external_links.push({ url: this.newExternalURL });
      this.clearExternalURL();
    },
    deleteExternalURL() {
      this.bounty.external_links = this.bounty.external_links.filter((_, index) => {
        return this.deleteExternalURLindex !== index;
      });
      this.clearExternalURL();
    },
    getValidationState({ dirty, validated, valid = null}) {
      return dirty || validated ? !valid : false;
    },
    nextStep() {
      if (this.selected_bounty_type === 'git') {
        this.$router.push('/bounty/create/git')
      } else {
        this.creation_step++
      }
    }
  }
};
</script>

<style>

</style>