import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faCube, faArrowRight, faArrowDown, faImage, faHandPointer, faFire, faWheatAwn } from '@fortawesome/free-solid-svg-icons'
import {
  faShoppingCart,
  faSearch,
  faUserCircle,
  faPlus,
  faMinus,
  faTrash,
  faList,
  faTable,
  faLeaf,
  faSeedling,
  faLocationDot,
  faPhone,
  faEnvelope,
  faSpinner,
  faCartPlus,
  faCircle,
  faExclamationTriangle,
  faExclamationCircle,
  faRotate,
  faWheatAlt,
  faCircleXmark,
  faCheck,
  faXmark,
  faUtensils,
  faBolt,
  faDumbbell,
  faBreadSlice,
  faOilCan,
  faMagnifyingGlassPlus,
  faChevronLeft,
  faChevronRight,
  faShareNodes,
  faCodeCompare,
  faMortarPestle,
  faTriangleExclamation,
  faChartPie,
  faShoppingBag,
  faTruck,
  faCalendar,
  faTimes,
  faStore,
  faCreditCard,
  faMoneyBill,
  faClock,
  faCircleCheck,
  faHeart,
  faBoxOpen,
  faUser,
  faLock,
  faFileLines,
  faNewspaper,
  faHouse,
  faArrowLeft,
  faTrainSubway
} from '@fortawesome/free-solid-svg-icons'

import {
  faHeart as farHeart
} from '@fortawesome/free-regular-svg-icons'

import {
  faFacebook,
  faTwitter,
  faInstagram
} from '@fortawesome/free-brands-svg-icons'

// Add icons to library
library.add(
  faShoppingCart,
  faSearch,
  faUserCircle,
  faPlus,
  faMinus,
  faTrash,
  faList,
  faTable,
  faLeaf,
  faSeedling,
  faLocationDot,
  faPhone,
  faEnvelope,
  faSpinner,
  faCartPlus,
  faCircle,
  faExclamationTriangle,
  faExclamationCircle,
  faRotate,
  faWheatAlt,
  faCircleXmark,
  faCheck,
  faXmark,
  faUtensils,
  faBolt,
  faDumbbell,
  faBreadSlice,
  faOilCan,
  faMagnifyingGlassPlus,
  faChevronLeft,
  faChevronRight,
  faShareNodes,
  faCodeCompare,
  faMortarPestle,
  faTriangleExclamation,
  faChartPie,
  faShoppingBag,
  faTruck,
  faCalendar,
  faTimes,
  faStore, faCreditCard, faMoneyBill, faClock, faCircleCheck, faHeart, faBoxOpen, faUser,
  faLock, faFileLines, faNewspaper, faHouse, faArrowLeft, faTrainSubway,
  farHeart,
  faFacebook,
  faTwitter,
  faInstagram
)

// Icons used by the redesigned storefront.
library.add(faCube, faArrowRight, faArrowDown, faImage, faHandPointer, faFire, faWheatAwn)

export default function installFontAwesome(app) {
  app.component('font-awesome-icon', FontAwesomeIcon)
}
