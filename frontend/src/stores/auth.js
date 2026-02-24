import { UserManager, WebStorageStateStore } from 'oidc-client-ts'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'


export const useAuthStore = defineStore('auth', () => {
  const connected = ref(false)
  const username = ref(null)
  const token = ref(null)

  const userManager = new UserManager({
    authority: import.meta.env.VITE_AUTH_URL,
    client_id: import.meta.env.VITE_AUTH_CLIENT_ID,
    redirect_uri: `${window.location.origin}/callback`,
    post_logout_redirect_uri: `${window.location.origin}/`,
    response_type: 'code',
    scope: 'openid profile',
    automaticSilentRenew: true,
    userStore: new WebStorageStateStore({ store: window.localStorage }),
  })

  const authenticated = computed(() => username.value !== null)

  const init = async () => {
    // Handle OIDC callback route first
    if (window.location.pathname === '/callback') {
      let callbackUser = null
      try {
        await userManager.signinRedirectCallback()
        callbackUser = await userManager.getUser()
      } catch (cbError) {
        console.error('Callback processing error:', cbError)
      } finally {
        // Always clean up callback URL
        window.history.replaceState({}, document.title, '/')
      }
      if (callbackUser) {
        username.value = callbackUser.profile.preferred_username
        token.value = callbackUser.access_token
      }
      return
    }

    // Check for existing user
    let user = await userManager.getUser()
    if (user) {
      if (user.expired) {
        try {
          user = await userManager.signinSilent()
        } catch (silentError) {
          console.error('Silent signin error:', silentError)
          await userManager.signinRedirect()
          // Clean up URL in case redirect returns to callback
          window.history.replaceState({}, document.title, '/')
          return
        }
      }
      if (user) {
        username.value = user.profile.preferred_username
        token.value = user.access_token
      }
      return
    }

    // No user found, start signin flow
    await userManager.signinRedirect()
  }

  const logout = async () => {
    try {
      await userManager.signoutRedirect()
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return {
    // State
    authenticated, connected, username, token,

    // Actions
    init, logout
  }
})