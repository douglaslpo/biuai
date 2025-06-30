/* eslint-env node */

const { configure } = require('quasar/wrappers')

module.exports = configure(function (/* ctx */) {
  return {
    eslint: {
      warnings: true,
      errors: true
    },

    boot: [
      'axios',
      'pinia',
      'auth',
      'vuetify'
    ],

    css: [
      'app.scss'
    ],

    extras: [
      'material-icons',
      'mdi-v7'
    ],

    build: {
      target: {
        browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'],
        node: 'node16'
      },

      vueRouterMode: 'history',
      
      env: {
        API_URL: process.env.VITE_API_URL || 'http://localhost:3000'
      }
    },

    devServer: {
      open: true,
      port: 8080,
      proxy: {
        '/api': {
          target: 'http://localhost:3000',
          changeOrigin: true,
          secure: false
        }
      }
    },

    framework: {
      config: {},
      plugins: [
        'Notify',
        'Dialog',
        'Loading',
        'LoadingBar'
      ]
    },

    animations: [],

    ssr: {
      pwa: false,
      prodPort: 3000,
      middlewares: [
        'render'
      ]
    },

    pwa: {
      workboxMode: 'generateSW',
      injectPwaMetaTags: true,
      swFilename: 'sw.js',
      manifestFilename: 'manifest.json',
      useCredentialsForManifestTag: false
    },

    cordova: {},

    capacitor: {
      hideSplashscreen: true
    },

    electron: {
      inspectPort: 5858,
      bundler: 'packager',
      packager: {},
      builder: {
        appId: 'biuai-frontend'
      }
    },

    bex: {
      contentScripts: [
        'my-content-script'
      ]
    }
  }
}) 