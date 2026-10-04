// Texts for the owner handbook (marketing/docs/handbook.mjs): how to run the
// shop day to day in the Backlover Studio. **Text** marks a button or menu
// name; each edition shows the Studio in its own language, so the names are
// the ones on screen.
export default {
  de: {
    title: 'Handbuch für Ihren Online-Shop',
    subtitle: 'Bestellungen, Produkte, Journal, Newsletter, Einstellungen und Menü-Bildschirme – alles im Backlover Studio.',
    eyebrow: 'Backlover Studio · Verwaltung',
    edition: 'Ausgabe {date}',
    runTitle: 'Handbuch',
    contents: 'Inhalt',
    screenshotNote: 'Abbildungen zeigen das Studio mit Beispieldaten.',
    sections: {
      overview: 'Das System im Überblick',
      dashboard: 'Anmelden & Übersicht',
      orders: 'Bestellungen bearbeiten',
      alerts: 'Neue Bestellungen nicht verpassen',
      routine: 'Der Tagesablauf',
      products: 'Produkte verwalten',
      productForm: 'Ein Produkt anlegen',
      productDetail: 'Bestand, Zutaten & Nährwerte',
      ingredients: 'Zutaten & Allergene',
      categories: 'Kategorien',
      users: 'Kunden & Team',
      journal: 'Das Journal',
      messages: 'Nachrichten beantworten',
      newsletter: 'Newsletter',
      shopSettings: 'Einstellungen des Ladens',
      screens: 'Menü-Bildschirme gestalten',
      screenContent: 'Inhalte & Aktionen',
      tv: 'Den Fernseher einrichten',
      emails: 'Automatische E-Mails',
      server: 'Server & Online-Zahlung',
      security: 'Sicherheit & Pflege',
      help: 'Hilfe & Checklisten'
    },

    welcomeTitle: 'Willkommen im Backlover Studio',
    welcome: [
      'Dieses Handbuch erklärt alles für den täglichen Betrieb: Bestellungen annehmen und bearbeiten, Produkte und Preise pflegen, Journal, Nachrichten und Newsletter, die Einstellungen Ihres Ladens und die Menü-Bildschirme für die Fernseher im Laden.',
      'Alles erledigen Sie im Backlover Studio, der Verwaltung Ihres Shops – im Browser, am Computer, Tablet oder Smartphone. Technische Kenntnisse brauchen Sie nicht. Nur E-Mail-Versand und Online-Zahlung werden einmalig auf dem Server eingerichtet (Kapitel 20).'
    ],

    overview: {
      intro: 'Ihr Shop besteht aus wenigen Bausteinen, die zusammenarbeiten. Alles, was Sie im Studio ändern, ist sofort im Shop und innerhalb einer Minute auf den Fernsehern im Laden.',
      parts: [
        ['Online-Shop', '/', 'Hier stöbern und bestellen Ihre Kundinnen und Kunden – auf Deutsch, Englisch und Arabisch.'],
        ['Backlover Studio', '/admin', 'Bestellungen, Produkte, Inhalte, Einstellungen und Menü-Bildschirme – hier arbeiten Sie jeden Tag.'],
        ['Menü-Bildschirme', '/tv', 'Ihre Speisekarte mit Preisen und Aktionen auf den Fernsehern im Laden.'],
        ['E-Mails', '', 'Bestätigungen für Ihre Kunden, eine Nachricht an Sie bei jeder Bestellung, Antworten und Newsletter.'],
        ['Online-Zahlung', 'Stripe', 'Karte, Apple Pay, Google Pay und mehr – sobald Stripe verbunden ist.'],
        ['Drei Sprachen', 'DE · EN · AR', 'Shop und Studio auf Deutsch, Englisch und Arabisch – Arabisch von rechts nach links.']
      ],
      accessTitle: 'Ihre Zugänge',
      accessLines: ['Adresse des Shops', 'E-Mail Ihres Admin-Kontos', 'Adresse für die Fernseher (…/tv)'],
      accessNote: 'Notieren Sie hier niemals Passwörter. Sie melden sich auf der normalen Anmeldeseite des Shops an – als Admin landen Sie direkt im Studio.',
      language: 'Die Seitenleiste ist in vier Bereiche gegliedert: Verkauf, Sortiment, Inhalte und Laden. Unten wechseln Sie die Sprache des Studios mit **Deutsch**, **English** oder **العربية**; **Zum Shop** öffnet Ihren Shop.'
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
      intro: 'Solange das Studio in einem sichtbaren Browser-Tab geöffnet ist, prüft es alle 30 Sekunden, ob neue Bestellungen eingegangen sind – und meldet sich auf mehreren Wegen.',
      channels: [
        ['Hinweis', 'Unten im Fenster erscheint „Neue Bestellung …“.'],
        ['Signalton', 'Ein kurzer Ton. Klicken Sie nach dem Öffnen einmal in die Seite, damit der Browser Töne erlaubt.'],
        ['Zähler', 'Die Zahl neuer Bestellungen steht im Titel des Browser-Tabs und bei „Bestellungen“.'],
        ['Benachrichtigung', 'Über die Glocke oben rechts eingeschaltet, meldet auch Ihr Computer oder Tablet jede neue Bestellung.'],
        ['E-Mail', 'Zusätzlich geht jede Bestellung an Ihre Adresse für Benachrichtigungen – auch wenn das Studio geschlossen ist.']
      ],
      tipTitle: 'Unser Tipp für die Theke',
      tip: 'Ein Tablet mit geöffnetem Studio, automatische Bildschirmsperre aus, Ton an. Das Studio funktioniert auch auf dem Smartphone – die Seitenleiste öffnen Sie oben über die Menü-Schaltfläche.',
      phoneLabels: ['Übersicht', 'Bestellungen']
    },

    routine: {
      intro: 'So sieht ein typischer Tag mit dem Online-Shop aus.',
      day: [
        ['Morgens', 'Übersicht öffnen, die Bestellungen für heute nach Abholzeit vorbereiten und die Bestände an die Backmenge anpassen.'],
        ['Tagsüber', 'Neue Bestellungen annehmen (**Zubereitung starten**) und bei Übergabe **Als übergeben markieren**. Ausverkauftes auf Bestand 0 setzen.'],
        ['Abends', 'Bestellungen für morgen ansehen, Bestände für den nächsten Tag eintragen, Nachrichten beantworten.'],
        ['Jede Woche', 'Neue und saisonale Produkte anlegen, die Aktionen auf den Bildschirmen prüfen, einen Journal-Beitrag oder Newsletter schreiben.']
      ],
      rulesTitle: 'So funktionieren Abhol- und Lieferzeiten',
      rules: [
        ['Zeitfenster', 'Kunden wählen Tag und Uhrzeit im {slot}-Minuten-Takt, bis zu {days} Tage im Voraus und nur innerhalb Ihrer Öffnungszeiten – nie an Schließtagen.'],
        ['Vorlaufzeit', 'Abholung frühestens {pickup} Minuten, Lieferung frühestens {delivery} Minuten nach der Bestellung.'],
        ['Kapazität', 'Auf Wunsch höchstens eine bestimmte Zahl an Bestellungen pro Zeitfenster; volle Fenster sind dann belegt.'],
        ['Bestand', 'Beim Bestellen wird der Bestand sofort abgezogen, bei einer Stornierung kommt er zurück. Bei 0 ist ein Produkt „Ausverkauft“.'],
        ['Online-Zahlung', 'Bezahlt ein Kunde online nicht innerhalb von 30 Minuten, storniert der Shop die Bestellung automatisch.']
      ],
      rulesNote: 'Alle Werte stellen Sie unter Einstellungen → Abholung & Lieferung ein (Kapitel 15).'
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
      visibleNote: 'Mit Bestand 0 bleibt es sichtbar, wird aber als ausverkauft angezeigt – auch auf den Menü-Bildschirmen.'
    },

    productForm: {
      intro: 'Mit **Produkt hinzufügen** oder dem Stift öffnen Sie das Formular. Mit **Produkt anlegen** bzw. **Änderungen speichern** ist es sofort im Shop.',
      fields: [
        ['Name & Beschreibung', 'Auf Deutsch, der Hauptsprache des Shops. Die Beschreibung steht auf der Produktseite und den Menü-Bildschirmen.'],
        ['Englisch (optional)', 'Erscheint im englischen und im arabischen Shop. Leer gelassen, zeigt der Shop den deutschen Text.'],
        ['Kategorie & Status', '„Entwurf“ für Produkte in Vorbereitung, „Aktiv“ für den Verkauf, „Eingestellt“ für Produkte, die es nicht mehr gibt.'],
        ['Preis', 'In Euro inklusive Mehrwertsteuer, mit Punkt: 2.40'],
        ['Bestand', 'Wie viele Stück verkauft werden können. Sinkt bei jeder Bestellung automatisch.'],
        ['Foto', 'JPG, PNG oder WebP bis 5 MB. Am schönsten ist ein freigestelltes PNG mit transparentem Hintergrund.'],
        ['3D-Modell (optional)', 'Eine .glb-Datei bis 20 MB für die 360°-Ansicht und „Auf deinem Tisch ansehen“. Ohne Modell erzeugt der Shop eine 3D-Ansicht aus dem Foto.'],
        ['Eigenschaften', 'Bestellbar, Saison, Vegan, Vegetarisch, Glutenfrei – als Kennzeichnung im Shop, als Filter und auf den Menü-Bildschirmen.']
      ],
      photoTitle: 'Tipps für gute Produktfotos',
      photo: ['Tageslicht, kein Blitz', 'Heller, ruhiger Hintergrund – oder freistellen', 'Quadratisch, mindestens 1200 × 1200 Pixel', 'Alle Produkte im gleichen Stil und Winkel']
    },

    productDetail: {
      intro: 'Das Auge in der Produktliste öffnet die Detailseite mit Foto, Grunddaten, Bestand, Zutaten und Nährwerten.',
      stockTitle: 'Bestand schnell ändern',
      stock: 'Unter **Bestandsverwaltung** die neue Stückzahl eingeben und **Aktualisieren** klicken – zum Beispiel morgens nach dem Backen. Der eingegebene Wert ersetzt den bisherigen Bestand.',
      recipeTitle: 'Zutaten & Nährwerte',
      recipe: [
        'Unter **Zutaten & Nährwerte** die Zutaten des Produkts anhaken – die Suche hilft bei langen Listen.',
        'Die Allergene ergeben sich aus den Zutaten und stehen direkt darunter.',
        '**Nährwerte angeben** einschalten und die Werte pro 100 g eintragen.',
        '**Zutaten & Nährwerte speichern** – sie erscheinen sofort auf der Produktseite.'
      ],
      allergenNote: 'Allergenangaben sind auch beim Online-Verkauf Pflicht. Prüfen Sie sie bei jeder Rezeptänderung. Neue Zutaten legen Sie unter **Zutaten verwalten** an (Kapitel 09).'
    },

    ingredients: {
      intro: 'Unter **Zutaten & Allergene** legen Sie jede Zutat einmal an und ordnen ihr die Allergene zu. Im Produkt wählen Sie danach nur noch die Zutaten aus – die Allergene folgen automatisch.',
      points: [
        ['Allergene', 'Ein Klick auf **Die 14 EU-Hauptallergene anlegen** legt alle Pflichtallergene nach LMIV an. Weitere tragen Sie im Feld darüber ein.'],
        ['Zutaten', '**Zutat hinzufügen**: Name, optional auf Englisch, und die enthaltenen Allergene anhaken.'],
        ['Verwendung', 'Die Spalte „Produkte“ zeigt, in wie vielen Produkten eine Zutat steckt. Ändern Sie eine Zutat, ändert sich jede dieser Produktseiten mit.'],
        ['Löschen', 'Eine gelöschte Zutat verschwindet aus allen Produkten – prüfen Sie vorher die Spalte „Produkte“.']
      ],
      tipTitle: 'In dieser Reihenfolge',
      tip: ['Allergene anlegen', 'Zutaten mit ihren Allergenen anlegen', 'In jedem Produkt die Zutaten anhaken']
    },

    categories: {
      intro: 'Kategorien gliedern Ihren Shop, zum Beispiel Brot, Gebäck, Kuchen und Kekse. Jede hat eine eigene Seite im Shop und eine Überschrift auf den Menü-Bildschirmen.',
      points: [
        ['Kategorie hinzufügen', 'Name und Beschreibung auf Deutsch, optional auf Englisch.'],
        ['Position', 'Niedrigere Zahlen erscheinen zuerst – im Shop und auf den Menü-Bildschirmen.'],
        ['Ausblenden & Einblenden', 'Ausgeblendete Kategorien und ihre Produkte verschwinden aus dem Shop, bleiben aber gespeichert – praktisch für Saisonware.'],
        ['Shop-Link', 'Die Adresse der Kategorie-Seite, etwa für Instagram.']
      ]
    },

    users: {
      intro: 'Unter **Benutzer** sehen Sie alle Konten – Ihre Kundinnen und Kunden und Ihr Team – mit Registrierungsdatum und Anzahl der Bestellungen.',
      points: [
        ['Deaktivieren', 'Das Konto kann sich nicht mehr anmelden, seine Bestellungen bleiben erhalten. Mit **Reaktivieren** jederzeit rückgängig.'],
        ['Zum Admin machen', 'Gibt vollen Zugriff auf das Studio – nur für Ihr Team.'],
        ['Adminrechte entziehen', 'Wenn jemand Ihr Team verlässt.']
      ],
      teamTitle: 'Ihr Team',
      team: [
        'Jede Person bekommt ein eigenes Konto – keine gemeinsamen Passwörter.',
        'Mitarbeitende registrieren sich ganz normal im Shop; danach machen Sie sie hier zum Admin.',
        'Ihr eigenes Konto können Sie hier nicht ändern – so sperren Sie sich nicht versehentlich aus.',
        'Admins haben dieselben Rechte wie Sie: Geben Sie sie nur Personen, denen Sie vertrauen.'
      ]
    },

    journal: {
      intro: 'Im **Journal** schreiben Sie Beiträge für die Journal-Seite Ihres Shops – Neuigkeiten, Saisonware, Geschichten aus der Backstube.',
      stepsTitle: 'Einen Beitrag schreiben',
      steps: [
        '**Neuer Beitrag** öffnen.',
        'Titel, Kurzfassung und Text auf Deutsch, im Reiter **English** optional auf Englisch. Absätze trennen Sie mit einer Leerzeile.',
        'Ein **Titelbild** hochladen – am besten im Querformat 16:9.',
        '**Vorschau** zeigt den Beitrag so, wie er im Shop erscheint.',
        'Unter **Veröffentlichung** wählen: **Entwurf**, **Veröffentlichen** oder **Planen** mit Datum und Uhrzeit – und speichern.'
      ],
      statesTitle: 'Die Liste',
      states: [
        ['Entwurf', 'Nur im Studio sichtbar.'],
        ['Geplant', 'Erscheint automatisch zum Termin.'],
        ['Veröffentlicht', 'Im Shop sichtbar, der neueste zuerst.'],
        ['EN', 'Der Beitrag hat eine englische Fassung; auch der arabische Shop zeigt sie.']
      ]
    },

    messages: {
      intro: 'Nachrichten aus dem Kontaktformular landen unter **Nachrichten**. Die Zahl in der Seitenleiste zeigt, wie viele noch offen sind. Jede Nachricht kommt zusätzlich per E-Mail.',
      stepsTitle: 'Eine Nachricht beantworten',
      steps: [
        'Die Nachricht links anklicken – rechts steht sie vollständig.',
        'Unter **Antworten** schreiben oder einen Textbaustein wählen: **Danke**, **Vorbestellung** oder **Rückruf**.',
        '**Antwort senden** schickt sie per E-Mail. Antwortet der Kunde, landet das in Ihrem Postfach für Benachrichtigungen.',
        'Die Nachricht gilt damit als erledigt und bleibt mit Ihrer Antwort gespeichert.'
      ],
      more: [
        ['Als erledigt markieren', 'Für Nachrichten, die Sie am Telefon oder im Laden geklärt haben.'],
        ['Im E-Mail-Programm', 'Öffnet eine Antwort in Ihrem eigenen E-Mail-Programm.'],
        ['Offen · Erledigt · Alle', 'Filter über der Liste; die Suche findet Namen, E-Mail-Adressen und Texte.']
      ]
    },

    newsletter: {
      intro: 'Unter **Newsletter** schreiben und versenden Sie Newsletter an alle, die sich im Shop dafür angemeldet haben.',
      stepsTitle: 'Einen Newsletter versenden',
      steps: [
        '**Neuer Newsletter**: Betreff und Text schreiben – daneben sehen Sie, wie die E-Mail aussieht.',
        '**Test an mich** schickt sie zuerst an Ihre eigene Adresse.',
        '**An … senden** verschickt sie an alle aktiven Abonnenten. Versendete Newsletter bleiben in der Liste.',
        'Jede E-Mail enthält einen persönlichen Abmeldelink. Abgemeldete Adressen bekommen nichts mehr.'
      ],
      subsTitle: 'Abonnenten',
      subs: 'Der Reiter **Abonnenten** zeigt alle Anmeldungen, aktive und abgemeldete. **Adresse hinzufügen** nur mit Einwilligung der Person, etwa auf einer Anmeldeliste im Laden. **Als CSV exportieren** für Ihre Unterlagen.',
      law: 'Schreiben Sie nur an Personen, die sich selbst angemeldet oder ausdrücklich zugestimmt haben.'
    },

    shopSettings: {
      intro: 'Unter **Einstellungen** pflegen Sie alles, was Ihren Laden ausmacht. Änderungen gelten sofort – im Shop, an der Kasse, in E-Mails, auf den Menü-Bildschirmen und im Impressum. Speichern mit **Änderungen speichern**.',
      items: [
        ['Öffnungszeiten', 'Jeden Tag an- oder ausschalten, mit Mittagspause oder zweitem Zeitraum. **Montag für Mo–Fr übernehmen** spart Tipparbeit.'],
        ['Schließtage', 'Feiertage, Urlaub, Inventur: An diesen Tagen gibt es keine Abholzeiten, die Kontaktseite zeigt sie an.'],
        ['Abholung & Lieferung', 'Ein- und ausschalten, Liefergebühr, Vorlaufzeiten, Länge der Zeitfenster, Tage im Voraus und Bestellungen pro Zeitfenster.'],
        ['Hinweis im Shop', 'Ein Banner oben auf jeder Seite, z. B. „Am Montag geschlossen“ – auf Deutsch und Englisch.'],
        ['Geschäft & Kontakt', 'Name, Adresse, Telefon, E-Mail, Anfahrt und Social-Media-Links.'],
        ['Impressum', 'Firma oder Inhaber, verantwortliche Person, USt-IdNr. und Handelsregister.'],
        ['Benachrichtigungen', 'Die E-Mail-Adresse für neue Bestellungen und Kontaktnachrichten.']
      ],
      note: 'Leere Felder übernehmen die Grundeinstellungen des Servers. Solange Sie nichts gespeichert haben, steht unten „Es gelten die Grundeinstellungen des Servers“.'
    },

    screens: {
      intro: 'Unter **Menü-Bildschirme** gestalten Sie die Speisekarten für die Fernseher im Laden – für die Theke, das Schaufenster oder die Café-Ecke jeweils eine eigene. Preise, Fotos und „Ausverkauft“ kommen live aus dem Shop.',
      card: 'Jede Karte zeigt eine Vorschau, ob der Fernseher **Online** ist (mit Auflösung) und den 4-stelligen Code. **Gestalten** öffnet den Editor, **Öffnen** die Seite des Bildschirms; dazu kommen Neu laden, Duplizieren und Löschen.',
      designTitle: 'Reiter „Gestaltung“',
      design: [
        ['Aufbau', '**Spalten mit Highlight**, **Foto-Kacheln**, **Klassische Karte** oder **Ein Produkt groß** (Kapitel 17).'],
        ['Farbwelt', 'Fünf Farbwelten oder **Eigene Farben**, dazu ein Hintergrundfoto, das abgedunkelt wird.'],
        ['Schrift', 'Elegant oder Modern.'],
        ['Sprache', 'Deutsch, Englisch, Arabisch – oder zwei im Wechsel.'],
        ['Ausrichtung', 'Automatisch, oder hochkant, wenn der Fernseher gedreht hängt.']
      ],
      live: 'Rechts sehen Sie eine Live-Vorschau jeder Änderung. **Speichern & live schalten** schickt sie an die Fernseher – innerhalb einer Minute.'
    },

    screenContent: {
      contentTitle: 'Reiter „Inhalt“',
      content: 'Überschrift und Laufschrift (auf Deutsch und Englisch, bei arabischen Bildschirmen auch Arabisch), was angezeigt wird – Preise, Beschreibungen, Fotos, Vegan & Co., QR-Code, Uhrzeit, Geöffnet/Geschlossen –, wie Ausverkauftes erscheint, wie lange eine Seite steht und welche Kategorien und Produkte der Bildschirm zeigt.',
      slidesTitle: 'Reiter „Aktionen“',
      slides: [
        '**Aktion hinzufügen** als **Produkt** (mit Foto aus dem Shop), **Foto** (eigenes Bild) oder **Botschaft** (nur Text).',
        'Titel, Text, Preis und ein Zusatz wie „statt 5,40 €“.',
        'Unter **Wann** Zeitraum, Uhrzeit und Wochentage – z. B. Frühstück Mo–Fr von 6 bis 11 Uhr. Leer heißt: immer.',
        'Das Auge zeigt eine Aktion sofort in der Vorschau, die Pfeile ändern die Reihenfolge.'
      ],
      layoutsTitle: 'Die vier Aufbauten',
      layouts: ['Spalten mit Highlight', 'Ein Produkt groß', 'Foto-Kacheln', 'Klassische Karte']
    },

    tv: {
      intro: 'Jeder Bildschirm hat einen 4-stelligen Code. So kommt er auf den Fernseher – einmalig und in zwei Minuten:',
      steps: [
        ['Adresse öffnen', 'Am Fernseher oder Stick den Browser öffnen und {url} aufrufen.'],
        ['Code eingeben', 'Den Code mit der Fernbedienung eingeben und **Bildschirm starten** wählen.'],
        ['Fertig', 'Das Gerät merkt sich den Bildschirm und startet ihn nach jedem Neustart von selbst.']
      ],
      devicesTitle: 'Welches Gerät?',
      devices: [
        ['Fire TV Stick (empfohlen)', 'Günstig und zuverlässig. „Fully Kiosk Browser“ installieren, Startseite …/tv, „Beim Start öffnen“ und „Bildschirm anlassen“ einschalten.'],
        ['Smart-TV', 'Der eingebaute Browser reicht für den Anfang; manche Geräte vergessen die Seite beim Ausschalten.'],
        ['Raspberry Pi', 'Für den Dauerbetrieb: deploy/kiosk/setup-raspberry-pi.sh richtet alles ein.'],
        ['PC oder Mini-PC', 'deploy/kiosk/menu-screen-windows.bat in den Autostart legen.']
      ],
      deviceTitle: 'Reiter „Gerät“',
      device: 'Code, QR-Code und Adresse des Bildschirms, ob er online ist und mit welcher Auflösung. **Bildschirm neu laden** startet die Seite am Fernseher aus der Ferne neu.',
      tipsTitle: 'Am Fernseher',
      tips: [
        'Energiesparmodus, Ausschalt-Timer und Bildschirmschoner ausschalten.',
        'Bildmodus „Standard“ oder „Natürlich“ statt „Dynamisch“.',
        'Mit dem Ein-/Aus-Timer des Fernsehers startet die Speisekarte zur Öffnung von selbst.',
        'Ohne Internet zeigt der Bildschirm die zuletzt geladene Karte weiter.'
      ]
    },

    emails: {
      intro: 'Der Shop verschickt E-Mails automatisch, sobald ein E-Mail-Server eingerichtet ist (Kapitel 20). Kunden bekommen sie in der Sprache, in der sie bestellt haben.',
      list: [
        ['Bestellbestätigung', 'An den Kunden, auf Deutsch, Englisch oder Arabisch.'],
        ['Neue Bestellung', 'An Ihre Adresse für Benachrichtigungen, mit Link ins Studio.'],
        ['Stornierung', 'An den Kunden, wenn eine Bestellung storniert wird.'],
        ['Kontaktformular', 'Jede Nachricht an Ihre Adresse für Benachrichtigungen.'],
        ['Antworten & Newsletter', 'Aus dem Studio, mit Ihrem Shop als Absender.'],
        ['Passwort vergessen', 'Ein Link zum Zurücksetzen an den Kunden.']
      ],
      customer: 'Bestätigung an den Kunden',
      shop: 'Hinweis an Sie'
    },

    server: {
      intro: 'Fast alles stellen Sie im Studio ein. Nur diese Werte stehen in der Datei .env.production auf dem Server – am einfachsten richtet sie Ihr Webentwickler einmalig ein. Danach startet „docker compose up -d“ den Shop neu.',
      head: ['Einstellung', 'Bedeutung', 'Beispiel'],
      rows: [
        ['FRONTEND_URL', 'Adresse Ihres Shops, für Links in E-Mails und QR-Codes', 'https://backlover.de'],
        ['EMAIL_HOST, EMAIL_PORT', 'E-Mail-Server für den Versand', 'smtp.… · 587'],
        ['EMAIL_HOST_USER, …_PASSWORD', 'Zugang zum E-Mail-Server', 'hallo@…'],
        ['DEFAULT_FROM_EMAIL', 'Absender aller E-Mails', 'Backlover <hallo@…>'],
        ['STRIPE_SECRET_KEY', 'Geheimer Schlüssel für die Online-Zahlung', 'sk_live_…'],
        ['STRIPE_WEBHOOK_SECRET', 'Schlüssel des Stripe-Webhooks', 'whsec_…'],
        ['SHOP_…', 'Grundwerte für Öffnungszeiten, Gebühren usw. – gelten, solange im Studio nichts gespeichert ist', 'mon-fri 07:00-18:00']
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
        ['Es kommen keine E-Mails an', 'Spam-Ordner prüfen, die Adresse unter Einstellungen → Benachrichtigungen prüfen und den E-Mail-Server prüfen lassen.'],
        ['Kein Ton bei neuen Bestellungen', 'Einmal in die Seite klicken, Ton am Gerät einschalten, Tab im Vordergrund lassen.'],
        ['„Online bezahlen“ fehlt an der Kasse', 'Die Stripe-Schlüssel fehlen oder sind falsch eingetragen.'],
        ['Der Fernseher zeigt nichts Neues', 'Im Studio prüfen, ob der Bildschirm online ist; **Bildschirm neu laden**; die Internetverbindung des Fernsehers prüfen.'],
        ['Der Fernseher fragt wieder nach dem Code', 'Den Code erneut eingeben – etwa nachdem die Browserdaten gelöscht wurden.'],
        ['Alle Zeitfenster sind belegt', 'Unter Einstellungen → Abholung & Lieferung mehr Bestellungen pro Zeitfenster erlauben (0 = unbegrenzt); Öffnungszeiten und Schließtage prüfen.']
      ],
      checklistTitle: 'Vor dem Start',
      checklist: [
        'Impressum und Rechtstexte vollständig',
        'Öffnungszeiten, Liefergebühr und Adresse eingetragen',
        'Alle Produkte mit Foto, Preis, Bestand, Zutaten und Allergenen',
        'Testbestellung mit jeder Zahlart – die E-Mails kommen an',
        'Menü-Bildschirme gestaltet und am Fernseher gekoppelt',
        'Tablet an der Theke mit geöffnetem Studio',
        'Automatische Datensicherung eingerichtet'
      ],
      weeklyTitle: 'Jede Woche',
      weekly: ['Bestände und Preise prüfen', 'Alle Nachrichten beantwortet?', 'Aktionen auf den Bildschirmen aktuell?', 'Journal-Beitrag oder Newsletter']
    },

    back: {
      title: 'Viel Erfolg mit Ihrem Online-Shop!',
      contactTitle: 'Ihr Ansprechpartner',
      contactLines: ['Name', 'Telefon', 'E-Mail']
    }
  },

  ar: {
    title: 'دليل إدارة متجرك الإلكتروني',
    subtitle: 'الطلبات والمنتجات والمدونة والنشرة البريدية والإعدادات وشاشات القائمة – كل ذلك في Backlover Studio.',
    eyebrow: 'Backlover Studio · لوحة الإدارة',
    edition: 'إصدار {date}',
    runTitle: 'دليل الإدارة',
    contents: 'المحتويات',
    screenshotNote: 'تعرض الصور لوحة الإدارة بالعربية مع بيانات على سبيل المثال.',
    sections: {
      overview: 'النظام في لمحة',
      dashboard: 'تسجيل الدخول ولوحة التحكم',
      orders: 'معالجة الطلبات',
      alerts: 'لا تفوّت أي طلب جديد',
      routine: 'يوم العمل',
      products: 'إدارة المنتجات',
      productForm: 'إضافة منتج',
      productDetail: 'المخزون والمكونات والقيم الغذائية',
      ingredients: 'المكونات ومسببات الحساسية',
      categories: 'الفئات',
      users: 'العملاء والفريق',
      journal: 'المدونة',
      messages: 'الرد على الرسائل',
      newsletter: 'النشرة البريدية',
      shopSettings: 'إعدادات المتجر',
      screens: 'تصميم شاشات القائمة',
      screenContent: 'المحتوى والعروض',
      tv: 'إعداد التلفاز',
      emails: 'الرسائل الإلكترونية التلقائية',
      server: 'الخادم والدفع الإلكتروني',
      security: 'الأمان والصيانة',
      help: 'المساعدة وقوائم التحقق'
    },

    welcomeTitle: 'مرحبًا بك في Backlover Studio',
    welcome: [
      'يشرح هذا الدليل كل ما تحتاجه للعمل اليومي: استقبال الطلبات ومعالجتها، وتحديث المنتجات والأسعار، والمدونة والرسائل والنشرة البريدية، وإعدادات متجرك، وشاشات القائمة لأجهزة التلفاز في المتجر.',
      'تنجز كل ذلك في Backlover Studio، لوحة إدارة متجرك، من المتصفح على الحاسوب أو الجهاز اللوحي أو الهاتف، دون أي خبرة تقنية. أما إرسال البريد الإلكتروني والدفع الإلكتروني فيُضبطان مرة واحدة على الخادم (الفصل 20).'
    ],

    overview: {
      intro: 'يتكوّن متجرك من أجزاء قليلة تعمل معًا. كل ما تغيّره في لوحة الإدارة يظهر فورًا في المتجر، وخلال دقيقة على شاشات التلفاز في المتجر.',
      parts: [
        ['المتجر الإلكتروني', '/', 'هنا يتصفح عملاؤك ويطلبون، بالألمانية والإنجليزية والعربية.'],
        ['Backlover Studio', '/admin', 'الطلبات والمنتجات والمحتوى والإعدادات وشاشات القائمة، هنا تعمل كل يوم.'],
        ['شاشات القائمة', '/tv', 'قائمتك مع الأسعار والعروض على شاشات التلفاز في المتجر.'],
        ['البريد الإلكتروني', '', 'تأكيدات لعملائك، ورسالة إليك مع كل طلب، والردود والنشرات البريدية.'],
        ['الدفع الإلكتروني', 'Stripe', 'البطاقة وApple Pay وGoogle Pay وغيرها، بمجرد ربط Stripe.'],
        ['ثلاث لغات', 'DE · EN · AR', 'المتجر ولوحة الإدارة بالألمانية والإنجليزية والعربية، والعربية من اليمين إلى اليسار.']
      ],
      accessTitle: 'بيانات الدخول',
      accessLines: ['عنوان المتجر', 'البريد الإلكتروني لحساب المدير', 'عنوان أجهزة التلفاز (…/tv)'],
      accessNote: 'لا تكتب كلمات المرور هنا أبدًا. تسجّل الدخول من صفحة الدخول العادية في المتجر، وبصفتك مديرًا تنتقل مباشرة إلى لوحة الإدارة.',
      language: 'ينقسم الشريط الجانبي إلى أربعة أقسام: المبيعات والكتالوج والمحتوى والمتجر. وفي أسفله تغيّر لغة لوحة الإدارة عبر **Deutsch** أو **English** أو **العربية**، ويفتح **عرض المتجر** متجرك.'
    },

    dashboard: {
      intro: 'بعد تسجيل الدخول تظهر **لوحة التحكم**، وتعرض لك بنظرة واحدة ما يجري اليوم.',
      points: [
        ['الترحيب', 'طلبات اليوم وإيراداته. يفتح زر **الطلبات المفتوحة** قائمة الطلبات مباشرة.'],
        ['الأرقام الرئيسية', 'الإيرادات من الطلبات المكتملة، وجميع الطلبات والمفتوحة منها، والمنتجات قليلة المخزون، والعملاء الجدد.'],
        ['أحدث الطلبات', 'آخر الطلبات مع المبلغ وطريقة الاستلام أو التوصيل والحالة.'],
        ['على وشك النفاد', 'المنتجات التي بقي منها 10 قطع أو أقل. يفتح زر **إعادة التعبئة** المنتج لتعديل المخزون.'],
        ['الجرس', 'في أعلى الصفحة تفعّل إشعارات سطح المكتب للطلبات الجديدة (الفصل 04).']
      ]
    },

    orders: {
      intro: 'في **الطلبات** تجد جميع الطلبات، الأحدث أولًا. يعرض كل سطر رقم الطلب والعميل ووقت الطلب وطريقة الاستلام أو التوصيل مع الموعد المطلوب والحالة والمبلغ.',
      filters: 'ابحث برقم الطلب أو الاسم أو البريد الإلكتروني، وصفِّ النتائج حسب الحالة وطريقة الاستلام والفترة الزمنية.',
      flowTitle: 'مسار الطلب',
      flow: [
        ['قيد الانتظار', 'طلب جديد'],
        ['قيد المعالجة', 'قيد التحضير'],
        ['مكتمل', 'تم الاستلام أو التوصيل'],
        ['ملغى', 'ألغيته أنت أو العميل']
      ],
      detailTitle: 'معالجة طلب',
      detailIntro: 'يفتح النقر على **التفاصيل** الطلب بكل بياناته: العميل، والاستلام أو عنوان التوصيل، والموعد المطلوب، وطريقة الدفع، وملاحظات العميل، وجميع المنتجات.',
      actions: [
        ['بدء التحضير', 'تصبح الحالة «قيد المعالجة»، فيعرف الفريق كله أن أحدًا يتولى الطلب.'],
        ['تعيين كـ«تم التسليم»', 'عند استلام الطلب أو توصيله. يُعدّ الدفع النقدي أو بالبطاقة مدفوعًا، وتظهر الإيرادات في لوحة التحكم.'],
        ['إلغاء الطلب', 'يُعاد المخزون وتصل العميلَ رسالة إلكترونية. وتُسترد المبالغ المدفوعة إلكترونيًا تلقائيًا عبر Stripe.'],
        ['رقم التتبع أو ملاحظة للسائق', 'للتوصيل: أدخل رقم الشحنة أو ملاحظة للسائق.']
      ],
      note: 'ينتقل الطلب دائمًا من «قيد الانتظار» إلى «قيد المعالجة» ثم «مكتمل». ولا يمكن تعديل الطلبات المكتملة أو الملغاة.'
    },

    alerts: {
      intro: 'ما دامت لوحة الإدارة مفتوحة في علامة تبويب ظاهرة، فإنها تتحقق كل 30 ثانية من وصول طلبات جديدة، وتنبّهك بعدة طرق.',
      channels: [
        ['تنبيه', 'تظهر أسفل النافذة رسالة «طلب جديد …».'],
        ['صوت', 'نغمة قصيرة. انقر مرة داخل الصفحة بعد فتحها كي يسمح المتصفح بالأصوات.'],
        ['عدّاد', 'يظهر عدد الطلبات الجديدة في عنوان علامة التبويب وبجانب «الطلبات».'],
        ['إشعار', 'بعد تفعيله من الجرس في الأعلى، ينبّهك الحاسوب أو الجهاز اللوحي أيضًا بكل طلب جديد.'],
        ['بريد إلكتروني', 'يُرسل كل طلب أيضًا إلى بريد الإشعارات، حتى لو كانت لوحة الإدارة مغلقة.']
      ],
      tipTitle: 'نصيحتنا للمنضدة',
      tip: 'جهاز لوحي ولوحة الإدارة مفتوحة عليه، مع إيقاف القفل التلقائي للشاشة وتشغيل الصوت. تعمل لوحة الإدارة أيضًا على الهاتف، وتفتح الشريط الجانبي من زر القائمة في الأعلى.',
      phoneLabels: ['لوحة التحكم', 'الطلبات']
    },

    routine: {
      intro: 'هكذا يبدو يوم عمل نموذجي مع المتجر الإلكتروني.',
      day: [
        ['صباحًا', 'افتح لوحة التحكم، وجهّز طلبات اليوم حسب موعد الاستلام، وعدّل المخزون حسب كمية الخَبز.'],
        ['خلال اليوم', 'استقبل الطلبات الجديدة (**بدء التحضير**)، وعند التسليم اختر **تعيين كـ«تم التسليم»**. واجعل مخزون ما نفد صفرًا.'],
        ['مساءً', 'راجع طلبات الغد، وأدخل مخزون اليوم التالي، وأجب عن الرسائل.'],
        ['كل أسبوع', 'أضف منتجات جديدة أو موسمية، وراجع العروض على الشاشات، واكتب مقالًا أو نشرة بريدية.']
      ],
      rulesTitle: 'كيف تعمل مواعيد الاستلام والتوصيل',
      rules: [
        ['الفترات الزمنية', 'يختار العملاء اليوم والساعة بفواصل {slot} دقيقة، حتى {days} أيام مقدمًا، ضمن ساعات عملك فقط، ولا مواعيد في أيام الإغلاق.'],
        ['مدة التحضير', 'أقرب موعد للاستلام بعد {pickup} دقيقة، وللتوصيل بعد {delivery} دقيقة من الطلب.'],
        ['السعة', 'يمكن تحديد عدد أقصى من الطلبات لكل فترة، فتظهر الفترات الممتلئة محجوزة.'],
        ['المخزون', 'يُخصم المخزون فور الطلب ويعود عند الإلغاء. وعندما يصل إلى صفر يظهر المنتج «نفد من المخزون».'],
        ['الدفع الإلكتروني', 'إذا لم يُكمل العميل الدفع الإلكتروني خلال 30 دقيقة، يلغي المتجر الطلب تلقائيًا.']
      ],
      rulesNote: 'تضبط كل هذه القيم في الإعدادات ← الاستلام والتوصيل (الفصل 15).'
    },

    products: {
      intro: 'في **المنتجات** ترى تشكيلتك كاملة، بما فيها المسودات والمنتجات المتوقفة التي لا تظهر في المتجر.',
      points: [
        ['الأرقام الرئيسية', 'عدد المنتجات الكلي والنشطة وقليلة المخزون، وقيمة المخزون.'],
        ['التصفية والبحث', 'صفِّ حسب الفئة والحالة ونطاق السعر وحالة المخزون، وابحث في القائمة من حقل البحث.'],
        ['الإجراءات', 'العين: تفاصيل المنتج. القلم: التعديل. سلة المهملات: الحذف، وإذا ورد المنتج في طلبات سابقة يُعلَّم «متوقف» بدلًا من حذفه.']
      ],
      visibleTitle: 'متى يظهر المنتج في المتجر؟',
      visible: ['الحالة «نشط»', 'خيار «متاح للطلب» مفعّل', 'الفئة ظاهرة'],
      visibleNote: 'إذا كان المخزون صفرًا يبقى ظاهرًا لكن بعلامة «نفد من المخزون»، على شاشات القائمة أيضًا.'
    },

    productForm: {
      intro: 'يفتح زر **إضافة منتج** أو القلم نموذج المنتج. وبعد **إنشاء المنتج** أو **حفظ التغييرات** يظهر في المتجر فورًا.',
      fields: [
        ['الاسم والوصف', 'بالألمانية، اللغة الأساسية للمتجر. يظهر الوصف في صفحة المنتج وعلى شاشات القائمة.'],
        ['الإنجليزية (اختياري)', 'تظهر في المتجر الإنجليزي والعربي. وإذا تُركت فارغة يعرض المتجر النص الألماني.'],
        ['الفئة والحالة', '«مسودة» للمنتجات قيد التحضير، و«نشط» للبيع، و«متوقف» للمنتجات التي لم تعد متوفرة.'],
        ['السعر', 'باليورو شاملًا ضريبة القيمة المضافة، مع نقطة عشرية: 2.40'],
        ['المخزون', 'عدد القطع المتاحة للبيع، وينقص تلقائيًا مع كل طلب.'],
        ['الصورة', 'JPG أو PNG أو WebP حتى 5 ميغابايت. والأجمل صورة PNG بخلفية شفافة.'],
        ['نموذج ثلاثي الأبعاد (اختياري)', 'ملف ‎.glb‎ حتى 20 ميغابايت للعرض الدائري و«شاهده على طاولتك». وبدونه ينشئ المتجر عرضًا ثلاثي الأبعاد من الصورة.'],
        ['الخصائص', 'متاح للطلب، موسمي، نباتي صرف، نباتي، خالٍ من الغلوتين – تظهر كعلامات في المتجر وكخيارات تصفية وعلى شاشات القائمة.']
      ],
      photoTitle: 'نصائح لصور منتجات جميلة',
      photo: ['ضوء النهار، دون فلاش', 'خلفية فاتحة وهادئة، أو إزالة الخلفية', 'صورة مربعة، 1200 × 1200 بكسل على الأقل', 'الأسلوب والزاوية نفسهما لكل المنتجات']
    },

    productDetail: {
      intro: 'تفتح العين في قائمة المنتجات صفحة التفاصيل: الصورة والبيانات الأساسية والمخزون والمكونات والقيم الغذائية.',
      stockTitle: 'تعديل المخزون بسرعة',
      stock: 'في **إدارة المخزون** أدخل العدد الجديد ثم انقر **تحديث** – مثلًا صباحًا بعد الخَبز. القيمة المُدخلة تحل محل المخزون السابق.',
      recipeTitle: 'المكونات والقيم الغذائية',
      recipe: [
        'في **المكونات والقيم الغذائية** حدّد مكونات المنتج، ويساعدك البحث في القوائم الطويلة.',
        'تُستنتج مسببات الحساسية من المكونات وتظهر تحتها مباشرة.',
        'فعّل **عرض القيم الغذائية** وأدخل القيم لكل 100 غرام.',
        '**حفظ المكونات والقيم الغذائية** – فتظهر فورًا في صفحة المنتج.'
      ],
      allergenNote: 'ذكر مسببات الحساسية إلزامي في البيع عبر الإنترنت أيضًا. راجعها مع كل تغيير في الوصفة. وتضيف المكونات الجديدة من **إدارة المكونات** (الفصل 09).'
    },

    ingredients: {
      intro: 'في **المكونات ومسببات الحساسية** تضيف كل مكوّن مرة واحدة وتحدد مسببات الحساسية فيه. وبعدها تكتفي في المنتج باختيار المكونات، فتتبعها مسببات الحساسية تلقائيًا.',
      points: [
        ['مسببات الحساسية', 'نقرة واحدة على زر إضافة مسببات الحساسية الـ14 الرئيسية في الاتحاد الأوروبي تضيف كل المسببات الإلزامية. وتضيف غيرها من الحقل فوقه.'],
        ['المكونات', '**إضافة مكوّن**: الاسم، والإنجليزية اختياريًا، وتحديد مسببات الحساسية التي يحتويها.'],
        ['الاستخدام', 'يعرض عمود «المنتجات» عدد المنتجات التي تحتوي المكوّن. وأي تعديل على المكوّن يظهر في صفحات هذه المنتجات كلها.'],
        ['الحذف', 'يختفي المكوّن المحذوف من كل المنتجات، فراجع عمود «المنتجات» قبل الحذف.']
      ],
      tipTitle: 'بهذا الترتيب',
      tip: ['أضف مسببات الحساسية', 'أضف المكونات مع مسببات حساسيتها', 'حدّد المكونات في كل منتج']
    },

    categories: {
      intro: 'تنظّم الفئات متجرك، مثل الخبز والمعجنات والكعك والبسكويت. ولكل فئة صفحتها في المتجر وعنوانها على شاشات القائمة.',
      points: [
        ['إضافة فئة', 'الاسم والوصف بالألمانية، والإنجليزية اختياريًا.'],
        ['الترتيب', 'الأرقام الأصغر تظهر أولًا، في المتجر وعلى شاشات القائمة.'],
        ['إخفاء وإظهار', 'تختفي الفئات المخفية ومنتجاتها من المتجر لكنها تبقى محفوظة، وهذا مفيد للمنتجات الموسمية.'],
        ['رابط المتجر', 'عنوان صفحة الفئة، مثلًا لإنستغرام.']
      ]
    },

    users: {
      intro: 'في **المستخدمون** ترى جميع الحسابات، عملاءك وفريقك، مع تاريخ التسجيل وعدد الطلبات.',
      points: [
        ['تعطيل', 'لا يستطيع الحساب تسجيل الدخول، وتبقى طلباته محفوظة. ويمكن التراجع في أي وقت عبر **إعادة التفعيل**.'],
        ['تعيين كمدير', 'يمنح صلاحية كاملة على لوحة الإدارة، لفريقك فقط.'],
        ['إزالة صلاحيات المدير', 'عندما يغادر أحد أعضاء الفريق.']
      ],
      teamTitle: 'فريقك',
      team: [
        'لكل شخص حسابه الخاص، دون كلمات مرور مشتركة.',
        'يسجّل الموظفون في المتجر بشكل عادي، ثم تمنحهم صلاحية المدير من هنا.',
        'لا يمكنك تعديل حسابك من هنا، كي لا تُغلق الباب على نفسك بالخطأ.',
        'للمديرين الصلاحيات نفسها التي لك، فامنحها لمن تثق بهم فقط.'
      ]
    },

    journal: {
      intro: 'في **المدونة** تكتب مقالات لصفحة المدونة في متجرك: أخبار ومنتجات موسمية وحكايات من المخبز.',
      stepsTitle: 'كتابة مقال',
      steps: [
        'افتح **مقال جديد**.',
        'العنوان والملخص والنص بالألمانية، وفي تبويب **English** بالإنجليزية اختياريًا. افصل بين الفقرات بسطر فارغ.',
        'ارفع **صورة الغلاف**، ويُفضّل أن تكون أفقية بنسبة 16:9.',
        'تعرض **معاينة** المقال كما سيظهر في المتجر.',
        'في **النشر** اختر: **مسودة** أو **نشر** أو **جدولة** بتاريخ ووقت، ثم احفظ.'
      ],
      statesTitle: 'القائمة',
      states: [
        ['مسودة', 'مرئية في لوحة الإدارة فقط.'],
        ['مجدول', 'يُنشر تلقائيًا في الموعد المحدد.'],
        ['منشور', 'ظاهر في المتجر، والأحدث أولًا.'],
        ['EN', 'للمقال نسخة إنجليزية، ويعرضها المتجر العربي أيضًا.']
      ]
    },

    messages: {
      intro: 'تصل رسائل نموذج التواصل إلى **الرسائل**. ويعرض الرقم في الشريط الجانبي عدد الرسائل المفتوحة. وتصلك كل رسالة أيضًا بالبريد الإلكتروني.',
      stepsTitle: 'الرد على رسالة',
      steps: [
        'انقر الرسالة في القائمة لتظهر كاملة بجانبها.',
        'اكتب في **رد** أو اختر نصًا جاهزًا: **شكر** أو **طلب مسبق** أو **معاودة الاتصال**.',
        '**إرسال الرد** يرسله بالبريد الإلكتروني. وإذا ردّ العميل يصل رده إلى بريد الإشعارات.',
        'تُعدّ الرسالة بذلك منتهية، وتبقى محفوظة مع ردك.'
      ],
      more: [
        ['تحديد كمنتهية', 'للرسائل التي أنهيتها بالهاتف أو في المتجر.'],
        ['في تطبيق البريد الخاص بي', 'يفتح ردًا في برنامج البريد الإلكتروني لديك.'],
        ['مفتوحة · منتهية · الكل', 'تصفية فوق القائمة، ويجد البحث الأسماء وعناوين البريد والنصوص.']
      ]
    },

    newsletter: {
      intro: 'في **النشرة البريدية** تكتب النشرات وترسلها إلى كل من اشترك فيها من المتجر.',
      stepsTitle: 'إرسال نشرة بريدية',
      steps: [
        '**نشرة بريدية جديدة**: اكتب الموضوع والنص، وترى بجانبهما شكل البريد الإلكتروني.',
        '**إرسال تجريبي لي** يرسلها أولًا إلى بريدك.',
        '**إرسال إلى …** يرسلها إلى كل المشتركين النشطين. وتبقى النشرات المرسلة في القائمة.',
        'يحتوي كل بريد على رابط شخصي لإلغاء الاشتراك، ولا يصل شيء إلى من ألغى اشتراكه.'
      ],
      subsTitle: 'المشتركون',
      subs: 'يعرض تبويب **المشتركون** كل الاشتراكات، النشطة والملغاة. استخدم **إضافة عنوان** فقط بموافقة الشخص، مثلًا من قائمة اشتراك في المتجر، و**تصدير بصيغة CSV** لسجلاتك.',
      law: 'لا تراسل إلا من اشترك بنفسه أو وافق صراحة.'
    },

    shopSettings: {
      intro: 'في **الإعدادات** تدير كل ما يخص متجرك. وتسري التغييرات فورًا: في المتجر وصفحة الدفع والرسائل الإلكترونية وشاشات القائمة وبيانات الناشر. احفظ عبر **حفظ التغييرات**.',
      items: [
        ['ساعات العمل', 'شغّل كل يوم أو أوقفه، مع استراحة غداء أو فترة ثانية. ويوفّر عليك زر تطبيق مواعيد الاثنين على باقي أيام الأسبوع الكتابة.'],
        ['أيام الإغلاق', 'العطل الرسمية والإجازات والجرد: لا مواعيد استلام في هذه الأيام، وتعرضها صفحة التواصل.'],
        ['الاستلام والتوصيل', 'التشغيل والإيقاف، ورسوم التوصيل، ومدة التحضير، وطول الفترة الزمنية، والأيام المتاحة مقدمًا، والطلبات لكل فترة.'],
        ['إعلان المتجر', 'شريط أعلى كل صفحة، مثل «مغلق يوم الاثنين»، بالألمانية والإنجليزية.'],
        ['النشاط التجاري والتواصل', 'الاسم والعنوان والهاتف والبريد وطريقة الوصول وروابط التواصل الاجتماعي.'],
        ['بيانات الناشر', 'الشركة أو المالك، والشخص المسؤول، والرقم الضريبي، والسجل التجاري.'],
        ['الإشعارات', 'البريد الإلكتروني الذي تصله الطلبات الجديدة ورسائل التواصل.']
      ],
      note: 'الحقول الفارغة تأخذ الإعدادات الأساسية من الخادم. وما دمت لم تحفظ شيئًا تظهر في الأسفل عبارة تطبيق الإعدادات الافتراضية للخادم.'
    },

    screens: {
      intro: 'في **شاشات القائمة** تصمم القوائم لأجهزة التلفاز في المتجر، لكل من المنضدة والواجهة وركن المقهى قائمته الخاصة. وتأتي الأسعار والصور وعلامة «نفد» مباشرة من المتجر.',
      card: 'تعرض كل بطاقة معاينة، وهل التلفاز **متصل** (مع الدقة)، والرمز المكوّن من 4 أرقام. يفتح **تصميم** المحرر، و**فتح** صفحة الشاشة، وإلى جانبهما إعادة التحميل والنسخ والحذف.',
      designTitle: 'تبويب «التصميم»',
      design: [
        ['التخطيط', '**أعمدة مع منتج بارز** أو **مربعات صور** أو **قائمة كلاسيكية** أو **منتج واحد بحجم كبير** (الفصل 17).'],
        ['نمط الألوان', 'خمسة أنماط أو **ألوان مخصصة**، مع صورة خلفية تُعتَّم.'],
        ['الخط', 'أنيق أو عصري.'],
        ['اللغة', 'الألمانية أو الإنجليزية أو العربية، أو لغتان بالتناوب.'],
        ['الاتجاه', 'تلقائي، أو عمودي إذا كان التلفاز مُعلّقًا بالطول.']
      ],
      live: 'تعرض المعاينة المباشرة بجانب المحرر كل تغيير. ويرسل **حفظ ونشر** التغييرات إلى أجهزة التلفاز خلال دقيقة.'
    },

    screenContent: {
      contentTitle: 'تبويب «المحتوى»',
      content: 'العنوان والشريط المتحرك (بالألمانية والإنجليزية، وبالعربية أيضًا للشاشات العربية)، وما يُعرض – الأسعار والأوصاف والصور وعلامات نباتي وغيرها ورمز QR والساعة ومفتوح/مغلق –، وكيف تظهر المنتجات النافدة، ومدة كل صفحة، والفئات والمنتجات التي تعرضها الشاشة.',
      slidesTitle: 'تبويب «العروض»',
      slides: [
        '**إضافة عرض** على شكل **منتج** (بصورته من المتجر) أو **صورة** (صورتك الخاصة) أو **رسالة** (نص فقط).',
        'العنوان والنص والسعر وإضافة مثل «بدلًا من 5.40 €».',
        'في **متى** الفترة والساعة وأيام الأسبوع، مثلًا فطور من الاثنين إلى الجمعة من 6 إلى 11. وإذا تُركت فارغة يُعرض العرض دائمًا.',
        'تعرض العين العرض فورًا في المعاينة، وتغيّر الأسهم الترتيب.'
      ],
      layoutsTitle: 'التخطيطات الأربعة',
      layouts: ['أعمدة مع منتج بارز', 'منتج واحد بحجم كبير', 'مربعات صور', 'قائمة كلاسيكية']
    },

    tv: {
      intro: 'لكل شاشة رمز من 4 أرقام. هكذا تصل إلى التلفاز، مرة واحدة وفي دقيقتين:',
      steps: [
        ['افتح العنوان', 'افتح المتصفح على التلفاز أو جهاز البث وانتقل إلى {url}.'],
        ['أدخل الرمز', 'أدخل الرمز بجهاز التحكم واختر **تشغيل الشاشة**.'],
        ['انتهى', 'يتذكر الجهاز الشاشة ويشغّلها تلقائيًا بعد كل إعادة تشغيل.']
      ],
      devicesTitle: 'أي جهاز؟',
      devices: [
        ['Fire TV Stick (موصى به)', 'رخيص وموثوق. ثبّت «Fully Kiosk Browser»، واجعل صفحة البداية …/tv، وفعّل التشغيل عند الإقلاع وإبقاء الشاشة مضاءة.'],
        ['تلفاز ذكي', 'يكفي المتصفح المدمج في البداية، وبعض الأجهزة تنسى الصفحة عند إطفائها.'],
        ['Raspberry Pi', 'للتشغيل المستمر: السكربت deploy/kiosk/setup-raspberry-pi.sh يُعدّ كل شيء.'],
        ['PC أو Mini PC', 'ضع deploy/kiosk/menu-screen-windows.bat في مجلد بدء التشغيل.']
      ],
      deviceTitle: 'تبويب «الجهاز»',
      device: 'الرمز ورمز QR وعنوان الشاشة، وهل هي متصلة وبأي دقة. ويعيد **إعادة تحميل الشاشة** تشغيل الصفحة على التلفاز عن بُعد.',
      tipsTitle: 'على التلفاز',
      tips: [
        'أوقف وضع توفير الطاقة ومؤقت الإطفاء وشاشة التوقف.',
        'اختر وضع الصورة «قياسي» أو «طبيعي» بدل «ديناميكي».',
        'بمؤقت التشغيل والإطفاء في التلفاز تبدأ القائمة تلقائيًا مع افتتاح المتجر.',
        'دون إنترنت تواصل الشاشة عرض آخر قائمة حمّلتها.'
      ]
    },

    emails: {
      intro: 'يرسل المتجر الرسائل تلقائيًا بمجرد إعداد خادم البريد الإلكتروني (الفصل 20)، ويتلقاها العملاء باللغة التي طلبوا بها.',
      list: [
        ['تأكيد الطلب', 'إلى العميل، بالألمانية أو الإنجليزية أو العربية.'],
        ['طلب جديد', 'إلى بريد الإشعارات، مع رابط إلى لوحة الإدارة.'],
        ['إلغاء الطلب', 'إلى العميل عند إلغاء الطلب.'],
        ['نموذج التواصل', 'كل رسالة إلى بريد الإشعارات.'],
        ['الردود والنشرات', 'من لوحة الإدارة، ومتجرك هو المرسل.'],
        ['نسيت كلمة المرور', 'رابط إعادة التعيين إلى العميل.']
      ],
      customer: 'تأكيد إلى العميل',
      shop: 'تنبيه إليك (بالألمانية)'
    },

    server: {
      intro: 'تضبط كل شيء تقريبًا من لوحة الإدارة. أما هذه القيم فقط فتوجد في ملف ‎.env.production‎ على الخادم، والأسهل أن يضبطها مطوّر موقعك مرة واحدة. وبعدها يعيد الأمر «docker compose up -d» تشغيل المتجر.',
      head: ['الإعداد', 'المعنى', 'مثال'],
      rows: [
        ['FRONTEND_URL', 'عنوان متجرك، للروابط في الرسائل ورموز QR', 'https://backlover.de'],
        ['EMAIL_HOST, EMAIL_PORT', 'خادم البريد للإرسال', 'smtp.… · 587'],
        ['EMAIL_HOST_USER, …_PASSWORD', 'بيانات الدخول إلى خادم البريد', 'hallo@…'],
        ['DEFAULT_FROM_EMAIL', 'مرسل كل الرسائل', 'Backlover <hallo@…>'],
        ['STRIPE_SECRET_KEY', 'المفتاح السري للدفع الإلكتروني', 'sk_live_…'],
        ['STRIPE_WEBHOOK_SECRET', 'مفتاح Webhook الخاص بـ Stripe', 'whsec_…'],
        ['SHOP_…', 'القيم الأساسية لساعات العمل والرسوم وغيرها، وتسري ما لم يُحفظ شيء في لوحة الإدارة', 'mon-fri 07:00-18:00']
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
        ['كلمات مرور قوية', '12 حرفًا على الأقل، وحساب خاص لكل شخص. ويعيد «نسيت كلمة المرور؟» تعيينها في أي وقت.'],
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
        ['منتج لا يظهر في المتجر', 'هل الحالة «نشط»؟ هل «متاح للطلب» مفعّل؟ هل الفئة ظاهرة؟'],
        ['لا تصل الرسائل الإلكترونية', 'افحص مجلد الرسائل المزعجة، وراجع البريد في الإعدادات ← الإشعارات، واطلب فحص خادم البريد.'],
        ['لا صوت عند الطلبات الجديدة', 'انقر مرة داخل الصفحة، وشغّل صوت الجهاز، وأبقِ علامة التبويب في المقدمة.'],
        ['الدفع الإلكتروني غير ظاهر', 'مفاتيح Stripe غير موجودة أو غير صحيحة.'],
        ['التلفاز لا يعرض الجديد', 'تحقق في لوحة الإدارة من اتصال الشاشة، ثم **إعادة تحميل الشاشة**، وافحص اتصال التلفاز بالإنترنت.'],
        ['التلفاز يطلب الرمز من جديد', 'أدخل الرمز مرة أخرى، مثلًا بعد مسح بيانات المتصفح.'],
        ['كل الفترات محجوزة', 'في الإعدادات ← الاستلام والتوصيل اسمح بطلبات أكثر لكل فترة (0 = بلا حد)، وراجع ساعات العمل وأيام الإغلاق.']
      ],
      checklistTitle: 'قبل الإطلاق',
      checklist: [
        'بيانات الناشر والنصوص القانونية مكتملة',
        'ساعات العمل ورسوم التوصيل والعنوان مُدخلة',
        'كل المنتجات بصورة وسعر ومخزون ومكونات ومسببات حساسية',
        'طلب تجريبي بكل طرق الدفع، والرسائل تصل',
        'شاشات القائمة مصممة ومرتبطة بالتلفاز',
        'جهاز لوحي عند المنضدة ولوحة الإدارة مفتوحة',
        'نسخ احتياطي تلقائي مُعدّ'
      ],
      weeklyTitle: 'كل أسبوع',
      weekly: ['مراجعة المخزون والأسعار', 'هل أُجيب عن كل الرسائل؟', 'هل العروض على الشاشات محدّثة؟', 'مقال في المدونة أو نشرة بريدية']
    },

    back: {
      title: 'نتمنى لك النجاح مع متجرك الإلكتروني!',
      contactTitle: 'جهة الاتصال',
      contactLines: ['الاسم', 'الهاتف', 'البريد الإلكتروني']
    }
  }
}
