// The printed menu: A4 portrait, two pages, with 3 mm bleed on every side
// (216 × 303 mm) for the print shop.
import menu from '../data/menu.mjs'
import { addressLines, documentHtml, esc, hoursList, host, logo, photo, price, qr, shopUrl, text } from '../shared.mjs'

const tag = (item, lang) => {
  if (item.tags?.includes('vegan')) return `<span class="diet is-vegan" title="${text(lang, 'vegan')}">VG</span>`
  if (item.tags?.includes('vegetarian')) return `<span class="diet" title="${text(lang, 'vegetarian')}">V</span>`
  return ''
}

const item = (it, lang) => `
  <div class="item">
    <div class="item-img"><img src="${photo(it.image)}" alt=""></div>
    <div class="item-text">
      <div class="item-line">
        <span class="item-name">${esc(it.name[lang])}</span>${tag(it, lang)}
        <span class="item-dots"></span>
        <span class="item-price">${price(it.price, lang)}</span>
      </div>
      <p class="item-desc">${esc(it.desc[lang])}</p>
    </div>
  </div>`

const section = (key, lang) => {
  const s = menu.find(sec => sec.key === key)
  return `
  <section class="section">
    <h2 class="display section-title">${esc(s.title[lang])}</h2>
    <p class="section-note">${esc(s.note[lang])}</p>
    <div class="section-items">${s.items.map(it => item(it, lang)).join('')}</div>
  </section>`
}

export async function menuDocument(lang) {
  const t = (path, params) => text(lang, path, params)
  const code = await qr(shopUrl('/products'))

  const front = `
  <div class="sheet paper">
    <div class="safe">
      <header class="hero">
        <div class="hero-text">
          <p class="eyebrow">${t('bakery')} · ${t('placeLine')}</p>
          ${logo('hero-logo')}
          <p class="display hero-title"><i>${t('menu.title')}</i></p>
          <p class="hero-intro">${t('menu.intro')}</p>
        </div>
        <img class="cutout hero-a" src="${photo('croissant-butter.png')}" alt="">
        <img class="cutout hero-b" src="${photo('pretzel.png')}" alt="">
        <img class="cutout hero-c" src="${photo('macarons.png')}" alt="">
      </header>
      <div class="ornament"><span></span><i>✦</i><span></span></div>
      <div class="columns">
        ${section('pastries', lang)}
        ${section('savoury', lang)}
      </div>
      <div class="band">
        <div class="band-photo" style="background-image:url('${photo('WhatsApp Image 2025-01-17 at 17.24.35_bd8602a2.jpg')}')"></div>
        <div class="band-text">
          <p class="eyebrow">${t('web')}</p>
          <p class="display band-title">${t('scanToOrder')}</p>
          <p class="band-url" dir="ltr">${esc(host())}</p>
        </div>
        <div class="qr qr-card band-qr">${code}</div>
      </div>
    </div>
  </div>`

  const back = `
  <div class="sheet paper">
    <div class="safe">
      <header class="mini">
        ${logo('mini-logo')}
        <span class="display mini-title"><i>${t('menu.title')}</i></span>
      </header>
      <div class="columns columns-tall">
        ${section('sweets', lang)}
        ${section('drinks', lang)}
      </div>
      <footer class="info">
        <div class="info-col">
          <p class="eyebrow">${t('hours')}</p>
          <div class="info-hours">${hoursList(lang)}</div>
        </div>
        <div class="info-col">
          <p class="eyebrow">${t('address')}</p>
          <p>${addressLines(lang).join('<br>')}</p>
          <p class="info-pay">${t('menu.paymentLine')}</p>
        </div>
        <div class="info-col info-qr">
          <div class="qr qr-card">${code}</div>
          <p dir="ltr">${esc(host())}</p>
        </div>
        <div class="info-notes">
          <span><span class="diet is-vegan">VG</span> ${t('vegan')}</span>
          <span><span class="diet">V</span> ${t('vegetarian')}</span>
          <span>${t('allergenNote')}</span>
          <span>${t('vatNote')}</span>
        </div>
      </footer>
    </div>
  </div>`

  return documentHtml({
    lang,
    title: `${t('menu.title')} – Backlover`,
    width: '216mm',
    height: '303mm',
    pages: [front, back],
    css: CSS
  })
}

