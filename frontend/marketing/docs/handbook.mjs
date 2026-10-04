// The owner handbook: an A4 brochure for the bakery on running the shop day
// to day, with screenshots of the admin. Texts are in data/handbook.mjs.
import handbook from '../data/handbook.mjs'
import { GUIDE_CSS } from './guide.mjs'
import { documentHtml, esc, host, logo, phone, photo, screen, shop, tv } from '../shared.mjs'

// Section, page it starts on.
const TOC = [
  ['overview', 3], ['dashboard', 4], ['orders', 5], ['alerts', 7], ['routine', 8], ['products', 9],
  ['productForm', 10], ['productDetail', 11], ['categories', 12], ['users', 13], ['content', 14],
  ['menuBoard', 15], ['emails', 16], ['settings', 17], ['security', 18], ['help', 19]
]

// Where the numbered markers sit on the dashboard screenshot (% of the image).
const DASHBOARD_MARKERS = [[19, 18], [19, 41], [19, 61], [61, 61], [95.5, 4]]

export async function handbookDocument(lang) {
  const H = handbook[lang]
  const ar = lang === 'ar'
  const num = (n) => (ar ? String(n).replace(/\d/g, d => '٠١٢٣٤٥٦٧٨٩'[d]) : String(n).padStart(2, '0'))
  const sectionNo = (key) => TOC.findIndex(([k]) => k === key) + 1
  // **Button** → a highlighted name from the admin.
  const rich = (value, params = {}) => esc(value)
    .replace(/\{(\w+)\}/g, (_, key) => params[key] ?? `{${key}}`)
    .replace(/\*\*(.+?)\*\*/g, '<b class="ui"><bdi>$1</bdi></b>')
  const edition = new Intl.DateTimeFormat(ar ? 'ar' : 'de-DE', { month: 'long', year: 'numeric', numberingSystem: 'latn' }).format(new Date())
  const slots = { slot: shop.slotMinutes, days: shop.slotDays, pickup: shop.pickupLeadMinutes, delivery: shop.deliveryLeadMinutes }

  const browser = (name, path = '', extra = '') => `
    <figure class="frame-browser ${extra}">
      <div class="frame-bar"><i></i><i></i><i></i><span dir="ltr">${esc(host())}${esc(path)}</span></div>
      <img src="${screen(lang, name)}" alt="">
    </figure>`
  // Part of a 1440 × 900 screenshot, in CSS pixels.
  const crop = (name, path, { x, y, w, h }) => `
    <figure class="frame-browser">
      <div class="frame-bar"><i></i><i></i><i></i><span dir="ltr">${esc(host())}${esc(path)}</span></div>
      <div class="crop" style="aspect-ratio:${w}/${h}">
        <img src="${screen(lang, name)}" alt="" style="width:${(1440 / w) * 100}%;transform:translate(${-(x / 1440) * 100}%,${-(y / 900) * 100}%)">
      </div>
    </figure>`
  const list = (items, cls = 'checks') => `<ul class="${cls}">${items.map(item => `<li>${rich(item)}</li>`).join('')}</ul>`
  const defs = (items, cls = '') => `<div class="defs ${cls}">${items.map(([term, text], i) => `
    <div class="def"><span class="def-n">${num(i + 1)}</span><div><p class="def-term"><bdi>${esc(term)}</bdi></p><p>${rich(text)}</p></div></div>`).join('')}</div>`

  const shell = (n, body, { title } = {}) => `
  <div class="sheet paper">
    <header class="run">${logo('run-logo')}<span>${esc(H.runTitle)}</span></header>
    <div class="body">
      ${title ? `<div class="sec-head"><span class="sec-no">${num(sectionNo(title))}</span><h2 class="display sec-title">${esc(H.sections[title])}</h2></div>` : ''}
      ${body}
    </div>
    <footer class="run-foot"><span>${esc(H.screenshotNote)}</span><span class="page-no">${num(n)}</span></footer>
  </div>`

  const pages = []

  // 1 — Cover
  pages.push(`
  <div class="sheet dark">
    <div class="cover">
      <header class="cover-top">${logo('cover-logo')}<span class="eyebrow">${esc(H.eyebrow)}</span></header>
      <div class="cover-shots">
        ${browser('admin-dashboard', '/admin', 'cover-browser')}
        <div class="cover-phone">${phone(screen(lang, 'mobile-admin-orders'))}</div>
      </div>
      <div class="cover-copy">
        <p class="eyebrow">${esc(H.edition.replace('{date}', edition))}</p>
        <h1 class="display cover-title hb-title">${esc(H.title)}</h1>
        <p class="cover-sub">${esc(H.subtitle)}</p>
      </div>
      <footer class="cover-foot"><span>${esc(shop.name)} · ${esc(shop.street)} · ${esc(shop.city)}</span><span dir="ltr">${esc(host())}/admin</span></footer>
    </div>
  </div>`)

  // 2 — Welcome and contents
  pages.push(shell(2, `
    <div class="welcome">
      <div>
        <p class="eyebrow">${esc(H.eyebrow)}</p>
        <h1 class="display welcome-title">${esc(H.welcomeTitle)}</h1>
        ${H.welcome.map(p => `<p class="lead">${rich(p)}</p>`).join('')}
      </div>
      <div class="welcome-photo" style="background-image:url('${photo('WhatsApp Image 2025-01-17 at 17.24.35_bd8602a2.jpg')}')"></div>
    </div>
    <div class="toc toc-2">
      <p class="eyebrow">${esc(H.contents)}</p>
      <ol>${TOC.map(([key, page], i) => `<li><span class="toc-no">${num(i + 1)}</span><span class="toc-name">${esc(H.sections[key])}</span><span class="toc-dots"></span><span class="toc-page">${num(page)}</span></li>`).join('')}</ol>
    </div>`))

  // 3 — Overview
  const O = H.overview
  pages.push(shell(3, `
    <p class="lead">${rich(O.intro)}</p>
    <div class="cards cards-3 parts">
      ${O.parts.map(([title, path, text], i) => `
        <div class="card"><span class="card-n">${num(i + 1)}</span><p class="card-title">${esc(title)}</p>${path ? `<p class="path" dir="ltr">${esc(path)}</p>` : ''}<p>${esc(text)}</p></div>`).join('')}
    </div>
    <div class="access">
      <p class="card-label">${esc(O.accessTitle)}</p>
      ${O.accessLines.map(line => `<div class="write"><span>${esc(line)}</span><i></i></div>`).join('')}
      <p class="access-note">${rich(O.accessNote)}</p>
    </div>
    <p class="note">${rich(O.language)}</p>`, { title: 'overview' }))

  // 4 — Dashboard
  const D = H.dashboard
  pages.push(shell(4, `
    <p class="lead">${rich(D.intro)}</p>
    <div class="marked">
      ${browser('admin-dashboard', '/admin')}
      ${DASHBOARD_MARKERS.map(([x, y], i) => `<span class="marker" style="left:${x}%;top:calc(5mm + (100% - 5mm) * ${y / 100})">${num(i + 1)}</span>`).join('')}
    </div>
    ${defs(D.points, 'defs-2')}`, { title: 'dashboard' }))

  // 5–6 — Orders
  const R = H.orders
  pages.push(shell(5, `
    <p class="lead">${rich(R.intro)}</p>
    ${browser('admin-orders', '/admin/orders')}
    <p>${rich(R.filters)}</p>
    <div class="flow-wrap">
      <p class="card-label">${esc(R.flowTitle)}</p>
      <div class="flow">${R.flow.map(([status, text], i) => `<div class="flow-step flow-${i}"><p class="flow-status"><bdi>${esc(status)}</bdi></p><p>${esc(text)}</p></div>`).join('')}</div>
    </div>
    <p class="note">${rich(R.note)}</p>`, { title: 'orders' }))
  pages.push(shell(6, `
    <h3 class="display sub-title">${esc(R.detailTitle)}</h3>
    <p class="lead">${rich(R.detailIntro)}</p>
    ${browser('admin-order', '/admin/orders')}
    <div class="cards cards-2">
      ${R.actions.map(([title, text]) => `<div class="card"><p class="action"><bdi>${esc(title)}</bdi></p><p>${rich(text)}</p></div>`).join('')}
    </div>`))

  // 7 — New order alerts
  const A = H.alerts
  pages.push(shell(7, `
    <p class="lead">${rich(A.intro)}</p>
    ${browser('admin-new-order', '/admin/orders')}
    <div class="split">
      ${defs(A.channels, 'defs-tight')}
      <div class="phones-tip">
        <div class="mini-phones">
          ${['admin-dashboard', 'admin-orders'].map((name, i) => `<div>${phone(screen(lang, `mobile-${name}`))}<p><bdi>${esc(A.phoneLabels[i])}</bdi></p></div>`).join('')}
        </div>
        <p class="card-label">${esc(A.tipTitle)}</p>
        <p>${rich(A.tip)}</p>
      </div>
    </div>`, { title: 'alerts' }))

  // 8 — Daily routine
  const T = H.routine
  pages.push(shell(8, `
    <p class="lead">${rich(T.intro)}</p>
    <div class="day">${T.day.map(([when, text], i) => `<div class="day-step"><span class="day-dot">${num(i + 1)}</span><p class="card-title">${esc(when)}</p><p>${rich(text)}</p></div>`).join('')}</div>
    <h3 class="display sub-title">${esc(T.rulesTitle)}</h3>
    <div class="split split-shot">
      ${defs(T.rules.map(([term, text]) => [term, text.replace(/\{(\w+)\}/g, (_, k) => slots[k])]), 'defs-tight')}
      <div>${browser('checkout-time', '/checkout')}</div>
    </div>`, { title: 'routine' }))

  // 9 — Products
  const P = H.products
  pages.push(shell(9, `
    <p class="lead">${rich(P.intro)}</p>
    ${browser('admin-products', '/admin/products')}
    ${defs(P.points, 'defs-3')}
    <div class="dark-box">
      <p class="card-label">${esc(P.visibleTitle)}</p>
      ${list(P.visible, 'checks checks-row')}
      <p>${rich(P.visibleNote)}</p>
    </div>`, { title: 'products' }))

  // 10 — Product form
  const F = H.productForm
  pages.push(shell(10, `
    <p class="lead">${rich(F.intro)}</p>
    <div class="form-split">
      <div>${crop('admin-product-form', '/admin/products', { x: 395, y: 20, w: 680, h: 880 })}</div>
      ${defs(F.fields, 'defs-tight')}
    </div>
    <div class="tip">
      <img class="tip-photo" src="${photo('croissant-butter.png')}" alt="">
      <div><p class="card-label">${esc(F.photoTitle)}</p>${list(F.photo, 'checks checks-2')}</div>
    </div>`, { title: 'productForm' }))

  // 11 — Product detail, stock, allergens
  const PD = H.productDetail
  pages.push(shell(11, `
    <p class="lead">${rich(PD.intro)}</p>
    ${crop('admin-product-detail', '/admin/products/…', { x: 0, y: 0, w: 1440, h: 640 })}
    <div class="cards cards-2 equal">
      <div class="card"><p class="card-title">${esc(PD.stockTitle)}</p><p>${rich(PD.stock)}</p></div>
      <div class="card"><p class="card-title">${esc(PD.allergenTitle)}</p><p>${rich(PD.allergenIntro)}</p>${list(PD.allergenSteps, 'steps')}</div>
    </div>
    <p class="note">${rich(PD.allergenNote)}</p>`, { title: 'productDetail' }))

  // 12 — Categories
  const C = H.categories
  pages.push(shell(12, `
    <p class="lead">${rich(C.intro)}</p>
    ${browser('admin-categories', '/admin/categories')}
    <div class="split split-even">
      <div>${crop('admin-category-form', '/admin/categories', { x: 300, y: 180, w: 1105, h: 590 })}</div>
      ${defs(C.points, 'defs-tight')}
    </div>`, { title: 'categories' }))

  // 13 — Users
  const U = H.users
  pages.push(shell(13, `
    <p class="lead">${rich(U.intro)}</p>
    ${browser('admin-users', '/admin/users')}
    ${defs(U.points, 'defs-3')}
    <div class="dark-box">
      <p class="card-label">${esc(U.teamTitle)}</p>
      ${list(U.team)}
    </div>`, { title: 'users' }))

  // 14 — Journal, messages, newsletter (Django admin)
  const N = H.content
  const djangoPath = '/django-admin/content/'
  pages.push(shell(14, `
    <p class="lead">${rich(N.intro)}</p>
    <div class="django">
      ${[['admin-django-posts', 'post/'], ['admin-django-post-form', 'post/add/'], ['admin-django-messages', 'contactmessage/'], ['admin-django-newsletter', 'newslettersubscriber/']]
        .map(([name, path]) => crop(name, djangoPath + path, { x: 0, y: 0, w: 1440, h: 620 })).join('')}
    </div>
    <div class="cols-3">
      <div><p class="card-title">${esc(N.postsTitle)}</p>${list(N.posts, 'steps')}</div>
      <div><p class="card-title">${esc(N.messagesTitle)}</p><p>${rich(N.messages)}</p></div>
      <div><p class="card-title">${esc(N.newsletterTitle)}</p><p>${rich(N.newsletter)}</p></div>
    </div>`, { title: 'content' }))

  // 15 — Menu board
  const M = H.menuBoard
  pages.push(shell(15, `
    <p class="lead">${rich(M.intro)}</p>
    <div class="tv-wrap">${tv(screen(lang, 'menu-board'))}</div>
    <div class="split split-even">
      <div>
        ${list(M.features)}
        <p class="card-label opt-label">${esc(M.optionsTitle)}</p>
        <table class="opts">${M.options.map(([code, text]) => `<tr><td dir="ltr"><code>${esc(code)}</code></td><td>${esc(text)}</td></tr>`).join('')}</table>
      </div>
      <div>
        <p class="card-label">${esc(M.setupTitle)}</p>
        ${defs(M.setup, 'defs-tight')}
        <p class="note">${rich(M.tip)}</p>
      </div>
    </div>`, { title: 'menuBoard' }))

  // 16 — Emails
  const E = H.emails
  pages.push(shell(16, `
    <p class="lead">${rich(E.intro)}</p>
    <div class="mails">
      <figure><img src="${screen(lang, 'admin-email-customer')}" alt=""><figcaption>${esc(E.customer)}</figcaption></figure>
      <figure><img src="${screen(lang, 'admin-email-shop')}" alt=""><figcaption>${esc(E.shop)}</figcaption></figure>
    </div>
    ${defs(E.list, 'defs-3')}`, { title: 'emails' }))

  // 17 — Settings and Stripe
  const G = H.settings
  pages.push(shell(17, `
    <p class="lead">${rich(G.intro)}</p>
    <table class="settings">
      <thead><tr>${G.head.map(h => `<th>${esc(h)}</th>`).join('')}</tr></thead>
      <tbody>${G.rows.map(([key, text, example]) => `<tr><td dir="ltr"><code>${esc(key)}</code></td><td>${esc(text)}</td><td dir="ltr"><code>${esc(example)}</code></td></tr>`).join('')}</tbody>
    </table>
    <div class="dark-box">
      <p class="card-label">${esc(G.stripeTitle)}</p>
      ${list(G.stripe, 'steps')}
      <p>${rich(G.stripeNote)}</p>
    </div>`, { title: 'settings' }))

  // 18 — Security
  pages.push(shell(18, `
    <div class="cards cards-2 security">
      ${H.security.items.map(([title, text], i) => `<div class="card card-icon"><span class="card-n">${num(i + 1)}</span><p class="card-title">${esc(title)}</p><p>${rich(text)}</p></div>`).join('')}
    </div>
    <div class="photo-band" style="background-image:url('${photo('WhatsApp Image 2025-01-17 at 17.24.35_bd8602a2.jpg')}')"></div>`, { title: 'security' }))

  // 19 — Help and checklists
  const X = H.help
  pages.push(shell(19, `
    <p class="card-label">${esc(X.problemsTitle)}</p>
    <table class="problems">${X.problems.map(([problem, fix]) => `<tr><th>${esc(problem)}</th><td>${rich(fix)}</td></tr>`).join('')}</table>
    <div class="split split-even">
      <div class="checklist"><p class="card-label">${esc(X.checklistTitle)}</p>${list(X.checklist, 'boxes')}</div>
      <div class="checklist"><p class="card-label">${esc(X.weeklyTitle)}</p>${list(X.weekly, 'boxes')}</div>
    </div>`, { title: 'help' }))

  // 20 — Back cover
  const B = H.back
  pages.push(`
  <div class="sheet dark">
    <div class="cover back">
      ${logo('cover-logo')}
      <h2 class="display back-title">${esc(B.title)}</h2>
      <img class="cutout bk-a" src="${photo('croissant-butter.png')}" alt="">
      <img class="cutout bk-b" src="${photo('cuppchtino.png')}" alt="">
      <div class="contact">
        <p class="eyebrow">${esc(B.contactTitle)}</p>
        ${B.contactLines.map(line => `<div class="write write-dark"><span>${esc(line)}</span><i></i></div>`).join('')}
      </div>
      <p class="back-small" dir="ltr">${esc(host())}/admin · ${esc(host())}/menu-board</p>
    </div>
  </div>`)

  return documentHtml({ lang, title: `${H.title} – Backlover`, width: '210mm', height: '297mm', pages, css: GUIDE_CSS + CSS })
}

