// Single source for the shop's public details (footer, contact, legal pages).
// Empty values are shown as "to be added" on the legal pages and hidden elsewhere.
export const business = {
  name: 'Backlover',
  legalName: '', // e.g. "Backlover GmbH" or the owner's full name
  owner: '', // person responsible for the content (Impressum)
  street: 'Friedrichstraße',
  houseNumber: '',
  postalCode: '',
  city: 'Berlin',
  country: 'Deutschland',
  transit: 'U-Bahn Friedrichstraße',
  email: '',
  phone: '',
  vatId: '', // USt-IdNr., if any
  register: '', // Handelsregister entry, if any
  openingHours: [], // e.g. [{ days: 'Mon–Fri', hours: '07:00–18:00' }]
  // Pickup and delivery times are shown on the shop's clock, wherever the
  // visitor is (the bookable slots come from the backend's opening hours).
  timeZone: 'Europe/Berlin',
  // Optional Spline scene for the home page hero (see .env.example).
  splineScene: import.meta.env.VITE_SPLINE_SCENE || '',
  social: {
    instagram: '',
    facebook: '',
    twitter: ''
  }
}

export const streetLine = () =>
  [business.street, business.houseNumber].filter(Boolean).join(' ')

export const cityLine = () =>
  [business.postalCode, business.city].filter(Boolean).join(' ')
