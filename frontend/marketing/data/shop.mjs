// The shop's details as printed on the menu, flyers, posters and the
// customer guide. Check every line before printing; empty values are left out.
export default {
  name: 'Backlover',
  street: 'Friedrichstraße',
  city: 'Berlin', // add the postcode, e.g. '10117 Berlin'
  transit: { de: 'U-Bahn Friedrichstraße', ar: 'محطة مترو فريدريش شتراسه' },
  // Printed as text and used for the QR codes. Set the real domain before printing!
  website: 'https://www.backlover.de',
  phone: '',
  email: '',
  instagram: '',
  // Same hours as SHOP_OPENING_HOURS on the server.
  hours: {
    de: [['Montag – Freitag', '07:00 – 18:00'], ['Samstag', '07:00 – 14:00'], ['Sonntag', '08:00 – 12:00']],
    ar: [['الاثنين – الجمعة', '07:00 – 18:00'], ['السبت', '07:00 – 14:00'], ['الأحد', '08:00 – 12:00']]
  },
  // From the shop settings (SHOP_DELIVERY_FEE, pickup and delivery lead times).
  deliveryFee: 3.5,
  pickupLeadMinutes: 60,
  deliveryLeadMinutes: 120,
  // SHOP_SLOT_MINUTES and SHOP_SLOT_DAYS
  slotMinutes: 30,
  slotDays: 7
}
