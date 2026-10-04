// The printed menu. Prices are examples: set your own before printing.
// `image` is a file in frontend/src/assets/bakery.
export default [
  {
    key: 'pastries',
    title: { de: 'Gebäck', ar: 'المعجنات' },
    note: { de: 'Jeden Morgen frisch laminiert', ar: 'تُحضَّر طازجة كل صباح' },
    items: [
      { name: { de: 'Buttercroissant', ar: 'كرواسون بالزبدة' }, desc: { de: 'Französische Butter, 27 Schichten', ar: 'زبدة فرنسية و27 طبقة مقرمشة' }, price: 1.8, image: 'croissant-butter.png', tags: ['vegetarian'] },
      { name: { de: 'Schokocroissant', ar: 'كرواسون بالشوكولاتة' }, desc: { de: 'Mit dunkler Schokolade', ar: 'محشو بالشوكولاتة الداكنة' }, price: 2.3, image: 'croissant-chocolate.png', tags: ['vegetarian'] },
      { name: { de: 'Laugenbrezel', ar: 'بريتزل ألماني' }, desc: { de: 'Mit grobem Salz, außen knusprig', ar: 'بالملح الخشن، مقرمش من الخارج' }, price: 1.2, image: 'pretzel.png', tags: ['vegan'] }
    ]
  },
  {
    key: 'savoury',
    title: { de: 'Herzhaft', ar: 'المالحات' },
    note: { de: 'Belegt nach Ihrer Wahl', ar: 'تُحضَّر حسب طلبك' },
    items: [
      { name: { de: 'Belegtes Baguette', ar: 'باغيت محشو' }, desc: { de: 'Käse, Tomate, frischer Salat', ar: 'جبن وطماطم وخس طازج' }, price: 4.9, image: '_8b3e5425-2b1c-47e2-9b11-fa54cd4c6380-removebg-preview.png' },
      { name: { de: 'Puten-Sandwich', ar: 'ساندويتش ديك رومي' }, desc: { de: 'Putenbrust, Käse, Salat', ar: 'صدر ديك رومي وجبن وخس' }, price: 4.5, image: 'WhatsApp_Image_2025-01-17_at_15.47.19_c64dd93f-removebg-preview.png' },
      { name: { de: 'Veggie-Bowl', ar: 'طبق نباتي' }, desc: { de: 'Kichererbsen, Avocado, Gemüse', ar: 'حمص وأفوكادو وخضار موسمية' }, price: 7.9, image: 'vbowl.png', tags: ['vegan'] }
    ]
  },
  {
    key: 'sweets',
    title: { de: 'Süßes', ar: 'الحلويات' },
    note: { de: 'Kuchen, Donuts & feine Kleinigkeiten', ar: 'دونات وكيك وحلويات صغيرة' },
    items: [
      { name: { de: 'Donut', ar: 'دونات' }, desc: { de: 'Hefeteig mit Schokoglasur', ar: 'بعجينة الخميرة وطبقة شوكولاتة' }, price: 1.9, image: 'donut.png', tags: ['vegetarian'] },
      { name: { de: 'Karamell-Donut', ar: 'دونات بالكراميل' }, desc: { de: 'Mit Karamellglasur', ar: 'بطبقة الكراميل' }, price: 2.2, image: 'donut-caramel.png', tags: ['vegetarian'] },
      { name: { de: 'Éclair', ar: 'إكلير' }, desc: { de: 'Brandteig, Vanillecreme, Schokolade', ar: 'عجينة الشو مع كريمة الفانيلا والشوكولاتة' }, price: 3.2, image: 'eclair.png', tags: ['vegetarian'] },
      { name: { de: 'Macarons (3 Stück)', ar: 'ماكرون (3 قطع)' }, desc: { de: 'Himbeere, Pistazie, Vanille', ar: 'توت العليق والفستق والفانيلا' }, price: 4.5, image: 'macarons.png', tags: ['vegetarian'] },
      { name: { de: 'Schoko-Cookie', ar: 'كوكيز بالشوكولاتة' }, desc: { de: 'Weich gebacken, große Stücke', ar: 'طري مع قطع شوكولاتة كبيرة' }, price: 1.9, image: 'cookie.png', tags: ['vegetarian'] },
      { name: { de: 'Beeren-Cupcake', ar: 'كب كيك بالتوت' }, desc: { de: 'Vanille, Buttercreme, Beeren', ar: 'فانيلا وكريمة الزبدة والتوت' }, price: 3.5, image: 'cupcake.png', tags: ['vegetarian'] }
    ]
  },
  {
    key: 'drinks',
    title: { de: 'Kaffee & Getränke', ar: 'القهوة والمشروبات' },
    note: { de: 'Mit Hafermilch ohne Aufpreis', ar: 'حليب الشوفان دون تكلفة إضافية' },
    items: [
      { name: { de: 'Espresso', ar: 'إسبريسو' }, desc: { de: 'Single Origin, kräftig', ar: 'حبوب مختارة، نكهة قوية' }, price: 2.1, image: 'coffee2.png', tags: ['vegan'] },
      { name: { de: 'Café Crème', ar: 'قهوة كريمة' }, desc: { de: 'Mild, mit feiner Crema', ar: 'خفيفة مع طبقة كريما ناعمة' }, price: 2.6, image: 'coffee3.png', tags: ['vegan'] },
      { name: { de: 'Cappuccino', ar: 'كابتشينو' }, desc: { de: 'Espresso, Milchschaum', ar: 'إسبريسو مع رغوة الحليب' }, price: 3.2, image: 'cuppchtino.png', tags: ['vegetarian'] },
      { name: { de: 'Flat White', ar: 'فلات وايت' }, desc: { de: 'Doppelter Espresso, samtige Milch', ar: 'إسبريسو مزدوج وحليب مخملي' }, price: 3.6, image: 'cuppo.png', tags: ['vegetarian'] },
      { name: { de: 'Latte Macchiato', ar: 'لاتيه ماكياتو' }, desc: { de: 'Viel Milch, wenig Bitterkeit', ar: 'حليب وفير ومذاق ناعم' }, price: 3.6, image: 'latte.png', tags: ['vegetarian'] },
      { name: { de: 'Heiße Schokolade', ar: 'شوكولاتة ساخنة' }, desc: { de: 'Mit Sahnehaube', ar: 'مع الكريمة المخفوقة' }, price: 3.4, image: 'hotchocolate.png', tags: ['vegetarian'] }
    ]
  }
]
