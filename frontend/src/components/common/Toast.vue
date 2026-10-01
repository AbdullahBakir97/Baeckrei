<template>
  <Teleport to="body">
    <div class="toasts" role="status" aria-live="polite">
      <TransitionGroup name="toast">
        <div v-for="toast in toasts" :key="toast.id" class="toast" :class="`is-${toast.type}`">
          <span class="toast-icon" aria-hidden="true">
            <font-awesome-icon :icon="icons[toast.type] || 'check'" />
          </span>
          <span>{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toasts } = useToast()
const icons = { success: 'check', error: 'circle-xmark', warning: 'exclamation-circle', info: 'check' }
</script>

<style scoped>
.toasts {
  position: fixed;
  left: 50%;
  bottom: 1.5rem;
  z-index: 70;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  width: max-content;
  max-width: calc(100vw - 2rem);
  transform: translateX(-50%);
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.6rem 1.1rem 0.6rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.92rem;
  color: #f4ece1;
  background: rgba(30, 25, 20, 0.92);
  border: 1px solid rgba(244, 236, 225, 0.12);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(16px);
}

.toast-icon {
  display: grid;
  place-items: center;
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  color: #0e0c0a;
  background: #e6a15a;
}

.is-error .toast-icon {
  background: #f08f79;
}

.is-warning .toast-icon {
  background: #f2c48d;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s, transform 0.5s var(--ease-out-expo);
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.96);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
