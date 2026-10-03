// Texts for the owner handbook (marketing/docs/handbook.mjs): how to run the
// shop day to day. **Text** marks a button or menu name in the admin. The
// Arabic edition shows the English admin, so its button names are English.
export default {
  de: {
    title: 'Handbuch für Ihren Online-Shop',
    subtitle: 'Bestellungen, Produkte, Menü-Bildschirm und Einstellungen – alles für den täglichen Betrieb.',
    eyebrow: 'Backlover Studio · Verwaltung',
    edition: 'Ausgabe {date}',
    runTitle: 'Handbuch',
    contents: 'Inhalt',
    screenshotNote: 'Abbildungen zeigen die Verwaltung mit Beispieldaten.',
    sections: {
      overview: 'Das System im Überblick',
      dashboard: 'Anmelden & Übersicht',
      orders: 'Bestellungen bearbeiten',
      alerts: 'Neue Bestellungen nicht verpassen',
      routine: 'Der Tagesablauf',
      products: 'Produkte verwalten',
      productForm: 'Ein Produkt anlegen',
      productDetail: 'Bestand, Zutaten & Allergene',
      categories: 'Kategorien',
      users: 'Kunden & Team',
      content: 'Journal, Nachrichten & Newsletter',
      menuBoard: 'Der Menü-Bildschirm im Laden',
      emails: 'Automatische E-Mails',
      settings: 'Einstellungen & Online-Zahlung',
      security: 'Sicherheit & Pflege',
      help: 'Hilfe & Checklisten'
    },

    welcomeTitle: 'Willkommen in Ihrer Verwaltung',
    welcome: [
      'Dieses Handbuch erklärt alles, was Sie für den täglichen Betrieb Ihres Online-Shops brauchen: Bestellungen annehmen und bearbeiten, Produkte und Preise pflegen, den Menü-Bildschirm im Laden einrichten und die wichtigsten Einstellungen.',
      'Technische Kenntnisse brauchen Sie dafür nicht. Alles Tägliche erledigen Sie im Browser – am Computer, Tablet oder Smartphone. Nur wenige Einstellungen (Kapitel 14) werden einmalig auf dem Server vorgenommen, am besten zusammen mit Ihrem Webentwickler.'
    ],

    overview: {
      intro: 'Ihr Shop besteht aus wenigen Bausteinen, die zusammenarbeiten. Alles, was Sie in der Verwaltung ändern, ist sofort im Shop und auf dem Menü-Bildschirm sichtbar.',
      parts: [
        ['Online-Shop', '/', 'Hier stöbern und bestellen Ihre Kundinnen und Kunden – auf Deutsch und Englisch.'],
        ['Verwaltung', '/admin', 'Bestellungen, Produkte, Kategorien und Benutzer. Hier arbeiten Sie jeden Tag.'],
        ['Django-Verwaltung', '/django-admin/', 'Journal-Beiträge, Kontaktnachrichten, Newsletter, Zutaten, Allergene und Nährwerte.'],
        ['Menü-Bildschirm', '/menu-board', 'Ihre aktuelle Auswahl mit Preisen für den Fernseher im Laden.'],
        ['E-Mails', '', 'Bestätigungen für Ihre Kunden und eine Nachricht an Sie bei jeder neuen Bestellung.'],
        ['Online-Zahlung', 'Stripe', 'Karte, Apple Pay, Google Pay und mehr – sobald Stripe verbunden ist.']
      ],
      accessTitle: 'Ihre Zugänge',
      accessLines: ['Adresse des Shops', 'E-Mail Ihres Admin-Kontos', 'Adresse der Django-Verwaltung'],
      accessNote: 'Notieren Sie hier niemals Passwörter. Sie melden sich auf der normalen Anmeldeseite des Shops an – als Admin landen Sie direkt in der Verwaltung.',
      language: 'Unten in der Seitenleiste wechseln Sie mit **English** / **Deutsch** die Sprache der Verwaltung. **Zum Shop** öffnet Ihren Shop, **Menü-Bildschirm** die digitale Speisekarte.'
    },

    dashboard: {
      intro: 'Nach der Anmeldung sehen Sie die **Übersicht**. Sie zeigt auf einen Blick, was heute los ist.',
      points: [
        ['Begrüßung', 'Bestellungen und Umsatz von heute. **Offene Bestellungen** führt direkt zur Liste der Bestellungen.'],
        ['Kennzahlen', 'Umsatz aus abgeschlossenen Bestellungen, alle und offene Bestellungen, Produkte mit wenig Bestand und neue Kunden.'],
        ['Neueste Bestellungen', 'Die letzten Bestellungen mit Betrag, Abholung oder Lieferung und Status.'],
        ['Wird knapp', 'Produkte mit 10 Stück oder weniger. **Auffüllen** öffnet das Produkt, um den Bestand zu ändern.'],
        ['Glocke', 'Oben rechts schalten Sie Desktop-Benachrichtigungen für neue Bestellungen ein (Kapitel 04).']
      ]
    },

    orders: {
      intro: 'Unter **Bestellungen** finden Sie alle Bestellungen, die neuesten zuerst. Jede Zeile zeigt Bestellnummer, Kunde, Bestellzeit, Abholung oder Lieferung mit Wunschzeit, Status und Betrag.',
      filters: 'Suchen Sie nach Bestellnummer, Name oder E-Mail und filtern Sie nach Status, Abholung oder Lieferung und Zeitraum.',
      flowTitle: 'Der Weg einer Bestellung',
      flow: [
        ['Offen', 'Neu eingegangen'],
        ['In Arbeit', 'Wird vorbereitet'],
        ['Abgeschlossen', 'Abgeholt oder geliefert'],
        ['Storniert', 'Von Ihnen oder vom Kunden']
      ],
      detailTitle: 'Eine Bestellung bearbeiten',
      detailIntro: 'Ein Klick auf **Details** öffnet die Bestellung mit allen Angaben: Kunde, Abholung oder Lieferadresse, Wunschzeit, Zahlungsart, Hinweise des Kunden und alle Artikel.',
      actions: [
        ['Zubereitung starten', 'Der Status wird „In Arbeit“. So sieht das ganze Team, dass sich jemand kümmert.'],
        ['Als übergeben markieren', 'Wenn die Bestellung abgeholt oder geliefert wurde. Bar- und Kartenzahlungen gelten damit als bezahlt, der Umsatz erscheint in der Übersicht.'],
        ['Bestellung stornieren', 'Der Bestand wird zurückgebucht, der Kunde bekommt eine E-Mail. Online bezahlte Beträge erstattet der Shop automatisch über Stripe.'],
        ['Hinweis für den Fahrer', 'Bei Lieferungen: Sendungsnummer oder eine Notiz für den Fahrer eintragen.']
      ],
      note: 'Eine Bestellung geht immer von „Offen“ über „In Arbeit“ zu „Abgeschlossen“. Abgeschlossene und stornierte Bestellungen lassen sich nicht mehr ändern.'
    },

    alerts: {
      intro: 'Solange die Verwaltung in einem sichtbaren Browser-Tab geöffnet ist, prüft sie alle 30 Sekunden, ob neue Bestellungen eingegangen sind – und meldet sich auf mehreren Wegen.',
      channels: [
        ['Hinweis', 'Unten im Fenster erscheint „Neue Bestellung …“.'],
        ['Signalton', 'Ein kurzer Ton. Klicken Sie nach dem Öffnen einmal in die Seite, damit der Browser Töne erlaubt.'],
        ['Zähler', 'Die Zahl neuer Bestellungen steht im Titel des Browser-Tabs und bei „Bestellungen“.'],
        ['Benachrichtigung', 'Über die Glocke oben rechts eingeschaltet, meldet auch Ihr Computer oder Tablet jede neue Bestellung.'],
        ['E-Mail', 'Zusätzlich geht jede Bestellung an Ihre Shop-Adresse – auch wenn die Verwaltung geschlossen ist.']
      ],
      tipTitle: 'Unser Tipp für die Theke',
      tip: 'Ein Tablet mit geöffneter Verwaltung, automatische Bildschirmsperre aus, Ton an. Die Verwaltung funktioniert auch auf dem Smartphone – das Menü öffnen Sie oben über die Menü-Schaltfläche.',
      phoneLabels: ['Übersicht', 'Bestellungen']
    },

    routine: {
      intro: 'So sieht ein typischer Tag mit dem Online-Shop aus.',
      day: [
        ['Morgens', 'Übersicht öffnen, die Bestellungen für heute nach Abholzeit vorbereiten und die Bestände an die Backmenge anpassen.'],
        ['Tagsüber', 'Neue Bestellungen annehmen (**Zubereitung starten**) und bei Übergabe **Als übergeben markieren**. Ausverkauftes auf Bestand 0 setzen.'],
        ['Abends', 'Bestellungen für morgen ansehen, Bestände für den nächsten Tag eintragen, Kontaktnachrichten beantworten.'],
        ['Jede Woche', 'Neue und saisonale Produkte anlegen, einen Journal-Beitrag schreiben, den Umsatz in der Übersicht ansehen.']
      ],
      rulesTitle: 'So funktionieren Abhol- und Lieferzeiten',
      rules: [
        ['Zeitfenster', 'Kunden wählen Tag und Uhrzeit im {slot}-Minuten-Takt, bis zu {days} Tage im Voraus und nur innerhalb Ihrer Öffnungszeiten.'],
        ['Vorlaufzeit', 'Abholung frühestens {pickup} Minuten, Lieferung frühestens {delivery} Minuten nach der Bestellung.'],
        ['Kapazität', 'Auf Wunsch höchstens eine bestimmte Zahl an Bestellungen pro Zeitfenster; volle Fenster sind dann belegt.'],
        ['Bestand', 'Beim Bestellen wird der Bestand sofort abgezogen, bei einer Stornierung kommt er zurück. Bei 0 ist ein Produkt „Ausverkauft“.'],
        ['Online-Zahlung', 'Bezahlt ein Kunde online nicht innerhalb von 30 Minuten, storniert der Shop die Bestellung automatisch.']
      ]
    },

    products: {
      intro: 'Unter **Produkte** sehen Sie Ihr ganzes Sortiment – auch Entwürfe und eingestellte Produkte, die im Shop nicht erscheinen.',
      points: [
        ['Kennzahlen', 'Produkte gesamt, aktive Produkte, Produkte mit wenig Bestand und der Wert des Bestands.'],
        ['Filter & Suche', 'Nach Kategorie, Status, Preisspanne und Lagerstatus filtern; das Suchfeld durchsucht die Liste.'],
        ['Aktionen', 'Auge: Produktdetails. Stift: bearbeiten. Papierkorb: löschen – kommt ein Produkt in früheren Bestellungen vor, wird es stattdessen als „Eingestellt“ markiert.']
      ],
      visibleTitle: 'Wann erscheint ein Produkt im Shop?',
      visible: ['Status „Aktiv“', '„Bestellbar“ ist angehakt', 'Die Kategorie ist eingeblendet'],
      visibleNote: 'Mit Bestand 0 bleibt es sichtbar, wird aber als ausverkauft angezeigt.'
    },

    productForm: {
      intro: 'Mit **Produkt hinzufügen** oder dem Stift öffnen Sie das Formular. Mit **Produkt anlegen** bzw. **Änderungen speichern** ist es sofort im Shop.',
      fields: [
        ['Name & Beschreibung', 'Auf Deutsch, der Hauptsprache des Shops. Die Beschreibung steht auf der Produktseite und dem Menü-Bildschirm.'],
        ['Englisch (optional)', 'Leer gelassen, zeigt der Shop auch auf Englisch den deutschen Text.'],
        ['Kategorie & Status', '„Entwurf“ für Produkte in Vorbereitung, „Aktiv“ für den Verkauf, „Eingestellt“ für Produkte, die es nicht mehr gibt.'],
        ['Preis', 'In Euro inklusive Mehrwertsteuer, mit Punkt: 2.40'],
        ['Bestand', 'Wie viele Stück verkauft werden können. Sinkt bei jeder Bestellung automatisch.'],
        ['Foto', 'JPG, PNG oder WebP bis 5 MB. Am schönsten ist ein freigestelltes PNG mit transparentem Hintergrund.'],
        ['3D-Modell (optional)', 'Eine .glb-Datei bis 20 MB für die 360°-Ansicht und „Auf deinem Tisch ansehen“. Ohne Modell erzeugt der Shop eine 3D-Ansicht aus dem Foto.'],
        ['Eigenschaften', 'Bestellbar, Saison, Vegan, Vegetarisch, Glutenfrei – als Kennzeichnung im Shop, als Filter und auf dem Menü-Bildschirm.']
      ],
      photoTitle: 'Tipps für gute Produktfotos',
      photo: ['Tageslicht, kein Blitz', 'Heller, ruhiger Hintergrund – oder freistellen', 'Quadratisch, mindestens 1200 × 1200 Pixel', 'Alle Produkte im gleichen Stil und Winkel']
    },

    productDetail: {
      intro: 'Das Auge in der Produktliste öffnet die Detailseite mit Foto, Grunddaten, Nährwerten pro 100 g sowie Zutaten und Allergenen.',
      stockTitle: 'Bestand schnell ändern',
      stock: 'Unter **Bestandsverwaltung** die neue Stückzahl eingeben und **Aktualisieren** klicken – zum Beispiel morgens nach dem Backen. Der eingegebene Wert ersetzt den bisherigen Bestand.',
      allergenTitle: 'Zutaten, Allergene & Nährwerte',
      allergenIntro: 'Diese Angaben pflegen Sie in der Django-Verwaltung im Bereich **Products**:',
      allergenSteps: [
        '**Allergen information**: die Allergene einmal anlegen, z. B. Gluten, Milch, Ei, Schalenfrüchte.',
        '**Ingredients**: Zutaten anlegen und ihnen die passenden Allergene zuordnen.',
        '**Nutrition information**: Nährwerte pro 100 g anlegen.',
        '**Products**: im Produkt die Zutaten auswählen und die Nährwerte zuordnen.'
      ],
      allergenNote: 'Allergenangaben sind auch beim Online-Verkauf Pflicht. Prüfen Sie sie bei jeder Rezeptänderung.'
    },

    categories: {
      intro: 'Kategorien gliedern Ihren Shop, zum Beispiel Brot, Gebäck, Kuchen und Kekse. Jede hat eine eigene Seite im Shop.',
      points: [
        ['Kategorie hinzufügen', 'Name und Beschreibung auf Deutsch, optional auf Englisch.'],
        ['Position', 'Niedrigere Zahlen erscheinen zuerst – im Shop und auf dem Menü-Bildschirm.'],
        ['Ausblenden & Einblenden', 'Ausgeblendete Kategorien und ihre Produkte verschwinden aus dem Shop, bleiben aber gespeichert – praktisch für Saisonware.'],
        ['Shop-Link', 'Die Adresse der Kategorie-Seite, etwa für Instagram. Ihr letzter Teil (z. B. „pastries“) filtert auch den Menü-Bildschirm.']
      ]
    },

    users: {
      intro: 'Unter **Benutzer** sehen Sie alle Konten – Ihre Kundinnen und Kunden und Ihr Team – mit Registrierungsdatum und Anzahl der Bestellungen.',
      points: [
        ['Deaktivieren', 'Das Konto kann sich nicht mehr anmelden, seine Bestellungen bleiben erhalten. Mit **Reaktivieren** jederzeit rückgängig.'],
        ['Zum Admin machen', 'Gibt vollen Zugriff auf die Verwaltung – nur für Ihr Team.'],
        ['Adminrechte entziehen', 'Wenn jemand Ihr Team verlässt.']
      ],
      teamTitle: 'Ihr Team',
      team: [
        'Jede Person bekommt ein eigenes Konto – keine gemeinsamen Passwörter.',
        'Mitarbeitende registrieren sich ganz normal im Shop; danach machen Sie sie hier zum Admin.',
        'Ihr eigenes Konto können Sie hier nicht ändern – so sperren Sie sich nicht versehentlich aus.',
        'Die Django-Verwaltung nutzt das Hauptkonto aus der Einrichtung. Weitere Personen brauchen dort eigene Rechte (Bereich **Users**).'
      ]
    },

    content: {
      intro: 'Diese Bereiche pflegen Sie in der Django-Verwaltung. Melden Sie sich dort mit der E-Mail-Adresse und dem Passwort Ihres Hauptkontos an.',
      postsTitle: 'Einen Journal-Beitrag schreiben',
      posts: [
        '**Content → Posts → Post hinzufügen** öffnen.',
        'Titel, kurze Zusammenfassung (**Excerpt**) und Text (**Body**). Absätze trennen Sie mit einer Leerzeile.',
        'Optional ein Titelbild (**Cover image**).',
        '**Published at**: Zeitpunkt der Veröffentlichung. Leer = Entwurf; ein Datum in der Zukunft veröffentlicht den Beitrag automatisch.'
      ],
      messagesTitle: 'Kontaktnachrichten',
      messages: 'Nachrichten aus dem Kontaktformular stehen unter **Contact messages** und kommen zusätzlich per E-Mail. Antworten Sie per E-Mail und haken Sie danach **Handled** an.',
      newsletterTitle: 'Newsletter',
      newsletter: 'Unter **Newsletter subscribers** stehen alle Anmeldungen aus dem Shop. Für den Versand nutzen Sie einen Newsletter-Dienst. Schreiben Sie nur an Adressen ohne Datum bei **Unsubscribed at** – alle anderen haben sich abgemeldet.'
    },

    menuBoard: {
      intro: 'Unter **/menu-board** zeigt der Shop Ihre Produkte und Preise als digitale Speisekarte für den Fernseher im Laden. Neue Preise und „Ausverkauft“ erscheinen innerhalb einer Minute.',
      features: ['Quer- und Hochformat, Full HD bis 4K', 'Blättert automatisch, wenn nicht alles auf eine Seite passt', 'Öffnungsstatus, Uhrzeit und QR-Code zum Vorbestellen', 'Bleibt eingeschaltet und lädt sich zweimal täglich neu'],
      optionsTitle: 'Optionen in der Adresse',
      options: [
        ['?lang=en', 'Englisch statt Deutsch'],
        ['?alternate=1', 'Abwechselnd Deutsch und Englisch'],
        ['?categories=pastries,cakes', 'Nur diese Kategorien – z. B. ein Bildschirm pro Theke'],
        ['?seconds=15', 'Sekunden pro Seite (mindestens 5)']
      ],
      setupTitle: 'Einen Bildschirm einrichten',
      setup: [
        ['Smart-TV oder Fire TV', 'Browser öffnen, Adresse eingeben, Vollbild. „Fully Kiosk Browser“ (Android) startet die Seite nach einem Stromausfall von selbst.'],
        ['Mini-PC oder Raspberry Pi', 'Chromium beim Start im Kiosk-Modus öffnen (Anleitung in docs/menu-board.md).'],
        ['Windows-PC', 'Eine Chrome-Verknüpfung mit --kiosk und der Adresse in den Autostart legen.']
      ],
      tip: 'Bildschirmschoner und Ausschalt-Timer des Fernsehers ausschalten und den Bildmodus „Standard“ oder „Natürlich“ wählen.'
    },

    emails: {
      intro: 'Der Shop verschickt E-Mails automatisch, sobald ein E-Mail-Server eingerichtet ist (Kapitel 14).',
      list: [
        ['Bestellbestätigung', 'An den Kunden, in der Sprache, in der er bestellt hat.'],
        ['Neue Bestellung', 'An Ihre Shop-Adresse, mit Link in die Verwaltung.'],
        ['Stornierung', 'An den Kunden, wenn eine Bestellung storniert wird.'],
        ['Kontaktformular', 'Jede Nachricht an Ihre Shop-Adresse.'],
        ['Passwort vergessen', 'Ein Link zum Zurücksetzen an den Kunden.']
      ],
      customer: 'Bestätigung an den Kunden',
      shop: 'Hinweis an Sie'
    },

    settings: {
      intro: 'Diese Einstellungen stehen in der Datei .env.production auf dem Server. Nach einer Änderung startet „docker compose up -d“ den Shop neu – am einfachsten erledigt das Ihr Webentwickler.',
      head: ['Einstellung', 'Bedeutung', 'Beispiel'],
      rows: [
        ['SHOP_OPENING_HOURS', 'Öffnungszeiten (Tage ohne Eintrag sind geschlossen)', 'mon-fri 07:00-18:00; sat 07:00-14:00'],
        ['SHOP_DELIVERY_FEE', 'Liefergebühr in Euro', '3.50'],
        ['SHOP_PICKUP_LEAD_MINUTES', 'Vorlaufzeit Abholung in Minuten', '60'],
        ['SHOP_DELIVERY_LEAD_MINUTES', 'Vorlaufzeit Lieferung in Minuten', '120'],
        ['SHOP_SLOT_MINUTES', 'Länge eines Zeitfensters in Minuten', '30'],
        ['SHOP_SLOT_DAYS', 'So viele Tage im Voraus buchbar', '7'],
        ['SHOP_SLOT_CAPACITY', 'Bestellungen pro Zeitfenster (0 = unbegrenzt)', '0'],
        ['SHOP_NOTIFICATION_EMAIL', 'Empfänger für neue Bestellungen und Nachrichten', 'bestellung@…'],
        ['EMAIL_HOST …', 'E-Mail-Server für den Versand', 'smtp.…'],
        ['SHOP_NAME / STREET / CITY', 'Name und Adresse in E-Mails und Suchmaschinen', 'Backlover']
      ],
      stripeTitle: 'Online-Zahlung mit Stripe',
      stripe: [
        'Ein Stripe-Konto anlegen und die Zahlarten einschalten: Karte, Apple Pay, Google Pay, PayPal, Klarna …',
        'Den geheimen Schlüssel als STRIPE_SECRET_KEY eintragen.',
        'Einen Webhook auf /api/orders/payments/stripe/webhook/ anlegen und seinen Schlüssel als STRIPE_WEBHOOK_SECRET eintragen.',
        'Neu starten – an der Kasse erscheint „Online bezahlen“.'
      ],
      stripeNote: 'Erst im Testmodus mit der Testkarte 4242 4242 4242 4242 ausprobieren. Auszahlungen und Erstattungen sehen Sie im Stripe-Dashboard.'
    },

    security: {
      items: [
        ['Starke Passwörter', 'Mindestens 12 Zeichen und für jede Person ein eigenes Konto. „Passwort vergessen?“ setzt ein Passwort jederzeit zurück.'],
        ['Abmelden', 'Auf gemeinsam genutzten Geräten nach der Arbeit unten in der Seitenleiste abmelden.'],
        ['Datensicherung', 'Datenbank und hochgeladene Fotos regelmäßig sichern – am besten täglich und automatisch.'],
        ['Updates', 'Neue Versionen spielt Ihr Webentwickler mit einem Befehl ein; die Datenbank wird dabei automatisch angepasst.'],
        ['Rechtstexte', 'Impressum, Datenschutzerklärung, AGB und Cookie-Richtlinie vor dem Start prüfen und bei Änderungen, etwa einer neuen Adresse, aktualisieren.'],
        ['Anfragen zum Datenschutz', 'Auskunfts- und Löschwünsche zeitnah beantworten. Bestelldaten müssen aus steuerlichen Gründen meist aufbewahrt werden – klären Sie Löschungen mit Ihrem Webentwickler.']
      ]
    },

    help: {
      problemsTitle: 'Wenn etwas nicht klappt',
      problems: [
        ['Ein Produkt erscheint nicht im Shop', 'Status „Aktiv“? „Bestellbar“ angehakt? Kategorie eingeblendet?'],
        ['Es kommen keine E-Mails an', 'Spam-Ordner prüfen; E-Mail-Server und SHOP_NOTIFICATION_EMAIL prüfen lassen.'],
        ['Kein Ton bei neuen Bestellungen', 'Einmal in die Seite klicken, Ton am Gerät einschalten, Tab im Vordergrund lassen.'],
        ['„Online bezahlen“ fehlt an der Kasse', 'Die Stripe-Schlüssel fehlen oder sind falsch eingetragen.'],
        ['Der Menü-Bildschirm zeigt nichts Neues', 'Internetverbindung prüfen. Die Seite aktualisiert sich jede Minute; notfalls neu laden.'],
        ['Ein Kunde hat sein Passwort vergessen', '„Passwort vergessen?“ auf der Anmeldeseite – er erhält einen Link per E-Mail.'],
        ['Alle Zeitfenster sind belegt', 'SHOP_SLOT_CAPACITY erhöhen oder auf 0 setzen; Öffnungszeiten prüfen.']
      ],
      checklistTitle: 'Vor dem Start',
      checklist: [
        'Impressum und Rechtstexte vollständig',
        'Öffnungszeiten, Liefergebühr und Adresse eingetragen',
        'Alle Produkte mit Foto, Preis, Bestand, Zutaten und Allergenen',
        'Testbestellung mit jeder Zahlart – die E-Mails kommen an',
        'Menü-Bildschirm im Laden eingerichtet',
        'Tablet an der Theke mit geöffneter Verwaltung',
        'Automatische Datensicherung eingerichtet'
      ],
      weeklyTitle: 'Jede Woche',
      weekly: ['Bestände und Preise prüfen', 'Kontaktnachrichten beantwortet?', 'Neue Produkte oder Saisonware anlegen', 'Journal-Beitrag oder Instagram-Post']
    },

    back: {
      title: 'Viel Erfolg mit Ihrem Online-Shop!',
      contactTitle: 'Ihr Ansprechpartner',
      contactLines: ['Name', 'Telefon', 'E-Mail']
    }
  },

  ar: {
    title: 'دليل إدارة متجرك الإلكتروني',
    subtitle: 'الطلبات والمنتجات وشاشة القائمة والإعدادات – كل ما تحتاجه للعمل اليومي.',
    eyebrow: 'Backlover Studio · لوحة الإدارة',
    edition: 'إصدار {date}',
    runTitle: 'دليل الإدارة',
    contents: 'المحتويات',
    screenshotNote: 'تعرض الصور لوحة الإدارة بالإنجليزية مع بيانات على سبيل المثال.',
    sections: {
      overview: 'النظام في لمحة',
      dashboard: 'تسجيل الدخول والصفحة الرئيسية',
      orders: 'معالجة الطلبات',
      alerts: 'لا تفوّت أي طلب جديد',
      routine: 'يوم العمل',
      products: 'إدارة المنتجات',
      productForm: 'إضافة منتج',
      productDetail: 'المخزون والمكونات ومسببات الحساسية',
      categories: 'الفئات',
      users: 'العملاء والفريق',
      content: 'المدونة والرسائل والنشرة البريدية',
      menuBoard: 'شاشة القائمة في المتجر',
      emails: 'الرسائل الإلكترونية التلقائية',
      settings: 'الإعدادات والدفع الإلكتروني',
      security: 'الأمان والصيانة',
      help: 'المساعدة وقوائم التحقق'
    },

    welcomeTitle: 'مرحبًا بك في لوحة الإدارة',
    welcome: [
      'يشرح هذا الدليل كل ما تحتاجه لتشغيل متجرك الإلكتروني يومًا بيوم: استقبال الطلبات ومعالجتها، وتحديث المنتجات والأسعار، وإعداد شاشة القائمة في المتجر، وأهم الإعدادات.',
      'لا تحتاج إلى أي خبرة تقنية. تنجز كل المهام اليومية من المتصفح على الحاسوب أو الجهاز اللوحي أو الهاتف. أما بعض الإعدادات القليلة (الفصل ١٤) فتُضبط مرة واحدة على الخادم، ويفضَّل أن يكون ذلك مع مطوّر موقعك.'
    ],

    overview: {
      intro: 'يتكوّن متجرك من أجزاء قليلة تعمل معًا. كل ما تغيّره في لوحة الإدارة يظهر فورًا في المتجر وعلى شاشة القائمة.',
      parts: [
        ['المتجر الإلكتروني', '/', 'هنا يتصفح عملاؤك ويطلبون، بالألمانية والإنجليزية.'],
        ['لوحة الإدارة', '/admin', 'الطلبات والمنتجات والفئات والمستخدمون. هنا تعمل كل يوم.'],
        ['إدارة Django', '/django-admin/', 'مقالات المدونة ورسائل التواصل والنشرة البريدية والمكونات ومسببات الحساسية والقيم الغذائية.'],
        ['شاشة القائمة', '/menu-board', 'تشكيلتك الحالية مع الأسعار لشاشة التلفاز في المتجر.'],
        ['البريد الإلكتروني', '', 'تأكيدات لعملائك ورسالة إليك مع كل طلب جديد.'],
        ['الدفع الإلكتروني', 'Stripe', 'البطاقة وApple Pay وGoogle Pay وغيرها، بمجرد ربط Stripe.']
      ],
      accessTitle: 'بيانات الدخول',
      accessLines: ['عنوان المتجر', 'البريد الإلكتروني لحساب المدير', 'عنوان إدارة Django'],
      accessNote: 'لا تكتب كلمات المرور هنا أبدًا. تسجّل الدخول من صفحة الدخول العادية في المتجر، وبصفتك مديرًا تنتقل مباشرة إلى لوحة الإدارة.',
      language: 'في أسفل الشريط الجانبي تغيّر لغة لوحة الإدارة عبر **English** / **Deutsch**. ويفتح **View shop** متجرك، و**Menu board** القائمة الرقمية.'
    },

    dashboard: {
      intro: 'بعد تسجيل الدخول تظهر صفحة **Dashboard**، وتعرض لك بنظرة واحدة ما يجري اليوم.',
      points: [
        ['الترحيب', 'طلبات اليوم وإيراداته. يفتح زر **Open orders** قائمة الطلبات مباشرة.'],
        ['الأرقام الرئيسية', 'الإيرادات من الطلبات المكتملة، وجميع الطلبات والمفتوحة منها، والمنتجات قليلة المخزون، والعملاء الجدد.'],
        ['أحدث الطلبات', 'آخر الطلبات مع المبلغ وطريقة الاستلام أو التوصيل والحالة.'],
        ['Running low', 'المنتجات التي بقي منها ١٠ قطع أو أقل. يفتح زر **Restock** المنتج لتعديل المخزون.'],
        ['الجرس', 'في أعلى اليمين تفعّل إشعارات سطح المكتب للطلبات الجديدة (الفصل ٠٤).']
      ]
    },

    orders: {
      intro: 'في **Orders** تجد جميع الطلبات، الأحدث أولًا. يعرض كل سطر رقم الطلب والعميل ووقت الطلب وطريقة الاستلام أو التوصيل مع الموعد المطلوب والحالة والمبلغ.',
      filters: 'ابحث برقم الطلب أو الاسم أو البريد الإلكتروني، وصفِّ النتائج حسب الحالة وطريقة الاستلام والفترة الزمنية.',
      flowTitle: 'مسار الطلب',
      flow: [
        ['Pending', 'طلب جديد'],
        ['Processing', 'قيد التحضير'],
        ['Completed', 'تم الاستلام أو التوصيل'],
        ['Canceled', 'ألغيته أنت أو العميل']
      ],
      detailTitle: 'معالجة طلب',
      detailIntro: 'يفتح النقر على **Details** الطلب بكل بياناته: العميل، والاستلام أو عنوان التوصيل، والموعد المطلوب، وطريقة الدفع، وملاحظات العميل، وجميع المنتجات.',
      actions: [
        ['Start preparing', 'تصبح الحالة «Processing»، فيعرف الفريق كله أن أحدًا يتولى الطلب.'],
        ['Mark as handed over', 'عند استلام الطلب أو توصيله. يُعدّ الدفع النقدي أو بالبطاقة مدفوعًا، وتظهر الإيرادات في الصفحة الرئيسية.'],
        ['Cancel order', 'يُعاد المخزون وتصل العميلَ رسالة إلكترونية. وتُسترد المبالغ المدفوعة إلكترونيًا تلقائيًا عبر Stripe.'],
        ['Tracking or driver note', 'للتوصيل: أدخل رقم الشحنة أو ملاحظة للسائق.']
      ],
      note: 'ينتقل الطلب دائمًا من «Pending» إلى «Processing» ثم «Completed». ولا يمكن تعديل الطلبات المكتملة أو الملغاة.'
    },

    alerts: {
      intro: 'ما دامت لوحة الإدارة مفتوحة في علامة تبويب ظاهرة، فإنها تتحقق كل ٣٠ ثانية من وصول طلبات جديدة، وتنبّهك بعدة طرق.',
      channels: [
        ['تنبيه', 'تظهر أسفل النافذة عبارة «New order …».'],
        ['صوت', 'نغمة قصيرة. انقر مرة داخل الصفحة بعد فتحها كي يسمح المتصفح بالأصوات.'],
        ['عدّاد', 'يظهر عدد الطلبات الجديدة في عنوان علامة التبويب وبجانب «Orders».'],
        ['إشعار', 'بعد تفعيله من الجرس في الأعلى، ينبّهك الحاسوب أو الجهاز اللوحي أيضًا بكل طلب جديد.'],
        ['بريد إلكتروني', 'يُرسل كل طلب أيضًا إلى بريد المتجر، حتى لو كانت لوحة الإدارة مغلقة.']
      ],
      tipTitle: 'نصيحتنا للمنضدة',
      tip: 'جهاز لوحي ولوحة الإدارة مفتوحة عليه، مع إيقاف القفل التلقائي للشاشة وتشغيل الصوت. تعمل لوحة الإدارة أيضًا على الهاتف، وتفتح القائمة من زر القائمة في الأعلى.',
      phoneLabels: ['Dashboard', 'Orders']
    },

    routine: {
      intro: 'هكذا يبدو يوم عمل نموذجي مع المتجر الإلكتروني.',
      day: [
        ['صباحًا', 'افتح الصفحة الرئيسية، وجهّز طلبات اليوم حسب موعد الاستلام، وعدّل المخزون حسب كمية الخَبز.'],
        ['خلال اليوم', 'استقبل الطلبات الجديدة (**Start preparing**)، وعند التسليم اختر **Mark as handed over**. واجعل مخزون ما نفد صفرًا.'],
        ['مساءً', 'راجع طلبات الغد، وأدخل مخزون اليوم التالي، وأجب عن رسائل التواصل.'],
        ['كل أسبوع', 'أضف منتجات جديدة أو موسمية، واكتب مقالًا في المدونة، وراجع الإيرادات في الصفحة الرئيسية.']
      ],
      rulesTitle: 'كيف تعمل مواعيد الاستلام والتوصيل',
      rules: [
        ['الفترات الزمنية', 'يختار العملاء اليوم والساعة بفواصل {slot} دقيقة، حتى {days} أيام مقدمًا، وضمن ساعات عملك فقط.'],
        ['مدة التحضير', 'أقرب موعد للاستلام بعد {pickup} دقيقة، وللتوصيل بعد {delivery} دقيقة من الطلب.'],
        ['السعة', 'يمكن تحديد عدد أقصى من الطلبات لكل فترة، فتظهر الفترات الممتلئة محجوزة.'],
        ['المخزون', 'يُخصم المخزون فور الطلب ويعود عند الإلغاء. وعندما يصل إلى صفر يظهر المنتج «نفد من المخزون».'],
        ['الدفع الإلكتروني', 'إذا لم يُكمل العميل الدفع الإلكتروني خلال ٣٠ دقيقة، يلغي المتجر الطلب تلقائيًا.']
      ]
    },

    products: {
      intro: 'في **Products** ترى تشكيلتك كاملة، بما فيها المسودات والمنتجات المتوقفة التي لا تظهر في المتجر.',
      points: [
        ['الأرقام الرئيسية', 'عدد المنتجات الكلي والنشطة وقليلة المخزون، وقيمة المخزون.'],
        ['التصفية والبحث', 'صفِّ حسب الفئة والحالة ونطاق السعر وحالة المخزون، وابحث في القائمة من حقل البحث.'],
        ['الإجراءات', 'العين: تفاصيل المنتج. القلم: التعديل. سلة المهملات: الحذف، وإذا ورد المنتج في طلبات سابقة يُعلَّم «Discontinued» بدلًا من حذفه.']
      ],
      visibleTitle: 'متى يظهر المنتج في المتجر؟',
      visible: ['الحالة «Active»', 'خيار «Available to order» مفعّل', 'الفئة ظاهرة'],
      visibleNote: 'إذا كان المخزون صفرًا يبقى ظاهرًا لكن بعلامة «نفد من المخزون».'
    },

    productForm: {
      intro: 'يفتح زر **Add product** أو القلم نموذج المنتج. وبعد **Create product** أو **Save changes** يظهر في المتجر فورًا.',
      fields: [
        ['الاسم والوصف', 'بالألمانية، اللغة الأساسية للمتجر. يظهر الوصف في صفحة المنتج وعلى شاشة القائمة.'],
        ['الإنجليزية (اختياري)', 'إذا تُرك فارغًا، يعرض المتجر النص الألماني في النسخة الإنجليزية أيضًا.'],
        ['الفئة والحالة', '«Draft» للمنتجات قيد التحضير، و«Active» للبيع، و«Discontinued» للمنتجات التي لم تعد متوفرة.'],
        ['السعر', 'باليورو شاملًا ضريبة القيمة المضافة، مع نقطة عشرية: 2.40'],
        ['المخزون', 'عدد القطع المتاحة للبيع، وينقص تلقائيًا مع كل طلب.'],
        ['الصورة', 'JPG أو PNG أو WebP حتى ٥ ميغابايت. والأجمل صورة PNG بخلفية شفافة.'],
        ['نموذج ثلاثي الأبعاد (اختياري)', 'ملف ‎.glb‎ حتى ٢٠ ميغابايت للعرض الدائري و«شاهده على طاولتك». وبدونه ينشئ المتجر عرضًا ثلاثي الأبعاد من الصورة.'],
        ['الخصائص', 'متاح للطلب، موسمي، نباتي، نباتي مع ألبان، خالٍ من الغلوتين – تظهر كعلامات في المتجر وكخيارات تصفية وعلى شاشة القائمة.']
      ],
      photoTitle: 'نصائح لصور منتجات جميلة',
      photo: ['ضوء النهار، دون فلاش', 'خلفية فاتحة وهادئة، أو إزالة الخلفية', 'صورة مربعة، ١٢٠٠ × ١٢٠٠ بكسل على الأقل', 'الأسلوب والزاوية نفسهما لكل المنتجات']
    },

    productDetail: {
      intro: 'تفتح العين في قائمة المنتجات صفحة التفاصيل: الصورة والبيانات الأساسية والقيم الغذائية لكل ١٠٠ غرام والمكونات ومسببات الحساسية.',
      stockTitle: 'تعديل المخزون بسرعة',
      stock: 'في **Stock management** أدخل العدد الجديد ثم انقر **Update** – مثلًا صباحًا بعد الخَبز. القيمة المُدخلة تحل محل المخزون السابق.',
      allergenTitle: 'المكونات ومسببات الحساسية والقيم الغذائية',
      allergenIntro: 'تدير هذه البيانات في إدارة Django ضمن قسم **Products**:',
      allergenSteps: [
        '**Allergen information**: أضف مسببات الحساسية مرة واحدة، مثل الغلوتين والحليب والبيض والمكسرات.',
        '**Ingredients**: أضف المكونات واربط بكل منها مسببات الحساسية المناسبة.',
        '**Nutrition information**: أضف القيم الغذائية لكل ١٠٠ غرام.',
        '**Products**: اختر في المنتج مكوناته واربط قيمه الغذائية.'
      ],
      allergenNote: 'ذكر مسببات الحساسية إلزامي في البيع عبر الإنترنت أيضًا. راجعها مع كل تغيير في الوصفة.'
    },

    categories: {
      intro: 'تنظّم الفئات متجرك، مثل الخبز والمعجنات والكعك والبسكويت، ولكل فئة صفحتها الخاصة في المتجر.',
      points: [
        ['Add category', 'الاسم والوصف بالألمانية، والإنجليزية اختياريًا.'],
        ['Position', 'الأرقام الأصغر تظهر أولًا، في المتجر وعلى شاشة القائمة.'],
        ['Hide و Show', 'تختفي الفئات المخفية ومنتجاتها من المتجر لكنها تبقى محفوظة، وهذا مفيد للمنتجات الموسمية.'],
        ['Shop link', 'عنوان صفحة الفئة، مثلًا لإنستغرام. وجزؤه الأخير (مثل «pastries») يُستخدم أيضًا لتصفية شاشة القائمة.']
      ]
    },

    users: {
      intro: 'في **Users** ترى جميع الحسابات، عملاءك وفريقك، مع تاريخ التسجيل وعدد الطلبات.',
      points: [
        ['Deactivate', 'لا يستطيع الحساب تسجيل الدخول، وتبقى طلباته محفوظة. ويمكن التراجع في أي وقت عبر **Reactivate**.'],
        ['Make admin', 'يمنح صلاحية كاملة على لوحة الإدارة، لفريقك فقط.'],
        ['Remove admin', 'عندما يغادر أحد أعضاء الفريق.']
      ],
      teamTitle: 'فريقك',
      team: [
        'لكل شخص حسابه الخاص، دون كلمات مرور مشتركة.',
        'يسجّل الموظفون في المتجر بشكل عادي، ثم تمنحهم صلاحية المدير من هنا.',
        'لا يمكنك تعديل حسابك من هنا، كي لا تُغلق الباب على نفسك بالخطأ.',
        'تُستخدم إدارة Django بالحساب الرئيسي الذي أُنشئ عند الإعداد، ويحتاج الآخرون فيها إلى صلاحيات خاصة (قسم **Users**).'
      ]
    },

    content: {
      intro: 'تدير هذه الأقسام في إدارة Django. سجّل الدخول هناك بالبريد الإلكتروني وكلمة المرور لحسابك الرئيسي.',
      postsTitle: 'كتابة مقال في المدونة',
      posts: [
        'افتح **Content → Posts → Add post**.',
        'العنوان، وملخص قصير (**Excerpt**)، والنص (**Body**). افصل بين الفقرات بسطر فارغ.',
        'صورة غلاف اختيارية (**Cover image**).',
        '**Published at**: موعد النشر. فارغ = مسودة، وتاريخ في المستقبل ينشر المقال تلقائيًا في حينه.'
      ],
      messagesTitle: 'رسائل التواصل',
      messages: 'تجد رسائل نموذج التواصل في **Contact messages**، وتصلك أيضًا عبر البريد الإلكتروني. أجب عنها بالبريد، ثم فعّل **Handled**.',
      newsletterTitle: 'النشرة البريدية',
      newsletter: 'في **Newsletter subscribers** تجد كل الاشتراكات من المتجر. للإرسال استخدم خدمة نشرات بريدية. ولا تراسل إلا العناوين التي لا تاريخ لها في **Unsubscribed at**، فالبقية ألغوا اشتراكهم.'
    },

    menuBoard: {
      intro: 'يعرض المتجر في **/menu-board** منتجاتك وأسعارك كقائمة رقمية لشاشة التلفاز في المتجر. وتظهر الأسعار الجديدة وعلامة «نفد» خلال دقيقة.',
      features: ['أفقي وعمودي، من Full HD حتى 4K', 'يقلب الصفحات تلقائيًا إذا لم يتسع كل شيء لصفحة واحدة', 'حالة الدوام والساعة ورمز QR للطلب المسبق', 'تبقى الشاشة مضاءة وتُحدَّث الصفحة مرتين يوميًا'],
      optionsTitle: 'خيارات في العنوان',
      options: [
        ['?lang=en', 'الإنجليزية بدل الألمانية'],
        ['?alternate=1', 'الألمانية والإنجليزية بالتناوب'],
        ['?categories=pastries,cakes', 'هذه الفئات فقط، مثلًا شاشة لكل منضدة'],
        ['?seconds=15', 'عدد الثواني لكل صفحة (٥ على الأقل)']
      ],
      setupTitle: 'إعداد الشاشة',
      setup: [
        ['تلفاز ذكي أو Fire TV', 'افتح المتصفح وأدخل العنوان وفعّل ملء الشاشة. ويشغّل «Fully Kiosk Browser» (أندرويد) الصفحة تلقائيًا بعد انقطاع الكهرباء.'],
        ['حاسوب صغير أو Raspberry Pi', 'شغّل Chromium عند الإقلاع في وضع الكشك (الشرح في docs/menu-board.md).'],
        ['حاسوب Windows', 'ضع اختصار Chrome مع ‎--kiosk‎ والعنوان في مجلد بدء التشغيل.']
      ],
      tip: 'أوقف شاشة التوقف ومؤقت الإطفاء في التلفاز، واختر وضع الصورة «قياسي» أو «طبيعي».'
    },

    emails: {
      intro: 'يرسل المتجر الرسائل تلقائيًا بمجرد إعداد خادم البريد الإلكتروني (الفصل ١٤).',
      list: [
        ['تأكيد الطلب', 'إلى العميل، باللغة التي طلب بها.'],
        ['طلب جديد', 'إلى بريد المتجر، مع رابط إلى لوحة الإدارة.'],
        ['إلغاء الطلب', 'إلى العميل عند إلغاء الطلب.'],
        ['نموذج التواصل', 'كل رسالة إلى بريد المتجر.'],
        ['نسيت كلمة المرور', 'رابط إعادة التعيين إلى العميل.']
      ],
      customer: 'تأكيد إلى العميل',
      shop: 'تنبيه إليك'
    },

    settings: {
      intro: 'توجد هذه الإعدادات في ملف ‎.env.production‎ على الخادم. وبعد أي تغيير يعيد الأمر «docker compose up -d» تشغيل المتجر، والأسهل أن يتولى ذلك مطوّر موقعك.',
      head: ['الإعداد', 'المعنى', 'مثال'],
      rows: [
        ['SHOP_OPENING_HOURS', 'ساعات العمل (الأيام غير المذكورة مغلقة)', 'mon-fri 07:00-18:00; sat 07:00-14:00'],
        ['SHOP_DELIVERY_FEE', 'رسوم التوصيل باليورو', '3.50'],
        ['SHOP_PICKUP_LEAD_MINUTES', 'مدة التحضير للاستلام بالدقائق', '60'],
        ['SHOP_DELIVERY_LEAD_MINUTES', 'مدة التحضير للتوصيل بالدقائق', '120'],
        ['SHOP_SLOT_MINUTES', 'طول الفترة الزمنية بالدقائق', '30'],
        ['SHOP_SLOT_DAYS', 'عدد الأيام المتاحة للحجز مقدمًا', '7'],
        ['SHOP_SLOT_CAPACITY', 'عدد الطلبات لكل فترة (0 = بلا حد)', '0'],
        ['SHOP_NOTIFICATION_EMAIL', 'مستلم الطلبات الجديدة والرسائل', 'bestellung@…'],
        ['EMAIL_HOST …', 'خادم البريد للإرسال', 'smtp.…'],
        ['SHOP_NAME / STREET / CITY', 'الاسم والعنوان في الرسائل ومحركات البحث', 'Backlover']
      ],
      stripeTitle: 'الدفع الإلكتروني عبر Stripe',
      stripe: [
        'أنشئ حسابًا في Stripe وفعّل طرق الدفع: البطاقة وApple Pay وGoogle Pay وPayPal وKlarna …',
        'أدخل المفتاح السري في STRIPE_SECRET_KEY.',
        'أنشئ Webhook على ‎/api/orders/payments/stripe/webhook/‎ وأدخل مفتاحه في STRIPE_WEBHOOK_SECRET.',
        'أعد التشغيل، فيظهر خيار الدفع الإلكتروني في صفحة الدفع.'
      ],
      stripeNote: 'جرّب أولًا في وضع الاختبار ببطاقة الاختبار 4242 4242 4242 4242. وتجد المدفوعات والمبالغ المستردة في لوحة Stripe.'
    },

    security: {
      items: [
        ['كلمات مرور قوية', '١٢ حرفًا على الأقل، وحساب خاص لكل شخص. ويعيد «نسيت كلمة المرور؟» تعيينها في أي وقت.'],
        ['تسجيل الخروج', 'على الأجهزة المشتركة سجّل الخروج بعد العمل من أسفل الشريط الجانبي.'],
        ['النسخ الاحتياطي', 'انسخ قاعدة البيانات والصور المرفوعة بانتظام، والأفضل يوميًا وتلقائيًا.'],
        ['التحديثات', 'يثبّت مطوّر موقعك الإصدارات الجديدة بأمر واحد، وتُحدَّث قاعدة البيانات تلقائيًا.'],
        ['النصوص القانونية', 'راجع بيانات الناشر وسياسة الخصوصية والشروط العامة وسياسة ملفات تعريف الارتباط قبل الإطلاق، وحدّثها عند أي تغيير كعنوان جديد.'],
        ['طلبات حماية البيانات', 'أجب عن طلبات الاطلاع والحذف في وقت قريب. وغالبًا يجب الاحتفاظ ببيانات الطلبات لأسباب ضريبية، فنسّق الحذف مع مطوّر موقعك.']
      ]
    },

    help: {
      problemsTitle: 'عندما لا يعمل شيء ما',
      problems: [
        ['منتج لا يظهر في المتجر', 'هل الحالة «Active»؟ هل «Available to order» مفعّل؟ هل الفئة ظاهرة؟'],
        ['لا تصل الرسائل الإلكترونية', 'افحص مجلد الرسائل المزعجة، واطلب فحص خادم البريد وSHOP_NOTIFICATION_EMAIL.'],
        ['لا صوت عند الطلبات الجديدة', 'انقر مرة داخل الصفحة، وشغّل صوت الجهاز، وأبقِ علامة التبويب في المقدمة.'],
        ['الدفع الإلكتروني غير ظاهر', 'مفاتيح Stripe غير موجودة أو غير صحيحة.'],
        ['شاشة القائمة لا تتحدث', 'افحص الاتصال بالإنترنت. تتحدث الصفحة كل دقيقة، وأعد تحميلها عند الحاجة.'],
        ['عميل نسي كلمة المرور', '«نسيت كلمة المرور؟» في صفحة الدخول، فيصله رابط بالبريد.'],
        ['كل الفترات محجوزة', 'ارفع SHOP_SLOT_CAPACITY أو اجعله 0، وراجع ساعات العمل.']
      ],
      checklistTitle: 'قبل الإطلاق',
      checklist: [
        'بيانات الناشر والنصوص القانونية مكتملة',
        'ساعات العمل ورسوم التوصيل والعنوان مُدخلة',
        'كل المنتجات بصورة وسعر ومخزون ومكونات ومسببات حساسية',
        'طلب تجريبي بكل طرق الدفع، والرسائل تصل',
        'شاشة القائمة في المتجر جاهزة',
        'جهاز لوحي عند المنضدة ولوحة الإدارة مفتوحة',
        'نسخ احتياطي تلقائي مُعدّ'
      ],
      weeklyTitle: 'كل أسبوع',
      weekly: ['مراجعة المخزون والأسعار', 'هل أُجيب عن كل الرسائل؟', 'إضافة منتجات جديدة أو موسمية', 'مقال في المدونة أو منشور على إنستغرام']
    },

    back: {
      title: 'نتمنى لك النجاح مع متجرك الإلكتروني!',
      contactTitle: 'جهة الاتصال',
      contactLines: ['الاسم', 'الهاتف', 'البريد الإلكتروني']
    }
  }
}
