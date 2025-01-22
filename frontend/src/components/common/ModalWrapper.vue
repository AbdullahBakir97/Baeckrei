<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="modalStore.isOpen" :class="class">
        <component
          :is="components[modalStore.modalComponent]"
          v-bind="modalStore.modalProps"
          @close="modalStore.closeModal"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useModalStore } from '@/stores/modalStore'
import ImageZoomModal from './ImageZoomModal.vue'

const components = {
  'ImageZoomModal': ImageZoomModal
}

defineProps({
  class: {
    type: String,
    default: ''
  }
})

const modalStore = useModalStore()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
