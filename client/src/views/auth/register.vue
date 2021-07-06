<template>
  <auth-layout>
    <validation-observer v-slot="{ invalid }">
      <v-form @submit.prevent="register">
        <validation-provider
          name="username"
          :rules="rules.username"
          v-slot="validationContext"
        >
          <v-text-field
            v-model="user.username"
            label="Username"
            :error="getValidationState(validationContext)"
            :error-messages="validationContext.errors[0]"
            required
            filled
          ></v-text-field>
        </validation-provider>
        <validation-provider
          name="email"
          :rules="rules.email"
          v-slot="validationContext"
        >
          <v-text-field
            v-model="user.email"
            label="Email"
            type="email"
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
          Register
        </v-btn>
        <div class="d-flex justify-space-between align-center mt-2">
          <router-link
            class="caption black--text text-decoration-none"
            to="/auth/login"
          >
            Have an account? Log in
          </router-link>
        </div>
      </v-form>
    </validation-observer>
  </auth-layout>
</template>

<script>
import { mapActions } from 'vuex'
import { ValidationProvider, ValidationObserver } from 'vee-validate';
import AuthLayout from '@/components/layouts/AuthLayout'
export default {
  components: { AuthLayout, ValidationObserver, ValidationProvider },
  data: () => ({
    user: {
      username: null,
      email: null,
      password: null
    },
    rules: {
      username: {
        required: true,
        alpha_dash: true,
        min: 3,
        max: 20
      },
      email: {
        required: true,
        email: true
      },
      password: {
        required: true,
        min: 8,
        has_upper_case: true,
        has_digit: true,
        no_whitespace: true
      }
    }
  }),
  methods: {
    ...mapActions({
      registerUser: 'auth/registerUser'
    }),
    async register() {
      await this.registerUser(this.user)
        .then(async () => {
          this.$router.push('/')
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