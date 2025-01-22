import { ref } from 'vue'

const isOpen = ref(false)
const modalComponent = ref(null)
const modalProps = ref({})

export function useModal() {
  const openModal = ({ component, props = {} }) => {
    modalComponent.value = component
    modalProps.value = props
    isOpen.value = true
  }

  const closeModal = () => {
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
}
