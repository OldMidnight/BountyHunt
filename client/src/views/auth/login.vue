<template>
  <auth-layout>
    <validation-observer v-slot="{ invalid }">
      <v-form @submit.prevent="login">
        <validation-provider
          name="username"
          :rules="rules.username"
          v-slot="validationContext"
        >
          <v-text-field
            v-model="user.username"
            label="Username or email"
            :error="getValidationState(validationContext)"
            :error-messages="validationContext.errors[0]"
            required
            filled
          ></v-text-field>
        </validation-provider>
        <validation-provider
          name="password"
          :rules="rules.password"
          v-slot="validationContext"
        >
          <v-text-field
            v-model="user.password"
            label="Password"
            type="password"
            :error="getValidationState(validationContext)"
            :error-messages="validationContext.errors[0]"
            required
            filled
          ></v-text-field>
        </validation-provider>
        <v-btn
          type="submit"
          class="w-100"
          :disabled="invalid"
          depressed
          color="primary"
          large
        > 
          Login
        </v-btn>
        <div class="d-flex justify-space-between align-center mt-2">
          <router-link
            class="caption black--text text-decoration-none"
            to="/auth/register"
          >
            Create an account
          </router-link>
        </div>
      </v-form>
    </validation-observer>
  </auth-layout>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { ValidationProvider, ValidationObserver } from 'vee-validate';
import AuthLayout from '@/components/layouts/AuthLayout'
export default {
  components: { AuthLayout, ValidationObserver, ValidationProvider },
  data: () => ({
    user: {
      username: null,
      password: null
    },
    rules: {
      username: {
        required: true
      },
      password: {
        required: true
      }
    }
  }),
  computed: {
    ...mapGetters({
      authUser: 'auth/user'
    })
  },
  methods: {
    ...mapActions({
      loginUser: 'auth/loginUser',
      fetchUser: 'auth/fetchUser'
    }),
    async login() {
      await this.loginUser(this.user)
        .then(() => {
          if (this.authUser.authenticated) {
            const redirect = this.$route.query.redirect
            this.$router.push(redirect ? redirect : '/')
          } else {
            this.$root.$emit('showSnackbar', { color: 'error', message: 'Invalid Username or Password' });
          }
        })
      
    },
    getValidationState({ dirty, validated, valid = null}) {
      return dirty || validated ? !valid : false;
    }
  }
}
</script>

<style>

</style>