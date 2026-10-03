// The customer guide: an A4 brochure about the bakery and the online shop,
// with screenshots of every page of the website.
import { addressLines, browser, documentHtml, esc, hoursList, host, logo, phone, photo, price, qr, screen, shop, shopUrl, text, tv } from '../shared.mjs'

// Every page of the website, in the order the guide shows them.
const ALL_PAGES = [
  ['home', '/'], ['shop', '/products'], ['category', '/categories/pastries'], ['seasonal', '/seasonal'],
  ['product', '/products/…'], ['cart', '/cart'], ['checkout', '/checkout'], ['checkout-time', '/checkout'],
  ['order', '/orders/…'], ['orders', '/orders'], ['profile', '/profile'], ['settings', '/settings'],
  ['wishlist', '/wishlist'], ['compare', '/compare'], ['journal', '/blog'], ['journal-post', '/blog/…'],
  ['about', '/about'], ['contact', '/contact'], ['login', '/login'], ['register', '/register'],
  ['forgot-password', '/forgot-password'], ['impressum', '/impressum'], ['privacy', '/privacy'],
  ['terms', '/terms'], ['cookies', '/cookie-policy'], ['not-found', '/…'], ['menu-board', '/menu-board']
]
const pathOf = (name) => ALL_PAGES.find(([key]) => key === name)?.[1] || ''

