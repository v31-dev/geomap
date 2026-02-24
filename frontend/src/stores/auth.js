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
    scope: 'openid profile offline_access',
    automaticSilentRenew: true,
    userStore: new WebStorageStateStore({ store: window.localStorage }),
  })

  const authenticated = computed(() => username.value !== null)

  const init = async () => {
    // If a user is already stored, use it
    const existingUser = await userManager.getUser()
    if (existingUser) {
      // If the token is expired, try silent renew first before redirecting to login
      if (existingUser.expired) {
        try {
          existingUser = await userManager.signinSilent()
        } catch (silentError) {
          console.error('Silent signin error:', silentError)
          await userManager.signinRedirect() // fallback to redirect if silent fails
          return
        }
      }
      
      username.value = existingUser.profile.preferred_username
      token.value = existingUser.access_token
      return
    }

    // If we're on the OIDC callback route, process the redirect response
    if (window.location.pathname === '/callback') {
      try {
        await userManager.signinRedirectCallback()
        // Remove the callback query params from the URL
        window.history.replaceState({}, document.title, '/')
        // after callback, user should be available
        const user = await userManager.getUser()
        if (user) {
          username.value = user.profile.preferred_username
          token.value = user.access_token
        }
        return
      } catch (cbError) {
        console.error('Callback processing error:', cbError)
      }
    }

    // No user and not on callback -> start signin flow
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