const CSS = `
  .ui { font-weight: 700; color: var(--ink); }
  .dark .ui, .dark-box .ui, .tip-dark .ui { color: var(--cream); }
  .sub-title { font-size: 18pt; }
  [lang="ar"] .sub-title { font-size: 15pt; }
  .note { padding: 4mm 5mm; border-radius: 3mm; background: rgba(230, 161, 90, 0.16); font-size: 8.8pt; line-height: 1.6; }
  .body > .frame-browser, .body > .marked { flex: none; }

  /* Cover */
  .cover-shots { position: relative; margin-top: 16mm; height: 120mm; }
  .cover-browser { width: 150mm; transform: perspective(600mm) rotateY(-8deg) rotate(-1.5deg); transform-origin: left center; }
  [dir="rtl"] .cover-browser { transform: perspective(600mm) rotateY(8deg) rotate(1.5deg); transform-origin: right center; }
  .cover-phone { position: absolute; width: 40mm; top: 22mm; inset-inline-end: 0; transform: rotate(5deg); }
  [dir="rtl"] .cover-phone { transform: rotate(-5deg); }
  .hb-title { font-size: 46pt; max-width: 165mm; }
  [lang="ar"] .hb-title { font-size: 38pt; }

  /* Contents in two columns */
  .toc-2 ol { grid-template-columns: 1fr 1fr; column-gap: 10mm; grid-auto-flow: column; grid-template-rows: repeat(8, auto); }
  .toc-2 li { font-size: 9.2pt; }

  /* Overview */
  .parts .card { padding-top: 4mm; }
  .parts .card-n { font-size: 16pt; }
  .path { margin-bottom: 1mm; font: 600 8pt ui-monospace, Menlo, monospace; color: var(--crust); }
  .access { padding: 6mm 7mm; border-radius: 4mm; background: var(--oven); color: var(--cream); }
  .access .card-label { color: var(--gold); margin-bottom: 3mm; }
  .write { display: flex; align-items: flex-end; gap: 4mm; margin-bottom: 4mm; font-size: 8.5pt; color: var(--cream-muted); }
  .write span { flex: none; width: 55mm; }
  .write i { flex: 1; border-bottom: 0.3mm dashed rgba(244, 236, 225, 0.35); height: 6mm; }
  .access-note { margin-top: 2mm; color: var(--cream-muted); }
  .access .ui { color: var(--cream); }

  /* Numbered definitions */
  .defs { display: grid; gap: 3.5mm 7mm; }
  .defs-2 { grid-template-columns: 1fr 1fr; }
  .defs-3 { grid-template-columns: repeat(3, 1fr); }
  .defs-tight { gap: 2.6mm; align-content: start; }
  .def { display: flex; gap: 3mm; align-items: flex-start; }
  .def-n { flex: none; width: 6.5mm; height: 6.5mm; display: grid; place-items: center; border-radius: 50%; background: var(--crust); color: #fff; font: 700 7.5pt var(--sans); }
  .def-term { font-size: 9.4pt; font-weight: 700; color: var(--ink); margin-bottom: 0.4mm; }
  .def p { line-height: 1.5; }

  /* Dashboard markers */
  .marked { position: relative; }
  .marker { position: absolute; width: 8mm; height: 8mm; margin: -4mm 0 0 -4mm; display: grid; place-items: center; border-radius: 50%;
    background: var(--crust); color: #fff; font: 700 9pt var(--sans); box-shadow: 0 0 0 1.2mm rgba(230, 161, 90, 0.35), 0 1mm 2mm rgba(0, 0, 0, 0.4); }
  [dir="rtl"] .marker { margin: -4mm -4mm 0 0; }

  /* Order flow */
  .flow { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm; }
  .flow-step { position: relative; padding: 3.5mm 4mm; border-radius: 3mm; background: rgba(255, 255, 255, 0.55); border: 0.25mm solid var(--line); }
  .flow-status { font-weight: 800; font-size: 9.5pt; margin-bottom: 0.5mm; }
  .flow-0 .flow-status { color: #b7791f; }
  .flow-1 .flow-status { color: #2b6cb0; }
  .flow-2 .flow-status { color: var(--green); }
  .flow-3 .flow-status { color: var(--ember); }
  .flow-step:not(:nth-child(3)):not(:last-child)::after { content: '→'; position: absolute; inset-inline-end: -3mm; top: 50%; transform: translate(50%, -50%); color: var(--crust); font-weight: 800; z-index: 1; }
  [dir="rtl"] .flow-step::after { content: '←' !important; }
  .flow-wrap .card-label { margin-bottom: 2.5mm; }
  .action { font-weight: 800; color: var(--crust); margin-bottom: 1mm; font-size: 9.6pt; }

  /* Split layouts */
  .split { display: grid; grid-template-columns: 1fr 70mm; gap: 7mm; align-items: start; }
  .split-shot { grid-template-columns: 1fr 82mm; }
  .split-even { grid-template-columns: 1fr 1fr; }
  .phones-tip p { font-size: 8pt; }
  .phones-tip { padding: 4mm 5mm; border-radius: 4mm; background: rgba(230, 161, 90, 0.16); }
  .mini-phones { display: grid; grid-template-columns: 20mm 20mm; justify-content: center; gap: 6mm; margin-bottom: 2.5mm; text-align: center; }
  .mini-phones .frame-phone { border-radius: 4mm; padding: 1.1mm; }
  .mini-phones .frame-phone img { border-radius: 3mm; }
  .mini-phones .frame-phone::before { width: 6mm; height: 1.5mm; margin-left: -3mm; top: 1.8mm; }
  .mini-phones p { margin-top: 2mm; font-weight: 700; color: var(--ink); font-size: 8pt; }

  /* Daily routine */
  .day { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; position: relative; }
  .day::before { content: ''; position: absolute; top: 4mm; left: 4mm; right: 4mm; height: 0.4mm; background: var(--line); }
  .day-step { position: relative; }
  .day-dot { position: relative; display: grid; place-items: center; width: 8mm; height: 8mm; border-radius: 50%; background: var(--oven); color: var(--gold); font: 700 8.5pt var(--sans); margin-bottom: 3mm; }

  /* Boxes and lists */
  .dark-box { padding: 6mm 7mm; border-radius: 4mm; background: var(--oven); color: var(--cream); margin-top: auto; }
  .dark-box p { color: var(--cream-muted); }
  .dark-box .card-label { color: var(--gold); margin-bottom: 3mm; }
  .checks, .steps, .boxes { list-style: none; display: grid; gap: 2mm; }
  .checks li, .steps li, .boxes li { position: relative; padding-inline-start: 6mm; font-size: 8.8pt; line-height: 1.5; color: var(--ink-2); }
  .dark-box .checks li, .dark-box .steps li { color: var(--cream-muted); }
  .checks li::before { content: '✓'; position: absolute; inset-inline-start: 0; color: var(--crust); font-weight: 800; }
  .dark-box .checks li::before { color: var(--crust-light); }
  .checks-row { grid-template-columns: repeat(3, auto); justify-content: start; gap: 2mm 9mm; margin-bottom: 3mm; }
  .checks-row li { color: var(--cream); font-weight: 600; }
  .checks-2 { grid-template-columns: 1fr 1fr; gap: 1.5mm 6mm; }
  .steps { counter-reset: step; margin-top: 2mm; }
  .steps li { counter-increment: step; padding-inline-start: 7mm; }
  .steps li::before { content: counter(step); position: absolute; inset-inline-start: 0; top: 0.3mm; width: 4.6mm; height: 4.6mm; display: grid; place-items: center;
    border-radius: 50%; background: var(--crust); color: #fff; font: 700 6.5pt var(--sans); }
  .dark-box .steps li { margin-bottom: 0.5mm; }
  .dark-box .steps + p { margin-top: 3mm; }
  .boxes li { padding-inline-start: 8mm; }
  .boxes li::before { content: ''; position: absolute; inset-inline-start: 0; top: 0.5mm; width: 4mm; height: 4mm; border: 0.35mm solid var(--crust); border-radius: 1mm; }

  /* Product form */
  .form-split { display: grid; grid-template-columns: 80mm 1fr; gap: 7mm; align-items: start; }
  .crop { position: relative; overflow: hidden; direction: ltr; }
  .crop img { display: block; max-width: none; }
  .tip-photo { width: 30mm; flex: none; filter: drop-shadow(0 2mm 3mm rgba(40, 22, 8, 0.3)); }
  .equal { align-items: stretch; }

  /* Django admin */
  .django { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }
  .cols-3 { display: grid; grid-template-columns: 1.15fr 1fr 1fr; gap: 7mm; }
  .cols-3 .card-title { margin-bottom: 1.5mm; }

  /* Menu board */
  .tv-wrap { padding: 0 14mm 7mm; }
  .opt-label { margin-top: 4mm; }
  .opts { width: 100%; border-collapse: collapse; font-size: 8.4pt; }
  .opts td { padding: 1.4mm 0; border-bottom: 0.25mm solid var(--line); vertical-align: top; color: var(--ink-2); }
  .opts td:first-child { width: 46mm; padding-inline-end: 3mm; }
  code { font: 600 7.6pt ui-monospace, Menlo, monospace; color: var(--crust); }

  /* Emails */
  .mails { display: grid; grid-template-columns: 1fr 1fr; gap: 8mm; padding: 0 6mm; }
  .mails img { width: 100%; border-radius: 3mm; box-shadow: 0 2.5mm 6mm rgba(29, 23, 18, 0.25); }
  .mails figcaption { margin-top: 2.5mm; text-align: center; font-size: 8.5pt; font-weight: 700; }

  /* Settings */
  .settings { width: 100%; border-collapse: collapse; font-size: 8.2pt; }
  .settings th { text-align: start; padding: 0 0 2mm; font-size: 7pt; letter-spacing: 0.12em; text-transform: uppercase; color: var(--crust); border-bottom: 0.35mm solid var(--line); }
  [lang="ar"] .settings th { letter-spacing: 0; font-size: 8.5pt; }
  .settings td { padding: 2mm 3mm 2mm 0; border-bottom: 0.25mm solid var(--line); vertical-align: top; color: var(--ink-2); }
  [dir="rtl"] .settings td { padding: 2mm 0 2mm 3mm; }
  .settings td:first-child { width: 62mm; }
  .settings td:last-child { width: 52mm; }
  .settings code { font-size: 7pt; }
  .settings td[dir="ltr"] { text-align: left; }

  /* Security */
  .security .card { padding: 6mm; }
  .security p { font-size: 9.2pt; }
  .photo-band { margin-top: auto; flex: 1; min-height: 40mm; max-height: 70mm; border-radius: 4mm; background-size: cover; background-position: center 45%; }

  /* Help */
  .problems { width: 100%; border-collapse: collapse; }
  .problems th, .problems td { padding: 2.6mm 0; border-bottom: 0.25mm solid var(--line); vertical-align: top; font-size: 9pt; line-height: 1.5; text-align: start; }
  .problems th { width: 66mm; padding-inline-end: 6mm; color: var(--ink); }
  .problems td { color: var(--ink-2); }
  .checklist { padding: 6mm; border-radius: 4mm; border: 0.3mm solid var(--line); background: rgba(255, 255, 255, 0.5); }
  .checklist .card-label { margin-bottom: 3mm; }

  /* Back cover */
  .contact { margin-top: auto; width: 110mm; position: relative; }
  .contact .eyebrow { margin-bottom: 4mm; }
  .write-dark { font-size: 9pt; }
  .write-dark span { width: 22mm; }
  .back-small { margin-top: 10mm; font-size: 8pt; }
  [lang="ar"] .def-term, [lang="ar"] .card-title { font-size: 10pt; }
  [lang="ar"] p, [lang="ar"] li { line-height: 1.7; }
`
