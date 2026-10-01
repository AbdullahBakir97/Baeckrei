// Kept apart from the Three.js modules so pages can check for WebGL
// without loading the 3D engine.
export function webglAvailable() {
  try {
    const canvas = document.createElement('canvas')
    return !!(window.WebGL2RenderingContext && canvas.getContext('webgl2')) || !!canvas.getContext('webgl')
  } catch {
    return false
  }
}
