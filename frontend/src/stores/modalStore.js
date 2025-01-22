import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useModalStore = defineStore('modal', () => {
  const isOpen = ref(false)
  const modalComponent = ref(null)
  const modalProps = ref({})

  function openModal({ component, props = {} }) {
    modalComponent.value = component
    modalProps.value = props
    isOpen.value = true
  }

  function closeModal() {
    isOpen.value = false
    modalComponent.value = null
    modalProps.value = {}
  }

  return {
    isOpen,
    modalComponent,
    modalProps,
    openModal,
    closeModal
  }
})
