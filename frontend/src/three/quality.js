// A rough performance tier for the 3D scenes, so phones and older laptops
// get fewer particles and a lower resolution instead of a stuttering page.
let cached = null

export function qualityTier() {
  if (cached) return cached
  const cores = navigator.hardwareConcurrency || 4
  const memory = navigator.deviceMemory || 4
  const touch = window.matchMedia('(pointer: coarse)').matches
  const saveData = navigator.connection?.saveData
  let tier = 'high'
  if (saveData || cores <= 2 || memory <= 2) tier = 'low'
  else if (touch || cores <= 4 || memory <= 4) tier = 'medium'
  cached = tier
  return tier
}

export const QUALITY = {
  high: { pixelRatio: 2, dust: 420, steam: true, items: 7, textureSize: 512 },
  medium: { pixelRatio: 1.5, dust: 180, steam: true, items: 6, textureSize: 512 },
  low: { pixelRatio: 1, dust: 0, steam: false, items: 4, textureSize: 256 }
}

export const quality = () => QUALITY[qualityTier()]
