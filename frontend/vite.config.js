import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { readFileSync } from 'node:fs'
import svgLoader from 'vite-svg-loader'

// Serves three.js's Draco decoder (for compressed 3D product models) from the
// shop itself at /draco/, in development and in the build.
function dracoDecoder() {
  const dir = fileURLToPath(new URL('./node_modules/three/examples/jsm/libs/draco/gltf/', import.meta.url))
  const files = ['draco_wasm_wrapper.js', 'draco_decoder.wasm']
  return {
    name: 'draco-decoder',
    configureServer(server) {
      server.middlewares.use('/draco', (req, res, next) => {
        const file = req.url.split('?')[0].replace(/^\//, '')
        if (!files.includes(file)) return next()
        res.setHeader('Content-Type', file.endsWith('.wasm') ? 'application/wasm' : 'text/javascript')
        res.end(readFileSync(dir + file))
      })
    },
    generateBundle() {
      for (const file of files) {
        this.emitFile({ type: 'asset', fileName: `draco/${file}`, source: readFileSync(dir + file) })
      }
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    dracoDecoder(),
    svgLoader({
      svgoConfig: {
        multipass: true,
        plugins: [
          {
            name: 'preset-default',
            params: {
              overrides: {
                removeViewBox: false
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
