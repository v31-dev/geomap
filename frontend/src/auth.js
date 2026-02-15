import { UserManager, WebStorageStateStore } from 'oidc-client-ts'

const authority = import.meta.env.VITE_AUTH_URL
const clientId = import.meta.env.VITE_AUTH_CLIENT_ID

if (!authority || !clientId) {
  console.error('Missing VITE_AUTH_URL or VITE_AUTH_CLIENT_ID')
}

const redirectUri = `${window.location.origin}/oidc/callback`
const postLogoutRedirectUri = `${window.location.origin}/`

const userManager = new UserManager({
  authority,
  client_id: clientId,
  redirect_uri: redirectUri,
  post_logout_redirect_uri: postLogoutRedirectUri,
  response_type: 'code',
  scope: 'openid profile email',
  automaticSilentRenew: false,
  userStore: new WebStorageStateStore({ store: window.localStorage })
})

export async function initAuth() {
  if (window.location.pathname === '/oidc/callback') {
    await userManager.signinRedirectCallback()
    window.location.replace('/')
    return null
  }

  const user = await userManager.getUser()
  if (!user || user.expired) {
    await userManager.signinRedirect()
    return null
  }

  return user
}

export async function getAccessToken() {
  const user = await userManager.getUser()
  if (!user || user.expired) {
    await userManager.signinRedirect()
    return null
  }
  return user.access_token
}

export async function logout() {
  await userManager.signoutRedirect()
}
