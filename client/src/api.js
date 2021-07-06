import axios from 'axios';
import router from '@/router'

const COOKIE_EXPIRED_MSG = 'Token has expired'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL,
  withCredentials: true,
  xsrfCookieName: 'csrf_access_token',
  xsrfHeaderName: 'X-CSRF-TOKEN'
});

// Interceptor used for handling response errors as well as auth token refreshing
api.interceptors.response.use((response) => {
  return response
}, async (error) => {
  const error_message = error.response.data.msg
  switch (error.response.status) {
    case 401:
      if (!error.config.retry && error_message === COOKIE_EXPIRED_MSG) {
        error.config.retry = true
        // change to work with refresh endpoint
        api.defaults.xsrfCookieName = 'csrf_refresh_token';
        await api.post('/auth/refresh_token')
        // revert for normal usage
        api.defaults.xsrfCookieName = 'csrf_access_token';
        return api(error.config)
      }
      break;
    case 404:
      router.push('/404');
      break;
    default:
      break;
  }
  return error.response;
});

export { api };