const CSS = `
  .safe { position: absolute; inset: 15mm 15mm 14mm; display: flex; flex-direction: column; }

  /* Front: header */
  .hero { position: relative; height: 84mm; }
  .hero-text { position: relative; z-index: 1; width: 104mm; padding-top: 2mm; }
  .hero-logo { display: block; margin-top: 4mm; font-size: 58pt; }
  .hero-title { margin-top: 1mm; font-size: 30pt; color: var(--crust); }
  [lang="ar"] .hero-title i { font-style: normal; }
  .hero-intro { margin-top: 4mm; font-size: 9.5pt; line-height: 1.55; color: var(--ink-2); }
  .hero-a { width: 78mm; top: 2mm; inset-inline-end: -4mm; transform: rotate(-8deg); }
  .hero-b { width: 46mm; top: 46mm; inset-inline-end: 52mm; transform: rotate(10deg); }
  .hero-c { width: 30mm; top: 54mm; inset-inline-end: 4mm; transform: rotate(-4deg); }
  [dir="rtl"] .hero-a { transform: rotate(8deg) scaleX(-1); }

  .ornament { display: flex; align-items: center; gap: 4mm; margin: 2mm 0 6mm; color: var(--crust); font-size: 8pt; }
  .ornament span { flex: 1; height: 0.25mm; background: var(--line); }

  /* Sections */
  .columns { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 0 10mm; margin-bottom: 9mm; }
  .columns-tall { margin-top: 8mm; }
  .section { display: flex; flex-direction: column; }
  .section-title { font-size: 25pt; }
  .section-note { margin-top: 1mm; font-size: 8pt; font-style: italic; color: var(--muted); }
  [lang="ar"] .section-note { font-style: normal; }
  .section-items { flex: 1; margin-top: 5mm; display: flex; flex-direction: column; justify-content: space-around; gap: 3mm; }
  .item { display: flex; align-items: center; gap: 3.5mm; }
  .item-img { flex: none; display: grid; place-items: center; width: 23mm; height: 23mm; border-radius: 50%;
    background: radial-gradient(closest-side, rgba(230, 161, 90, 0.28), rgba(230, 161, 90, 0.06) 70%, transparent); }
  .item-img img { width: 21mm; height: 21mm; object-fit: contain; filter: drop-shadow(0 1.2mm 1.4mm rgba(40, 22, 8, 0.3)); }
  .item-text { flex: 1; min-width: 0; }
  .item-line { display: flex; align-items: baseline; gap: 1.5mm; }
  .item-name { font-size: 11.5pt; font-weight: 700; white-space: nowrap; }
  .item-dots { flex: 1; min-width: 3mm; border-bottom: 0.35mm dotted rgba(29, 23, 18, 0.3); transform: translateY(-0.8mm); }
  .item-price { font-size: 11.5pt; font-weight: 700; color: var(--crust); }
  .item-desc { margin-top: 1mm; font-size: 8.2pt; line-height: 1.4; color: var(--muted); }
  .diet { display: inline-grid; place-items: center; min-width: 4.2mm; height: 4.2mm; padding: 0 0.6mm; border-radius: 2.1mm;
    border: 0.25mm solid var(--green); color: var(--green); font: 700 5.4pt var(--sans); vertical-align: 0.4mm; }
  .diet.is-vegan { background: var(--green); color: #fff; }

  /* Front: bottom band */
  .band { margin-top: auto; display: flex; align-items: stretch; height: 52mm; border-radius: 5mm; overflow: hidden; background: var(--oven); color: var(--cream); }
  .band-photo { width: 74mm; background-size: cover; background-position: center 40%; }
  .band-text { flex: 1; padding: 8mm 7mm; display: flex; flex-direction: column; justify-content: center; }
  .band-text .eyebrow { color: var(--crust-light); }
  .band-title { margin-top: 2mm; font-size: 19pt; line-height: 1.1; }
  .band-url { margin-top: 3mm; font-size: 9pt; font-weight: 600; color: var(--gold); }
  .band-qr { align-self: center; width: 34mm; height: 34mm; margin-inline-end: 7mm; }

  /* Back */
  .mini { display: flex; align-items: baseline; justify-content: space-between; padding-bottom: 4mm; border-bottom: 0.25mm solid var(--line); }
  .mini-logo { font-size: 26pt; }
  .mini-title { font-size: 16pt; color: var(--crust); }
  [lang="ar"] .mini-title i { font-style: normal; }
  .info { display: grid; grid-template-columns: 1.15fr 1.25fr 0.8fr; gap: 4mm 8mm; padding: 7mm 8mm 6mm; border-radius: 5mm;
    background: var(--oven); color: var(--cream); font-size: 8.4pt; line-height: 1.55; }
  .info .eyebrow { margin-bottom: 2mm; color: var(--crust-light); }
  .info-hours { display: grid; gap: 0.8mm; }
  .info-pay { margin-top: 2mm; color: var(--cream-muted); font-size: 7.6pt; }
  .info-qr { display: grid; justify-items: center; align-content: start; gap: 2mm; font-size: 7.6pt; font-weight: 600; color: var(--gold); }
  .info-qr .qr { width: 26mm; height: 26mm; }
  .info-notes { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 1.5mm 5mm; padding-top: 3mm; border-top: 0.25mm solid rgba(244, 236, 225, 0.15);
    font-size: 6.8pt; color: var(--cream-muted); }
  .info-notes .diet { border-color: #9fd49a; color: #9fd49a; }
  .info-notes .diet.is-vegan { background: #9fd49a; color: var(--oven); }
  [lang="ar"] .item-name, [lang="ar"] .item-price { font-size: 12.5pt; }
  [lang="ar"] .item-desc { font-size: 9pt; }
  [lang="ar"] .hero-intro { font-size: 10.5pt; }
  [lang="ar"] .section-note { font-size: 9pt; }
  [lang="ar"] .info { font-size: 9pt; }
`
