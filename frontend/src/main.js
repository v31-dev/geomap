import { createApp } from 'vue'
import App from './App.vue'
import { initAuth } from './auth'

const app = createApp(App)

initAuth()
  .then((user) => {
    if (user) {
      app.mount('#app')
    }
  })
  .catch((error) => {
    console.error('AUth initialization error:', error)
  })