// Texts for the printed menu, flyers, poster, social posts and the
// customer guide, in German and Arabic.
export default {
  de: {
    bakery: 'Bäckerei',
    placeLine: 'Friedrichstraße · Berlin',
    tagline: 'Früh gebacken, den ganzen Tag geliebt.',
    vegan: 'Vegan',
    vegetarian: 'Vegetarisch',
    hours: 'Öffnungszeiten',
    address: 'Adresse',
    web: 'Online',
    scanToOrder: 'Scannen & online vorbestellen',
    vatNote: 'Alle Preise in Euro inkl. MwSt.',
    allergenNote: 'Informationen zu Allergenen und Zutaten erhalten Sie gern an der Theke und auf unserer Website.',

    menu: {
      title: 'Speisekarte',
      intro: 'Brot, Gebäck und Kuchen – jeden Morgen frisch aus unserem Ofen in der Friedrichstraße.',
      paymentLine: 'Bar oder mit Karte – oder einfach online vorbestellen und abholen.'
    },

    flyer: {
      badge: 'Neu',
      headline: ['Vorbestellen.', 'Abholen.', 'Genießen.'],
      sub: 'Bestellen Sie Ihr Lieblingsgebäck online und holen Sie es zur Wunschzeit frisch ab – ganz ohne Warteschlange.',
      stepsTitle: 'So einfach geht’s',
      steps: [
        ['Auswählen', 'Brot, Gebäck und Kuchen im Online-Shop aussuchen – mit Fotos, Preisen und 3D-Ansicht.'],
        ['Zeit wählen', 'Abholzeit im 30-Minuten-Takt wählen oder liefern lassen.'],
        ['Abholen', 'Frisch eingepackt abholen und bar, mit Karte oder online bezahlen.']
      ],
      perks: ['Bestätigung per E-Mail', 'Deutsch & Englisch', 'Merkliste & Bestellverlauf'],
      deliveryLine: 'Lieferung in Berlin: {fee}'
    },

    breakfast: {
      kicker: 'Frühstück to go',
      headline: 'Guten Morgen, Berlin.',
      sub: 'Der beste Start in den Tag – frisch gebrüht und knusprig gebacken.',
      offerLabel: 'Frühstücksangebot',
      backTitle: 'Schon gewusst?',
      backText: 'Ihr Frühstück steht bereit, wenn Sie kommen: online vorbestellen, Abholzeit wählen und einfach mitnehmen.',
      showCard: 'Gilt im Laden, solange der Vorrat reicht.'
    },

    poster: {
      kicker: 'Jetzt neu',
      headline: ['Online', 'vorbestellen'],
      sub: 'Frisch zur Wunschzeit – ohne Warteschlange.',
      cta: 'QR-Code scannen'
    },

    social: {
      postKicker: 'Jetzt online',
      postHeadline: ['Frisch', 'vorbestellt.'],
      postSub: 'Auswählen, Abholzeit wählen, abholen.',
      storyKicker: 'Neu bei Backlover',
      storyHeadline: ['Dein Gebäck', 'wartet', 'schon.'],
      storySub: 'Online vorbestellen und frisch abholen.',
      link: 'Link in der Bio'
    },

    guide: {
      title: 'Kundeninformation',
      subtitle: 'Alles über unsere Bäckerei und den Online-Shop',
      edition: 'Ausgabe {date}',
      contents: 'Inhalt',
      welcomeTitle: 'Willkommen bei Backlover',
      welcome: [
        'Backlover ist eine kleine Bäckerei in der Friedrichstraße in Berlin. Jeden Morgen backen wir Brot, Croissants, Brezeln, Kuchen und Süßes frisch in unserem eigenen Ofen.',
        'Mit unserem Online-Shop können Sie alles bequem vorbestellen und zu Ihrer Wunschzeit abholen oder liefern lassen. Diese Broschüre zeigt Ihnen Schritt für Schritt, wie das funktioniert – und welche Seiten Sie auf unserer Website finden.'
      ],
      sections: {
        glance: 'Auf einen Blick',
        order: 'Online bestellen in fünf Schritten',
        discover: 'Produkte entdecken',
        pickup: 'Abholung, Lieferung & Bezahlung',
        account: 'Ihr Kundenkonto',
        mobile: 'Auf dem Smartphone',
        inStore: 'Im Laden',
        more: 'Journal, Newsletter & Kontakt',
        allPages: 'Alle Seiten im Überblick',
        privacy: 'Datenschutz & Rechtliches',
        faq: 'Häufige Fragen'
      },
      glance: {
        address: 'Adresse',
        hours: 'Öffnungszeiten',
        web: 'Online-Shop',
        payment: 'Bezahlung',
        paymentText: 'Bar oder mit Karte bei Abholung oder Lieferung; online, sobald Online-Zahlung freigeschaltet ist.',
        delivery: 'Lieferung',
        deliveryText: 'Abholung im Laden kostenlos, Lieferung in Berlin für {fee}.',
        languages: 'Sprachen',
        languagesText: 'Die Website ist auf Deutsch und Englisch verfügbar.'
      },
      orderSteps: [
        ['Shop öffnen', 'Unter {site} finden Sie alle Produkte mit Fotos, Preisen und Hinweisen wie „Vegan“. Filtern Sie nach Kategorie oder suchen Sie gezielt.', 'shop'],
        ['Produkt ansehen', 'Auf der Produktseite drehen Sie das Gebäck in 3D, lesen Zutaten und Allergene und legen es in den Warenkorb.', 'product'],
        ['Warenkorb prüfen', 'Mengen ändern oder entfernen – der Warenkorb bleibt auch ohne Anmeldung erhalten.', 'cart'],
        ['Zeit & Bezahlung wählen', 'An der Kasse melden Sie sich an, wählen Abholung oder Lieferung, den Tag und die Uhrzeit und die Zahlungsart.', 'checkout-time'],
        ['Bestellung bestätigt', 'Sie sehen den Status Ihrer Bestellung und erhalten eine Bestätigung per E-Mail.', 'order']
      ],
      discover: [
        ['Kategorien & Saison', 'Brot, Gebäck, Kuchen, Kekse und saisonale Spezialitäten – jede Kategorie hat ihre eigene Seite.', 'category'],
        ['Saisonales', 'Unter „Saison“ finden Sie, was es nur für kurze Zeit gibt.', 'seasonal']
      ],
      threeD: {
        title: '3D-Ansicht & „Auf deinem Tisch“',
        text: 'Viele Produkte können Sie auf der Produktseite mit dem Finger oder der Maus drehen und heranzoomen. Bei Produkten mit 3D-Modell erscheint auf dem Smartphone die Schaltfläche „Auf deinem Tisch ansehen“: Ihr Gebäck erscheint dann über die Kamera in Originalgröße auf Ihrem Tisch.'
      },
      discoverTips: [
        ['Filter', 'Vegan, vegetarisch oder glutenfrei – mit einem Klick sehen Sie nur passende Produkte.'],
        ['Sortieren & Suchen', 'Nach Name, Preis oder Neuheit sortieren, oder direkt nach einem Produkt suchen.'],
        ['Zutaten & Allergene', 'Jede Produktseite nennt Zutaten, Allergene und Nährwerte.']
      ],
      pickup: [
        ['Abholung', 'Wählen Sie an der Kasse einen Tag und eine Uhrzeit im 30-Minuten-Takt. Die früheste Abholzeit liegt etwa {lead} Minuten nach der Bestellung.'],
        ['Lieferung', 'Wir liefern in Berlin für {fee}. Die früheste Lieferzeit liegt etwa {deliveryLead} Minuten nach der Bestellung.'],
        ['Bezahlung', 'Bar oder mit Karte bei Abholung oder Lieferung. Ist Online-Zahlung freigeschaltet, zahlen Sie direkt mit Karte, Apple Pay oder Google Pay.'],
        ['Stornieren', 'Solange Ihre Bestellung noch nicht abgeholt wurde, können Sie sie auf der Bestellseite stornieren. Online bezahlte Beträge werden automatisch erstattet.']
      ],
      account: [
        ['Bestellungen', 'Alle Bestellungen mit Status, Abholzeit und Beträgen.', 'orders'],
        ['Profil', 'Ihre persönlichen Angaben verwalten.', 'profile'],
        ['Einstellungen', 'Passwort ändern und Lieferadressen speichern.', 'settings'],
        ['Merkliste', 'Lieblingsprodukte mit dem Herz speichern.', 'wishlist'],
        ['Vergleichen', 'Preise, Zutaten und Nährwerte nebeneinander.', 'compare'],
        ['Anmelden & Registrieren', 'Konto anlegen oder Passwort per E-Mail zurücksetzen.', 'register']
      ],
      accountPerks: {
        title: 'Warum ein Kundenkonto?',
        items: ['Schneller bestellen mit gespeicherten Lieferadressen', 'Alle Bestellungen und ihren Status an einem Ort', 'Merkliste auf jedem Gerät', 'Bestellbestätigung und Erinnerungen per E-Mail']
      },
      mobile: 'Die Website passt sich jedem Bildschirm an. Auf dem Smartphone öffnet sich das Menü über die Schaltfläche oben rechts; alle Funktionen stehen genauso zur Verfügung.',
      mobileShots: [['home', 'Startseite'], ['shop', 'Shop'], ['product', 'Produkt in 3D'], ['menu', 'Menü']],
      inStore: {
        title: 'Unsere Menü-Bildschirme',
        text: 'Im Laden zeigen unsere Bildschirme die aktuelle Auswahl mit Preisen – immer auf dem neuesten Stand. Über den QR-Code können Sie direkt online vorbestellen.'
      },
      inStorePoints: [
        ['Immer aktuell', 'Neue Produkte und Preise erscheinen sofort – ohne Austausch von Schildern.'],
        ['Ausverkauft?', 'Was heute vergriffen ist, ist auf dem Bildschirm markiert.'],
        ['Auf einen Blick', 'Vegan, vegetarisch, glutenfrei und Saisonales sind klar gekennzeichnet.']
      ],
      more: [
        ['Journal', 'Geschichten aus der Backstube, neue Produkte und Saisonales.', 'journal'],
        ['Beitrag lesen', 'Jeder Beitrag mit Lesefortschritt und Lesezeit.', 'journal-post'],
        ['Über uns', 'Unsere Geschichte und was uns beim Backen wichtig ist.', 'about'],
        ['Kontakt', 'Schreiben Sie uns – wir antworten so schnell wie möglich.', 'contact']
      ],
      newsletter: 'Newsletter: Unten auf jeder Seite können Sie sich für unseren Newsletter anmelden (einmal im Monat). Abmelden geht jederzeit über den Link in jeder E-Mail.',
      pageNames: {
        home: 'Startseite', shop: 'Shop', seasonal: 'Saison', category: 'Kategorie', product: 'Produktseite',
        cart: 'Warenkorb', checkout: 'Kasse', 'checkout-time': 'Kasse: Zeit wählen', order: 'Bestellbestätigung',
        orders: 'Bestellungen', profile: 'Profil', settings: 'Einstellungen', wishlist: 'Merkliste', compare: 'Vergleichen',
        journal: 'Journal', 'journal-post': 'Journal-Beitrag', about: 'Über uns', contact: 'Kontakt', login: 'Anmelden',
        register: 'Registrieren', 'forgot-password': 'Passwort vergessen', impressum: 'Impressum', privacy: 'Datenschutz',
        terms: 'AGB', cookies: 'Cookie-Richtlinie', 'not-found': 'Seite nicht gefunden', 'menu-board': 'Menü-Bildschirm'
      },
      privacy: [
        'Wir speichern nur, was für Ihre Bestellung nötig ist: Name, E-Mail, gegebenenfalls Telefon und Lieferadresse sowie Ihre Bestellungen.',
        'Die Website verwendet keine Werbe- oder Tracking-Cookies. Im Browser gespeichert werden nur Anmeldung, Warenkorb, Merkliste und Ihre Spracheinstellung.',
        'Online-Zahlungen laufen über unseren Zahlungsdienstleister; Kartendaten erreichen unseren Server nicht.',
        'Impressum, Datenschutzerklärung, AGB und Cookie-Richtlinie finden Sie unten auf jeder Seite.'
      ],
      faq: [
        ['Muss ich ein Konto anlegen?', 'Stöbern und den Warenkorb füllen geht ohne Konto. Zum Bestellen melden Sie sich an der Kasse an oder legen in einer Minute ein Konto an.'],
        ['Wie früh kann ich abholen?', 'Die Kasse zeigt Ihnen die freien Zeiten. Frühestens etwa {lead} Minuten nach der Bestellung.'],
        ['Kann ich meine Bestellung ändern?', 'Stornieren Sie die Bestellung auf der Bestellseite und bestellen Sie neu – oder rufen Sie uns an.'],
        ['Wo finde ich Allergene?', 'Auf jeder Produktseite unter „Zutaten“ und „Allergene“, und jederzeit an der Theke.'],
        ['Passwort vergessen?', 'Auf der Anmeldeseite „Passwort vergessen?“ wählen – Sie erhalten einen Link per E-Mail.'],
        ['Welche Sprache hat die Website?', 'Deutsch und Englisch, umschaltbar oben in der Navigation.'],
        ['Kann ich mit Karte zahlen?', 'Ja, bei Abholung und Lieferung bar oder mit Karte – und online, sobald die Online-Zahlung freigeschaltet ist.'],
        ['Gibt es vegane Produkte?', 'Ja. Im Shop filtern Sie nach vegan, vegetarisch oder glutenfrei; im Laden sind sie gekennzeichnet.'],
        ['Wohin liefern Sie?', 'Innerhalb Berlins für {fee}. Die freien Lieferzeiten sehen Sie an der Kasse.'],
        ['Wie erfahre ich von Neuheiten?', 'Im Journal und in unserem monatlichen Newsletter – die Anmeldung finden Sie unten auf jeder Seite.']
      ],
      backTitle: 'Bis bald in der Friedrichstraße!',
      screenshotNote: 'Abbildungen zeigen die Website mit Beispielprodukten.'
    }
  },

  ar: {
    bakery: 'مخبز',
    placeLine: 'فريدريش شتراسه · برلين',
    tagline: 'يُخبز في الصباح الباكر، ويُحَبّ طوال اليوم.',
    vegan: 'نباتي صرف',
    vegetarian: 'نباتي',
    hours: 'ساعات العمل',
    address: 'العنوان',
    web: 'المتجر الإلكتروني',
    scanToOrder: 'امسح الرمز واطلب مسبقًا عبر الإنترنت',
    vatNote: 'جميع الأسعار باليورو وتشمل ضريبة القيمة المضافة.',
    allergenNote: 'يسعدنا تزويدكم بمعلومات المكونات ومسببات الحساسية عند المنضدة وعلى موقعنا الإلكتروني.',

    menu: {
      title: 'قائمة الطعام',
      intro: 'خبز ومعجنات وكعك، طازجة كل صباح من فرننا في شارع فريدريش شتراسه.',
      paymentLine: 'الدفع نقدًا أو بالبطاقة، أو اطلب مسبقًا عبر الإنترنت واستلم طلبك.'
    },

    flyer: {
      badge: 'جديد',
      headline: ['اطلب مسبقًا.', 'استلم.', 'استمتع.'],
      sub: 'اطلب معجناتك المفضلة عبر الإنترنت واستلمها طازجة في الوقت الذي يناسبك، دون انتظار في الطابور.',
      stepsTitle: 'بكل سهولة',
      steps: [
        ['اختر', 'تصفّح الخبز والمعجنات والكعك في متجرنا الإلكتروني، مع الصور والأسعار والعرض ثلاثي الأبعاد.'],
        ['حدّد الوقت', 'اختر موعد الاستلام كل ٣٠ دقيقة، أو اطلب التوصيل.'],
        ['استلم', 'استلم طلبك طازجًا وادفع نقدًا أو بالبطاقة أو عبر الإنترنت.']
      ],
      perks: ['تأكيد عبر البريد الإلكتروني', 'الألمانية والإنجليزية', 'قائمة المفضلة وسجل الطلبات'],
      deliveryLine: 'التوصيل داخل برلين: {fee}'
    },

    breakfast: {
      kicker: 'فطور سريع',
      headline: 'صباح الخير يا برلين.',
      sub: 'أفضل بداية ليومك: قهوة طازجة ومعجنات مقرمشة.',
      offerLabel: 'عرض الفطور',
      backTitle: 'هل تعلم؟',
      backText: 'فطورك جاهز عند وصولك: اطلب مسبقًا عبر الإنترنت، واختر موعد الاستلام، وخذه معك.',
      showCard: 'العرض ساري في المتجر حتى نفاد الكمية.'
    },

    poster: {
      kicker: 'جديد الآن',
      headline: ['اطلب مسبقًا', 'عبر الإنترنت'],
      sub: 'طازج في الوقت الذي يناسبك، دون انتظار.',
      cta: 'امسح رمز QR'
    },

    social: {
      postKicker: 'متوفر الآن عبر الإنترنت',
      postHeadline: ['اطلب', 'مسبقًا.'],
      postSub: 'اختر، حدّد موعد الاستلام، واستلم.',
      storyKicker: 'جديد في باك لوفر',
      storyHeadline: ['معجناتك', 'بانتظارك', 'بالفعل.'],
      storySub: 'اطلب مسبقًا عبر الإنترنت واستلمها طازجة.',
      link: 'الرابط في الملف الشخصي'
    },

    guide: {
      title: 'دليل العملاء',
      subtitle: 'كل ما تحتاج معرفته عن مخبزنا ومتجرنا الإلكتروني',
      edition: 'إصدار {date}',
      contents: 'المحتويات',
      welcomeTitle: 'أهلًا بكم في باك لوفر',
      welcome: [
        'باك لوفر مخبز صغير في شارع فريدريش شتراسه في برلين. نخبز كل صباح الخبز والكرواسون والبريتزل والكعك والحلويات طازجة في فرننا الخاص.',
        'من خلال متجرنا الإلكتروني يمكنكم طلب كل شيء مسبقًا بسهولة، واستلامه في الوقت الذي يناسبكم أو توصيله إليكم. يشرح لكم هذا الدليل خطوة بخطوة كيف يعمل ذلك، وما الصفحات التي ستجدونها على موقعنا.'
      ],
      sections: {
        glance: 'لمحة سريعة',
        order: 'الطلب عبر الإنترنت في خمس خطوات',
        discover: 'اكتشف منتجاتنا',
        pickup: 'الاستلام والتوصيل والدفع',
        account: 'حسابك الشخصي',
        mobile: 'على الهاتف الذكي',
        inStore: 'في المتجر',
        more: 'المدونة والنشرة البريدية والتواصل',
        allPages: 'جميع الصفحات في لمحة',
        privacy: 'حماية البيانات والمعلومات القانونية',
        faq: 'أسئلة شائعة'
      },
      glance: {
        address: 'العنوان',
        hours: 'ساعات العمل',
        web: 'المتجر الإلكتروني',
        payment: 'الدفع',
        paymentText: 'نقدًا أو بالبطاقة عند الاستلام أو التوصيل، وعبر الإنترنت عند تفعيل الدفع الإلكتروني.',
        delivery: 'التوصيل',
        deliveryText: 'الاستلام من المتجر مجاني، والتوصيل داخل برلين مقابل {fee}.',
        languages: 'اللغات',
        languagesText: 'الموقع متوفر باللغتين الألمانية والإنجليزية. تعرض الصور في هذا الدليل النسخة الإنجليزية.'
      },
      orderSteps: [
        ['افتح المتجر', 'على {site} تجد جميع المنتجات مع الصور والأسعار وعلامات مثل «نباتي». صفِّ حسب الفئة أو ابحث مباشرة.', 'shop'],
        ['شاهد المنتج', 'في صفحة المنتج يمكنك تدوير المعجنات بتقنية ثلاثية الأبعاد، والاطلاع على المكونات ومسببات الحساسية، ثم إضافتها إلى السلة.', 'product'],
        ['راجع السلة', 'غيّر الكميات أو احذف المنتجات، وتبقى السلة محفوظة حتى دون تسجيل الدخول.', 'cart'],
        ['اختر الوقت وطريقة الدفع', 'عند الدفع تسجّل الدخول، وتختار الاستلام أو التوصيل، واليوم والساعة، وطريقة الدفع.', 'checkout-time'],
        ['تم تأكيد الطلب', 'تشاهد حالة طلبك وتصلك رسالة تأكيد عبر البريد الإلكتروني.', 'order']
      ],
      discover: [
        ['الفئات', 'الخبز والمعجنات والكعك والبسكويت والمنتجات الموسمية، ولكل فئة صفحتها الخاصة.', 'category'],
        ['المنتجات الموسمية', 'في قسم «الموسم» تجد ما يتوفر لفترة قصيرة فقط.', 'seasonal']
      ],
      threeD: {
        title: 'العرض ثلاثي الأبعاد و«شاهده على طاولتك»',
        text: 'يمكنك تدوير كثير من المنتجات وتكبيرها في صفحة المنتج بإصبعك أو بالفأرة. وللمنتجات التي لها نموذج ثلاثي الأبعاد يظهر على الهاتف زر «شاهده على طاولتك»، فتظهر المعجنات عبر الكاميرا بحجمها الحقيقي على طاولتك.'
      },
      discoverTips: [
        ['التصفية', 'نباتي أو نباتي مع ألبان أو خالٍ من الغلوتين – بنقرة واحدة ترى المنتجات المناسبة فقط.'],
        ['الترتيب والبحث', 'رتّب حسب الاسم أو السعر أو الأحدث، أو ابحث مباشرة عن منتج.'],
        ['المكونات والحساسية', 'تذكر كل صفحة منتج المكونات ومسببات الحساسية والقيم الغذائية.']
      ],
      pickup: [
        ['الاستلام', 'اختر عند الدفع يومًا وساعة بفواصل ٣٠ دقيقة. أقرب موعد للاستلام بعد نحو {lead} دقيقة من الطلب.'],
        ['التوصيل', 'نوصّل داخل برلين مقابل {fee}. أقرب موعد للتوصيل بعد نحو {deliveryLead} دقيقة من الطلب.'],
        ['الدفع', 'نقدًا أو بالبطاقة عند الاستلام أو التوصيل. وعند تفعيل الدفع الإلكتروني يمكنك الدفع مباشرة بالبطاقة أو Apple Pay أو Google Pay.'],
        ['الإلغاء', 'يمكنك إلغاء طلبك من صفحة الطلب ما دام لم يُستلم بعد، وتُسترد المبالغ المدفوعة إلكترونيًا تلقائيًا.']
      ],
      account: [
        ['الطلبات', 'جميع طلباتك مع الحالة وموعد الاستلام والمبالغ.', 'orders'],
        ['الملف الشخصي', 'إدارة بياناتك الشخصية.', 'profile'],
        ['الإعدادات', 'تغيير كلمة المرور وحفظ عناوين التوصيل.', 'settings'],
        ['المفضلة', 'احفظ منتجاتك المفضلة بالضغط على القلب.', 'wishlist'],
        ['المقارنة', 'الأسعار والمكونات والقيم الغذائية جنبًا إلى جنب.', 'compare'],
        ['الدخول والتسجيل', 'أنشئ حسابًا أو استعد كلمة المرور عبر البريد الإلكتروني.', 'register']
      ],
      accountPerks: {
        title: 'لماذا حساب شخصي؟',
        items: ['طلب أسرع مع عناوين التوصيل المحفوظة', 'جميع طلباتك وحالتها في مكان واحد', 'قائمة المفضلة على كل أجهزتك', 'تأكيد الطلب والتذكيرات عبر البريد الإلكتروني']
      },
      mobile: 'يتكيّف الموقع مع كل شاشة. على الهاتف تُفتح القائمة من الزر أعلى الشاشة، وتتوفر جميع الوظائف بالطريقة نفسها.',
      mobileShots: [['home', 'الصفحة الرئيسية'], ['shop', 'المتجر'], ['product', 'المنتج ثلاثي الأبعاد'], ['menu', 'القائمة']],
      inStore: {
        title: 'شاشات القائمة في متجرنا',
        text: 'تعرض الشاشات في المتجر تشكيلتنا الحالية مع الأسعار، محدّثة دائمًا. ويمكنك عبر رمز QR الطلب مسبقًا مباشرة عبر الإنترنت.'
      },
      inStorePoints: [
        ['محدّثة دائمًا', 'تظهر المنتجات والأسعار الجديدة فورًا، دون تغيير اللافتات.'],
        ['نفد من المخزون؟', 'ما نفد اليوم يظهر مُعلَّمًا على الشاشة.'],
        ['بنظرة واحدة', 'المنتجات النباتية والخالية من الغلوتين والموسمية مُعلَّمة بوضوح.']
      ],
      more: [
        ['المدونة', 'قصص من المخبز والمنتجات الجديدة والموسمية.', 'journal'],
        ['قراءة مقال', 'كل مقال مع مؤشر التقدم ومدة القراءة.', 'journal-post'],
        ['من نحن', 'قصتنا وما يهمنا في الخَبز.', 'about'],
        ['تواصل معنا', 'راسلنا وسنرد عليك في أسرع وقت ممكن.', 'contact']
      ],
      newsletter: 'النشرة البريدية: يمكنك الاشتراك في نشرتنا الشهرية من أسفل كل صفحة، وإلغاء الاشتراك في أي وقت عبر الرابط الموجود في كل رسالة.',
      pageNames: {
        home: 'الصفحة الرئيسية', shop: 'المتجر', seasonal: 'الموسم', category: 'الفئة', product: 'صفحة المنتج',
        cart: 'السلة', checkout: 'الدفع', 'checkout-time': 'الدفع: اختيار الوقت', order: 'تأكيد الطلب',
        orders: 'الطلبات', profile: 'الملف الشخصي', settings: 'الإعدادات', wishlist: 'المفضلة', compare: 'المقارنة',
        journal: 'المدونة', 'journal-post': 'مقال', about: 'من نحن', contact: 'تواصل معنا', login: 'تسجيل الدخول',
        register: 'إنشاء حساب', 'forgot-password': 'نسيت كلمة المرور', impressum: 'بيانات الناشر', privacy: 'حماية البيانات',
        terms: 'الشروط العامة', cookies: 'سياسة ملفات تعريف الارتباط', 'not-found': 'الصفحة غير موجودة', 'menu-board': 'شاشة القائمة'
      },
      privacy: [
        'لا نحفظ إلا ما يلزم لطلبك: الاسم والبريد الإلكتروني، وعند الحاجة رقم الهاتف وعنوان التوصيل، إضافة إلى طلباتك.',
        'لا يستخدم الموقع ملفات تعريف ارتباط للإعلانات أو التتبع. يُحفظ في المتصفح فقط تسجيل الدخول والسلة والمفضلة واللغة المختارة.',
        'تتم المدفوعات الإلكترونية عبر مزوّد خدمة الدفع لدينا، ولا تصل بيانات البطاقة إلى خوادمنا.',
        'تجد بيانات الناشر وسياسة الخصوصية والشروط العامة وسياسة ملفات تعريف الارتباط أسفل كل صفحة.'
      ],
      faq: [
        ['هل أحتاج إلى إنشاء حساب؟', 'يمكنك التصفح وملء السلة دون حساب. وللطلب تسجّل الدخول عند الدفع أو تنشئ حسابًا في دقيقة واحدة.'],
        ['ما أقرب موعد للاستلام؟', 'تعرض لك صفحة الدفع المواعيد المتاحة، وأقربها بعد نحو {lead} دقيقة من الطلب.'],
        ['هل يمكنني تعديل طلبي؟', 'ألغِ الطلب من صفحة الطلب واطلب من جديد، أو اتصل بنا.'],
        ['أين أجد معلومات الحساسية؟', 'في كل صفحة منتج تحت «المكونات» و«مسببات الحساسية»، وفي أي وقت عند المنضدة.'],
        ['نسيت كلمة المرور؟', 'اختر «نسيت كلمة المرور؟» في صفحة تسجيل الدخول، وسيصلك رابط عبر البريد الإلكتروني.'],
        ['ما لغة الموقع؟', 'الألمانية والإنجليزية، ويمكن التبديل بينهما من شريط التنقل في الأعلى.'],
        ['هل يمكنني الدفع بالبطاقة؟', 'نعم، نقدًا أو بالبطاقة عند الاستلام والتوصيل، وإلكترونيًا عند تفعيل الدفع عبر الإنترنت.'],
        ['هل توجد منتجات نباتية؟', 'نعم. في المتجر الإلكتروني يمكنك التصفية حسب النباتي أو الخالي من الغلوتين، وهي مُعلَّمة في المتجر أيضًا.'],
        ['إلى أين توصّلون؟', 'داخل برلين مقابل {fee}. تجد مواعيد التوصيل المتاحة في صفحة الدفع.'],
        ['كيف أعرف بالمنتجات الجديدة؟', 'في المدونة وفي نشرتنا البريدية الشهرية، والاشتراك أسفل كل صفحة.']
      ],
      backTitle: 'نراكم قريبًا في فريدريش شتراسه!',
      screenshotNote: 'تعرض الصور الموقع مع منتجات على سبيل المثال.'
    }
  }
}