export async function guideDocument(lang) {
  const t = (path, params) => text(lang, path, params)
  const ar = lang === 'ar'
  const fee = price(shop.deliveryFee, lang)
  const params = { fee, lead: shop.pickupLeadMinutes, deliveryLead: shop.deliveryLeadMinutes, site: `<bdi dir="ltr">${esc(host())}</bdi>` }
  const num = (n) => (ar ? String(n).replace(/\d/g, d => '٠١٢٣٤٥٦٧٨٩'[d]) : String(n).padStart(2, '0'))
  const edition = new Intl.DateTimeFormat(ar ? 'ar' : 'de-DE', { month: 'long', year: 'numeric', numberingSystem: 'latn' }).format(new Date())
  const codeDark = await qr(shopUrl('/products'))
  const codeLight = await qr(shopUrl('/products'), { dark: '#f4ece1' })
  const S = t('guide.sections')

  // Page numbers of each section (pages are counted below).
  const TOC = [
    ['glance', 3], ['order', 4], ['discover', 6], ['pickup', 7], ['account', 8], ['mobile', 9],
    ['inStore', 10], ['more', 11], ['allPages', 12], ['privacy', 14], ['faq', 15]
  ]
  const sectionNo = (key) => TOC.findIndex(([k]) => k === key) + 1

  const shell = (n, body, { title } = {}) => `
  <div class="sheet paper">
    <header class="run">${logo('run-logo')}<span>${t('guide.title')}</span></header>
    <div class="body">
      ${title ? `<div class="sec-head"><span class="sec-no">${num(sectionNo(title))}</span><h2 class="display sec-title">${esc(S[title])}</h2></div>` : ''}
      ${body}
    </div>
    <footer class="run-foot"><span>${esc(t('guide.screenshotNote'))}</span><span class="page-no">${num(n)}</span></footer>
  </div>`

  const pages = []

  // 1 — Cover
  pages.push(`
  <div class="sheet dark">
    <div class="cover">
      <header class="cover-top">${logo('cover-logo')}<span class="eyebrow">${t('bakery')} · ${t('placeLine')}</span></header>
      <img class="cutout cv-a" src="${photo('croissant-butter.png')}" alt="">
      <img class="cutout cv-b" src="${photo('pretzel.png')}" alt="">
      <img class="cutout cv-c" src="${photo('donut-caramel.png')}" alt="">
      <img class="cutout cv-d" src="${photo('macarons.png')}" alt="">
      <img class="cutout cv-e" src="${photo('cuppchtino.png')}" alt="">
      <div class="cover-copy">
        <p class="eyebrow">${t('guide.edition', { date: edition })}</p>
        <h1 class="display cover-title">${t('guide.title')}</h1>
        <p class="cover-sub">${t('guide.subtitle')}</p>
      </div>
      <footer class="cover-foot">
        <span>${addressLines(lang).join(' · ')}</span>
        <span dir="ltr">${esc(host())}</span>
      </footer>
    </div>
  </div>`)

  // 2 — Welcome and contents
  pages.push(shell(2, `
    <div class="welcome">
      <div>
        <p class="eyebrow">${t('bakery')} · ${t('placeLine')}</p>
        <h1 class="display welcome-title">${t('guide.welcomeTitle')}</h1>
        ${t('guide.welcome').map(p => `<p class="lead">${esc(p)}</p>`).join('')}
      </div>
      <div class="welcome-photo" style="background-image:url('${photo('WhatsApp Image 2025-01-17 at 17.24.35_bd8602a2.jpg')}')"></div>
    </div>
    <div class="toc">
      <p class="eyebrow">${t('guide.contents')}</p>
      <ol>${TOC.map(([key, page], i) => `<li><span class="toc-no">${num(i + 1)}</span><span class="toc-name">${esc(S[key])}</span><span class="toc-dots"></span><span class="toc-page">${num(page)}</span></li>`).join('')}</ol>
    </div>`))

  // 3 — At a glance
  const G = t('guide.glance')
  pages.push(shell(3, `
    <div class="cards cards-3">
      <div class="card"><p class="card-label">${G.address}</p><p>${addressLines(lang).join('<br>')}</p></div>
      <div class="card"><p class="card-label">${G.hours}</p><div class="hours">${hoursList(lang)}</div></div>
      <div class="card card-qr"><div><p class="card-label">${G.web}</p><p class="url" dir="ltr">${esc(host())}</p></div><div class="qr q-sm">${codeDark}</div></div>
      <div class="card"><p class="card-label">${G.payment}</p><p>${esc(G.paymentText)}</p></div>
      <div class="card"><p class="card-label">${G.delivery}</p><p>${t('guide.glance.deliveryText', { fee })}</p></div>
      <div class="card"><p class="card-label">${G.languages}</p><p>${esc(G.languagesText)}</p></div>
    </div>
    <div class="hero-shot">${browser(screen(lang, 'home'), '/')}</div>`, { title: 'glance' }))

  // 4–5 — Ordering in five steps
  const steps = t('guide.orderSteps')
  const step = ([title, body, shot], i) => `
    <div class="step">
      <div class="step-text">
        <span class="step-n">${num(i + 1)}</span>
        <h3 class="display step-title">${esc(title)}</h3>
        <p>${body.replace('{site}', params.site)}</p>
      </div>
      <div class="step-shot">${browser(screen(lang, shot), pathOf(shot))}</div>
    </div>`
  pages.push(shell(4, `<div class="steps">${steps.slice(0, 3).map(step).join('')}</div>`, { title: 'order' }))
  pages.push(shell(5, `
    <div class="steps">${steps.slice(3).map((s, i) => step(s, i + 3)).join('')}</div>
    <div class="tip">
      <div class="qr q-md">${codeDark}</div>
      <div><p class="card-label">${t('web')}</p><p class="tip-title display">${t('scanToOrder')}</p><p class="url" dir="ltr">${esc(host())}</p></div>
    </div>`))

  // 6 — Discover products, 3D and AR
  pages.push(shell(6, `
    <div class="duo">
      ${t('guide.discover').map(([title, body, shot]) => `
        <div class="duo-item">${browser(screen(lang, shot), pathOf(shot))}<h3 class="display mini-title">${esc(title)}</h3><p>${esc(body)}</p></div>`).join('')}
    </div>
    <div class="cards cards-3 tips">
      ${t('guide.discoverTips').map(([title, body]) => `<div class="card"><p class="card-title">${esc(title)}</p><p>${esc(body)}</p></div>`).join('')}
    </div>
    <div class="feature">
      <div class="feature-shot">${browser(screen(lang, 'product'), pathOf('product'))}</div>
      <div class="feature-phone">${phone(screen(lang, 'mobile-product'))}</div>
      <div class="feature-text">
        <p class="card-label">3D · AR</p>
        <h3 class="display feature-title">${t('guide.threeD.title')}</h3>
        <p>${t('guide.threeD.text')}</p>
      </div>
    </div>`, { title: 'discover' }))

  // 7 — Pickup, delivery, payment
  pages.push(shell(7, `
    <div class="cards cards-2">
      ${t('guide.pickup').map(([title, body], i) => `
        <div class="card card-icon"><span class="card-n">${num(i + 1)}</span><p class="card-title">${esc(title)}</p><p>${body.replace('{lead}', params.lead).replace('{deliveryLead}', params.deliveryLead).replace('{fee}', fee)}</p></div>`).join('')}
    </div>
    <div class="hero-shot">${browser(screen(lang, 'checkout'), '/checkout')}</div>`, { title: 'pickup' }))

  // 8 — Customer account
  pages.push(shell(8, `
    <div class="grid-3">
      ${t('guide.account').map(([title, body, shot]) => `
        <div class="tile">${browser(screen(lang, shot), pathOf(shot))}<h3 class="tile-title">${esc(title)}</h3><p>${esc(body)}</p></div>`).join('')}
    </div>
    <div class="perks">
      <div class="perks-text">
        <h3 class="display feature-title">${t('guide.accountPerks.title')}</h3>
        <ul>${t('guide.accountPerks.items').map(item => `<li>${esc(item)}</li>`).join('')}</ul>
      </div>
      <div class="perks-shot">${browser(screen(lang, 'login'), pathOf('login'))}</div>
    </div>`, { title: 'account' }))

  // 9 — On the phone
  pages.push(shell(9, `
    <p class="lead lead-wide">${esc(t('guide.mobile'))}</p>
    <div class="phones">
      ${t('guide.mobileShots').map(([shot, label]) => `<div class="phone-col">${phone(screen(lang, `mobile-${shot}`))}<p>${esc(label)}</p></div>`).join('')}
    </div>
    <div class="tip">
      <div class="qr q-md">${codeDark}</div>
      <div><p class="card-label">${t('web')}</p><p class="tip-title display">${t('scanToOrder')}</p><p class="url" dir="ltr">${esc(host())}</p></div>
    </div>`, { title: 'mobile' }))

  // 10 — In the shop: the menu screens
  pages.push(shell(10, `
    <div class="tv-wrap">${tv(screen(lang, 'menu-board'))}</div>
    <div class="cards cards-3">
      ${t('guide.inStorePoints').map(([title, body], i) => `<div class="card card-icon"><span class="card-n">${num(i + 1)}</span><p class="card-title">${esc(title)}</p><p>${esc(body)}</p></div>`).join('')}
    </div>
    <div class="instore">
      <div>
        <h3 class="display feature-title">${t('guide.inStore.title')}</h3>
        <p class="lead">${t('guide.inStore.text')}</p>
      </div>
      <div class="instore-qr"><div class="qr q-md">${codeDark}</div><p dir="ltr">${esc(host())}</p></div>
    </div>`, { title: 'inStore' }))

  // 11 — Journal, newsletter, contact
  pages.push(shell(11, `
    <div class="grid-2">
      ${t('guide.more').map(([title, body, shot]) => `
        <div class="tile">${browser(screen(lang, shot), pathOf(shot))}<h3 class="tile-title">${esc(title)}</h3><p>${esc(body)}</p></div>`).join('')}
    </div>
    <div class="note">${esc(t('guide.newsletter'))}</div>`, { title: 'more' }))

  // 12–13 — Every page
  const names = t('guide.pageNames')
  const thumb = ([key, path]) => `<div class="thumb">${browser(screen(lang, key), path)}<p><strong>${esc(names[key])}</strong><span dir="ltr">${esc(path)}</span></p></div>`
  // The legal pages are shown larger on the privacy page.
  const LEGAL = ['impressum', 'privacy', 'terms', 'cookies']
  const indexed = ALL_PAGES.filter(([key]) => !LEGAL.includes(key))
  const legalCard = `<div class="thumb-note"><p class="card-label">${esc(S.privacy)}</p><p>${LEGAL.map(key => esc(names[key])).join(' · ')}</p><span class="page-no">→ ${num(14)}</span></div>`
  pages.push(shell(12, `<div class="thumbs">${indexed.slice(0, 12).map(thumb).join('')}</div>`, { title: 'allPages' }))
  pages.push(shell(13, `<div class="thumbs">${indexed.slice(12).map(thumb).join('')}${legalCard}</div>`))

  // 14 — Privacy and legal
  pages.push(shell(14, `
    <ul class="bullets">${t('guide.privacy').map(p => `<li>${esc(p)}</li>`).join('')}</ul>
    <div class="grid-2 grid-legal">
      ${LEGAL.map(key => `<div class="tile">${browser(screen(lang, key), pathOf(key))}<h3 class="tile-title">${esc(names[key])}</h3></div>`).join('')}
    </div>`, { title: 'privacy' }))

  // 15 — FAQ
  pages.push(shell(15, `
    <div class="faq">
      ${t('guide.faq').map(([q, a]) => `<div class="faq-item"><h3 class="faq-q">${esc(q)}</h3><p>${esc(a).replace('{lead}', params.lead).replace('{fee}', fee)}</p></div>`).join('')}
    </div>
    <div class="tip tip-dark">
      <div class="qr q-md">${codeLight}</div>
      <div><p class="card-label">${t('web')}</p><p class="tip-title display">${t('scanToOrder')}</p><p class="url" dir="ltr">${esc(host())}</p></div>
    </div>`, { title: 'faq' }))

  // 16 — Back cover
  pages.push(`
  <div class="sheet dark">
    <div class="cover back">
      ${logo('cover-logo')}
      <h2 class="display back-title">${t('guide.backTitle')}</h2>
      <img class="cutout bk-a" src="${photo('croissant-chocolate.png')}" alt="">
      <img class="cutout bk-b" src="${photo('latte.png')}" alt="">
      <div class="back-grid">
        <div><p class="eyebrow">${t('hours')}</p><div class="hours">${hoursList(lang)}</div></div>
        <div><p class="eyebrow">${t('address')}</p><p>${addressLines(lang).join('<br>')}</p></div>
        <div class="back-qr"><div class="qr qr-card q-lg">${codeDark}</div><p dir="ltr">${esc(host())}</p></div>
      </div>
      <p class="back-small">${t('allergenNote')}</p>
    </div>
  </div>`)

  return documentHtml({ lang, title: `${t('guide.title')} – Backlover`, width: '210mm', height: '297mm', pages, css: CSS })
}

