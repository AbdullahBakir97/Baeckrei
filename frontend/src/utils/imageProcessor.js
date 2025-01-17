import { ref } from 'vue'

export const processedImages = ref([])
export const animationState = ref({
  isAnimating: false,
  progress: 0
})

export async function processImages(imageFiles) {
  const processed = []
  animationState.value.isAnimating = true
  
  for (const [index, file] of imageFiles.entries()) {
    try {
      // Load image
      const image = await loadImage(file)
      
      // Calculate dimensions
      const maxWidth = 400
      const scale = Math.min(1, maxWidth / image.width)
      const width = Math.round(image.width * scale)
      const height = Math.round(image.height * scale)
      const padding = 40 // Extra padding for shadow
      
      // Create main canvas
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      canvas.width = width + padding * 2
      canvas.height = height + padding * 2
      
      // Draw image centered
      ctx.save()
      ctx.translate(padding, padding)
      ctx.drawImage(image, 0, 0, width, height)
      ctx.restore()
      
      // Create shadow canvas
      const shadowCanvas = document.createElement('canvas')
      const shadowCtx = shadowCanvas.getContext('2d')
      shadowCanvas.width = canvas.width
      shadowCanvas.height = canvas.height + 20
      
      // Draw shadow
      shadowCtx.save()
      shadowCtx.shadowColor = 'rgba(0, 0, 0, 0.2)'
      shadowCtx.shadowBlur = 15
      shadowCtx.shadowOffsetX = 0
      shadowCtx.shadowOffsetY = 5
      shadowCtx.translate(padding, padding)
      shadowCtx.drawImage(image, 0, 0, width, height)
      shadowCtx.restore()
      
      // Combine canvases
      const finalCanvas = document.createElement('canvas')
      const finalCtx = finalCanvas.getContext('2d')
      finalCanvas.width = canvas.width
      finalCanvas.height = canvas.height + 20
      
      // Draw shadow and image
      finalCtx.drawImage(shadowCanvas, 0, 0)
      finalCtx.drawImage(canvas, 0, 0)
      
      // Update progress
      animationState.value.progress = ((index + 1) / imageFiles.length) * 100
      
      const processedImage = {
        src: finalCanvas.toDataURL('image/png'),
        width: finalCanvas.width,
        height: finalCanvas.height,
        aspectRatio: width / height,
        originalSrc: file
      }
      
      processed.push(processedImage)
    } catch (error) {
      console.error(`Error processing image: ${file}`, error)
    }
  }
  
  animationState.value.isAnimating = false
  animationState.value.progress = 100
  processedImages.value = processed
  return processed
}

async function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

export function getOptimalImageSize(image, maxWidth = 300) {
  const ratio = image.width / image.height
  const width = Math.min(maxWidth, image.width)
  const height = width / ratio
  
  return {
    width: Math.round(width),
    height: Math.round(height)
  }
}