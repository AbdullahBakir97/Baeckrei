#!/usr/bin/env node
// Shrinks a scanned 3D model for the web before uploading it in the admin.
//
//   npm run optimize-model -- scan.glb brezel.glb
//
// Uses glTF-Transform (downloaded by npx on first use): merges and welds
// geometry, simplifies dense scan meshes, resizes textures to 2048 px
// (keeping JPEG/PNG) and compresses the geometry with Draco. These are the
// formats the phones' own AR viewers (Scene Viewer, Quick Look) read too, so
// the shop's 3D viewer and the "View on your table" button share one file.
import { execFileSync } from 'node:child_process'
import { existsSync, statSync } from 'node:fs'

const [input, output] = process.argv.slice(2)
if (!input || !output) {
  console.error('Usage: npm run optimize-model -- <input.glb> <output.glb>')
  process.exit(1)
}
if (!existsSync(input)) {
  console.error(`File not found: ${input}`)
  process.exit(1)
}

execFileSync('npx', [
  '--yes', '@gltf-transform/cli@4', 'optimize', input, output,
  '--compress', 'draco',
  '--texture-compress', 'auto',
  '--instance', 'false',
  '--texture-size', '2048',
  '--simplify-ratio', '0.5'
], { stdio: 'inherit' })

const mb = (file) => (statSync(file).size / 1024 / 1024).toFixed(1)
console.log(`\n${input}: ${mb(input)} MB  ->  ${output}: ${mb(output)} MB`)
if (statSync(output).size > 20 * 1024 * 1024) {
  console.warn('The result is still over the 20 MB upload limit; try a lower --texture-size or --simplify-ratio.')
}
