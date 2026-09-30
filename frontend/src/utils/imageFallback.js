export const PLACEHOLDER_IMAGE = '/images/placeholder.svg'

// Swap a broken <img> to the placeholder exactly once. Without the guard, a
// missing placeholder would trigger @error again and retry forever.
export function applyImageFallback(event) {
  const img = event?.target
  if (!img || img.dataset.fallbackApplied) return
  img.dataset.fallbackApplied = 'true'
  img.src = PLACEHOLDER_IMAGE
}