const CSS = `
  .sheet.paper { display: flex; flex-direction: column; }
  .run { display: flex; align-items: baseline; justify-content: space-between; margin: 12mm 16mm 0; padding-bottom: 3mm;
    border-bottom: 0.25mm solid var(--line); font-size: 7.5pt; color: var(--muted); }
  .run-logo { font-size: 15pt; }
  .run-foot { display: flex; justify-content: space-between; align-items: center; margin: 0 16mm 9mm; padding-top: 3mm;
    border-top: 0.25mm solid var(--line); font-size: 6.5pt; color: var(--muted); }
  .page-no { font: 400 13pt var(--display); color: var(--crust); }
  .body { flex: 1; min-height: 0; padding: 8mm 16mm 6mm; display: flex; flex-direction: column; gap: 7mm; }
  [lang="ar"] .body { font-size: 1.06em; }

  .sec-head { display: flex; align-items: baseline; gap: 4mm; }
  .sec-no { font: 400 30pt var(--display); color: var(--crust); }
  .sec-title { font-size: 30pt; }
  [lang="ar"] .sec-title { font-size: 25pt; }
  .lead { font-size: 10pt; line-height: 1.65; color: var(--ink-2); }
  .lead + .lead { margin-top: 3mm; }
  .lead-wide { max-width: 150mm; }
  .card-label { font-size: 7pt; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: var(--crust); margin-bottom: 1.5mm; }
  [lang="ar"] .card-label { letter-spacing: 0; font-size: 8.5pt; }
  .url { font-weight: 700; color: var(--crust); }
  p { font-size: 8.6pt; line-height: 1.6; color: var(--ink-2); }
  .dark p { color: var(--cream-muted); }
  .hours { display: grid; gap: 0.8mm; font-size: 8.6pt; }
  .qr { flex: none; }
  .q-sm { width: 18mm; height: 18mm; }
  .q-md { width: 26mm; height: 26mm; }
  .q-lg { width: 34mm; height: 34mm; }

  /* Cover */
  .cover { position: absolute; inset: 18mm 18mm 16mm; display: flex; flex-direction: column; }
  .cover-top { display: flex; align-items: baseline; justify-content: space-between; }
  .cover-logo { font-size: 30pt; }
  .cv-a { width: 128mm; top: 28mm; inset-inline-end: -22mm; transform: rotate(-9deg); }
  .cv-b { width: 70mm; top: 92mm; inset-inline-start: 0; transform: rotate(-14deg); }
  .cv-c { width: 52mm; top: 118mm; inset-inline-end: 6mm; transform: rotate(8deg); }
  .cv-d { width: 32mm; top: 30mm; inset-inline-start: 8mm; }
  .cv-e { width: 46mm; top: 56mm; inset-inline-start: 46mm; }
  .cover-copy { margin-top: auto; position: relative; }
  .cover-title { margin-top: 3mm; font-size: 62pt; line-height: 0.95; }
  [lang="ar"] .cover-title { font-size: 48pt; line-height: 1.3; }
  .cover-sub { margin-top: 4mm; font-size: 13pt; color: var(--cream-muted); }
  .cover-foot { display: flex; justify-content: space-between; margin-top: 10mm; padding-top: 5mm; border-top: 0.25mm solid rgba(244, 236, 225, 0.15);
    font-size: 8pt; color: var(--cream-muted); }

  /* Welcome */
  .welcome { display: grid; grid-template-columns: 1fr 64mm; gap: 9mm; }
  .welcome-title { margin: 2mm 0 5mm; font-size: 30pt; }
  [lang="ar"] .welcome-title { font-size: 24pt; }
  .welcome-photo { border-radius: 4mm; background-size: cover; background-position: center; min-height: 92mm; }
  .toc { padding: 7mm 8mm; border-radius: 4mm; background: var(--oven); color: var(--cream); }
  .toc .eyebrow { color: var(--crust-light); margin-bottom: 3mm; }
  .toc ol { list-style: none; display: grid; gap: 2.4mm; }
  .toc li { display: flex; align-items: baseline; gap: 3mm; font-size: 10pt; }
  .toc-no { width: 7mm; font: 400 12pt var(--display); color: var(--crust-light); }
  .toc-dots { flex: 1; border-bottom: 0.3mm dotted rgba(244, 236, 225, 0.25); }
  .toc-page { font-weight: 700; color: var(--gold); }

  /* Cards */
  .cards { display: grid; gap: 4mm; }
  .cards-3 { grid-template-columns: repeat(3, 1fr); }
  .cards-2 { grid-template-columns: repeat(2, 1fr); }
  .card { padding: 4.5mm 5mm; border-radius: 3.5mm; background: rgba(255, 255, 255, 0.55); border: 0.25mm solid var(--line); }
  .card-qr { display: flex; align-items: center; justify-content: space-between; gap: 3mm; }
  .card-icon { position: relative; padding-top: 6mm; }
  .card-n { font: 400 22pt var(--display); color: var(--crust); }
  .card-title { margin: 1mm 0 1.5mm; font-size: 11pt; font-weight: 700; color: var(--ink); }
  .hero-shot { margin-top: auto; }

  /* Steps */
  .steps { display: grid; gap: 8mm; }
  .step { display: grid; grid-template-columns: 1fr 96mm; gap: 8mm; align-items: center; }
  .step-n { font: 400 30pt var(--display); color: var(--crust); line-height: 1; }
  .step-title { margin: 1.5mm 0 2mm; font-size: 17pt; }
  [lang="ar"] .step-title { font-size: 15pt; }
  .tip { margin-top: auto; display: flex; align-items: center; gap: 6mm; padding: 6mm; border-radius: 4mm; background: rgba(230, 161, 90, 0.16); }
  .tip-title { font-size: 17pt; margin-bottom: 1.5mm; }
  .tip-dark { background: var(--oven); color: var(--cream); }
  .tip-dark p { color: var(--cream-muted); }
  .tip-dark .url, .tip-dark .card-label { color: var(--gold); }

  /* Discover */
  .duo { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }
  .mini-title { margin: 3mm 0 1mm; font-size: 14pt; }
  .tips .card-title { font-size: 10pt; }
  .feature { position: relative; display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; padding: 6mm; border-radius: 4mm; background: var(--oven); color: var(--cream); margin-top: auto; }
  .feature p { color: var(--cream-muted); }
  .feature .card-label { color: var(--crust-light); }
  .feature-shot { grid-column: 1; }
  .feature-phone { position: absolute; width: 30mm; bottom: -4mm; inset-inline-start: 72mm; transform: rotate(4deg); }
  .feature-text { grid-column: 2; padding-inline-start: 22mm; }
  .feature-title { font-size: 16pt; margin-bottom: 2mm; }
  [lang="ar"] .feature-title { font-size: 14pt; }

  /* Grids of screenshots */
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 7mm 5mm; }
  .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 7mm 6mm; }
  .tile-title { margin: 2.5mm 0 0.8mm; font-size: 10pt; font-weight: 700; }
  .perks { margin-top: auto; display: grid; grid-template-columns: 1fr 84mm; gap: 8mm; align-items: center; padding: 7mm; border-radius: 4mm; background: var(--oven); color: var(--cream); }
  .perks ul { list-style: none; display: grid; gap: 2.4mm; margin-top: 3mm; }
  .perks li { position: relative; padding-inline-start: 6mm; font-size: 9pt; line-height: 1.5; color: var(--cream-muted); }
  .perks li::before { content: '✓'; position: absolute; inset-inline-start: 0; color: var(--crust-light); font-weight: 800; }
  .note { margin-top: auto; padding: 5mm 6mm; border-radius: 3.5mm; background: rgba(230, 161, 90, 0.16); font-size: 9pt; line-height: 1.6; }

  /* Phones */
  .phones { flex: 1; display: grid; grid-template-columns: repeat(4, 1fr); gap: 6mm; align-items: center; }
  .phone-col { text-align: center; }
  .phone-col:nth-child(even) { transform: translateY(10mm); }
  .phone-col p { margin-top: 3mm; font-weight: 700; color: var(--ink); }

  /* In the shop */
  .tv-wrap { padding: 2mm 6mm 8mm; }
  .instore { display: grid; grid-template-columns: 1fr auto; gap: 8mm; align-items: center; margin-top: auto; }
  .instore-qr { display: grid; justify-items: center; gap: 2mm; font-size: 8pt; font-weight: 700; color: var(--crust); }

  /* All pages */
  .thumbs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 4.5mm 5mm; }
  .thumb p { min-width: 0; display: flex; justify-content: space-between; gap: 2mm; margin-top: 1.5mm; font-size: 7pt; }
  .thumb strong { color: var(--ink); }
  .thumb span { color: var(--muted); }
  .thumb-note { display: flex; flex-direction: column; justify-content: center; gap: 1mm; padding: 5mm; border-radius: 2.2mm; border: 0.3mm dashed var(--crust); aspect-ratio: 1440 / 1000; }
  .thumb .frame-bar { height: 3.4mm; }
  .thumb .frame-bar span { font-size: 4.2pt; }

  /* Privacy and FAQ */
  .bullets { display: grid; gap: 3mm; padding-inline-start: 5mm; }
  .bullets li { font-size: 9.6pt; line-height: 1.6; color: var(--ink-2); }
  .bullets li::marker { color: var(--crust); }
  .grid-legal { margin-top: 2mm; }
  .faq { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm 9mm; }
  .faq-q { font: 400 14pt var(--display); margin-bottom: 1.5mm; }
  [lang="ar"] .faq-q { font-size: 12.5pt; font-weight: 600; }

  /* Back cover */
  .back { justify-content: flex-start; }
  .back-title { margin-top: 10mm; font-size: 40pt; max-width: 130mm; }
  [lang="ar"] .back-title { font-size: 32pt; }
  .bk-a { width: 110mm; top: 76mm; inset-inline-end: -14mm; transform: rotate(-10deg); }
  .bk-b { width: 62mm; top: 92mm; inset-inline-start: 10mm; }
  .back-grid { margin-top: auto; display: grid; grid-template-columns: 1fr 1fr auto; gap: 8mm; align-items: end; font-size: 9pt; line-height: 1.6; }
  .back-grid p, .back-grid .hours { color: var(--cream); }
  .back-grid .eyebrow { margin-bottom: 2mm; color: var(--crust-light); }
  .back-qr { display: grid; justify-items: center; gap: 2mm; font-size: 8.5pt; font-weight: 700; }
  .back-qr p { color: var(--gold); }
  .back-small { margin-top: 8mm; font-size: 7pt; }
`
