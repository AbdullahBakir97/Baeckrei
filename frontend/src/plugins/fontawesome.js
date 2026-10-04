import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faCube, faArrowRight, faArrowDown, faImage, faHandPointer, faFire, faWheatAwn, faEuroSign, faLayerGroup, faReceipt, faUsers, faRightFromBracket, faBars, faGlobe, faCircleInfo, faBell } from '@fortawesome/free-solid-svg-icons'
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
library.add(faCube, faArrowRight, faArrowDown, faImage, faHandPointer, faFire, faWheatAwn, faEuroSign, faLayerGroup, faReceipt, faUsers, faRightFromBracket, faBars, faGlobe, faCircleInfo, faBell)

// Studio (admin) icons
import {
  faTv, faGear, faPaperPlane, faInbox, faPen, faEye, faCopy, faDownload, faUpRightFromSquare, faReply,
  faCalendarXmark, faPalette, faBullhorn, faGripVertical, faMobileScreen, faDisplay, faWifi, faPlay
} from '@fortawesome/free-solid-svg-icons'
library.add(faTv, faGear, faPaperPlane, faInbox, faPen, faEye, faCopy, faDownload, faUpRightFromSquare, faReply,
  faCalendarXmark, faPalette, faBullhorn, faGripVertical, faMobileScreen, faDisplay, faWifi, faPlay)

export default function installFontAwesome(app) {
  app.component('font-awesome-icon', FontAwesomeIcon)
}
