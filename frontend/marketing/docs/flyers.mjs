// Flyer (A5), breakfast postcard (A6), window poster (A3) and social posts.
// Print sizes include 3 mm bleed on every side.
import offers from '../data/offers.mjs'
import { addressLines, documentHtml, esc, hoursList, host, logo, phone, photo, price, qr, screen, shop, shopUrl, text } from '../shared.mjs'

const lines = (parts, accent = 1) => parts
  .map((part, i) => (i === accent ? `<span class="accent">${esc(part)}</span>` : esc(part)))
  .join('<br>')

// ---------------------------------------------------------------------------
// A5 flyer: "order ahead online"
// ---------------------------------------------------------------------------
export async function flyerDocument(lang) {
  const t = (path, params) => text(lang, path, params)
  const code = await qr(shopUrl('/products'))
  const fee = price(shop.deliveryFee, lang)

  const front = `
  <div class="sheet dark">
    <div class="safe">
      <header class="f-top">${logo('f-logo')}<span class="eyebrow">${t('bakery')} · ${t('placeLine')}</span></header>
      <img class="cutout f-a" src="${photo('croissant-chocolate.png')}" alt="">
      <img class="cutout f-b" src="${photo('donut-caramel.png')}" alt="">
      <img class="cutout f-c" src="${photo('pretzel.png')}" alt="">
      <div class="f-copy">
        <span class="badge">${t('flyer.badge')}</span>
        <h1 class="display f-head">${lines(t('flyer.headline'))}</h1>
        <p class="f-sub">${t('flyer.sub')}</p>
      </div>
      <footer class="f-cta">
        <div class="qr qr-card f-qr">${code}</div>
        <div><p class="f-cta-title">${t('scanToOrder')}</p><p class="f-url" dir="ltr">${esc(host())}</p></div>
      </footer>
    </div>
  </div>`

  const back = `
  <div class="sheet paper">
    <div class="safe">
      <p class="eyebrow">${t('web')}</p>
      <h2 class="display b-title">${t('flyer.stepsTitle')}</h2>
      <div class="b-body">
        <ol class="steps">
          ${t('flyer.steps').map(([title, body], i) => `
            <li><span class="step-n">${i + 1}</span><div><strong>${esc(title)}</strong><p>${esc(body)}</p></div></li>`).join('')}
        </ol>
        <div class="b-phone">${phone(screen(lang, 'mobile-shop'))}</div>
      </div>
      <ul class="perks">${t('flyer.perks').map(p => `<li><span>✓</span>${esc(p)}</li>`).join('')}</ul>
      <footer class="b-info">
        <div><p class="eyebrow">${t('hours')}</p><div class="b-hours">${hoursList(lang)}</div></div>
        <div><p class="eyebrow">${t('address')}</p><p>${addressLines(lang).join('<br>')}</p><p class="b-fee">${t('flyer.deliveryLine', { fee })}</p></div>
      </footer>
    </div>
  </div>`

  return documentHtml({ lang, title: 'Flyer A5 – Backlover', width: '154mm', height: '216mm', pages: [front, back], css: FLYER_CSS })
}

const FLYER_CSS = `
  .safe { position: absolute; inset: 11mm 11mm 10mm; display: flex; flex-direction: column; }
  .accent { color: var(--crust-light); font-style: italic; }
  [lang="ar"] .accent { font-style: normal; }
  .paper .accent { color: var(--crust); }
  .badge { display: inline-block; padding: 1.2mm 3.4mm; border-radius: 9mm; background: var(--crust-light); color: var(--oven); font-size: 7.5pt; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; }
  [lang="ar"] .badge { letter-spacing: 0; font-size: 9pt; }

  .f-top { display: flex; align-items: baseline; justify-content: space-between; }
  .f-logo { font-size: 26pt; }
  .f-a { width: 90mm; top: 14mm; inset-inline-end: -18mm; transform: rotate(-10deg); }
  .f-b { width: 42mm; top: 50mm; inset-inline-end: 50mm; transform: rotate(6deg); }
  .f-c { width: 36mm; top: 72mm; inset-inline-end: 0; transform: rotate(-12deg); }
  [dir="rtl"] .f-a { transform: rotate(10deg) scaleX(-1); }
  .f-copy { position: relative; margin-top: auto; }
  .f-head { margin-top: 4mm; font-size: 40pt; }
  [lang="ar"] .f-head { font-size: 34pt; }
  .f-sub { margin-top: 4mm; max-width: 108mm; font-size: 9.6pt; line-height: 1.55; color: var(--cream-muted); }
  [lang="ar"] .f-sub { font-size: 10.5pt; }
  .f-cta { display: flex; align-items: center; gap: 5mm; margin-top: 7mm; padding-top: 6mm; border-top: 0.25mm solid rgba(244, 236, 225, 0.15); }
  .f-qr { width: 25mm; height: 25mm; flex: none; }
  .f-cta-title { font-size: 11pt; font-weight: 700; }
  .f-url { margin-top: 1mm; font-size: 9pt; font-weight: 600; color: var(--gold); }

  .b-title { margin-top: 2mm; font-size: 32pt; }
  .b-body { flex: 1; display: grid; grid-template-columns: 1fr 48mm; gap: 7mm; margin-top: 6mm; align-items: center; }
  .steps { list-style: none; display: grid; gap: 9mm; }
  .steps li { display: flex; gap: 3.5mm; }
  .step-n { flex: none; display: grid; place-items: center; width: 9mm; height: 9mm; border-radius: 50%; background: var(--oven); color: var(--crust-light);
    font: 400 15pt var(--display); }
  .steps strong { font-size: 11pt; }
  [lang="ar"] .steps strong { font-size: 12pt; }
  .steps p { margin-top: 1mm; font-size: 8.4pt; line-height: 1.5; color: var(--ink-2); }
  [lang="ar"] .steps p { font-size: 9.2pt; }
  .b-phone { transform: rotate(3deg); }
  [dir="rtl"] .b-phone { transform: rotate(-3deg); }
  .perks { list-style: none; display: flex; flex-wrap: wrap; gap: 2mm; margin: 6mm 0; }
  .perks li { display: flex; align-items: center; gap: 1.5mm; padding: 1.4mm 3mm; border-radius: 9mm; background: var(--paper-2); font-size: 7.8pt; font-weight: 600; }
  .perks span { color: var(--green); font-weight: 800; }
  .b-info { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; padding: 6mm; border-radius: 4mm; background: var(--oven); color: var(--cream);
    font-size: 8pt; line-height: 1.6; }
  [lang="ar"] .b-info { font-size: 8.8pt; }
  .b-info .eyebrow { margin-bottom: 1.5mm; color: var(--crust-light); }
  .b-hours { display: grid; gap: 0.5mm; }
  .b-fee { margin-top: 1.5mm; color: var(--gold); font-weight: 600; }
`

// ---------------------------------------------------------------------------
// A6 postcard: breakfast offer
// ---------------------------------------------------------------------------
export async function postcardDocument(lang) {
  const t = (path, params) => text(lang, path, params)
  const offer = offers.breakfast
  const code = await qr(shopUrl('/products'), { dark: '#f4ece1' })

  const front = `
  <div class="sheet warm">
    <div class="safe">
      <header class="p-top">${logo('p-logo')}<span class="eyebrow">${t('breakfast.kicker')}</span></header>
      <img class="cutout p-cup" src="${photo('cuppchtino.png')}" alt="">
      <img class="cutout p-croissant" src="${photo('croissant-butter.png')}" alt="">
      <div class="p-offer">
        <span class="p-offer-label">${t('breakfast.offerLabel')}</span>
        <span class="p-offer-price">${price(offer.price, lang)}</span>
        <span class="p-offer-items">${esc(offer.items[lang])}</span>
      </div>
      <div class="p-copy">
        <h1 class="display p-head">${esc(t('breakfast.headline'))}</h1>
        <p class="p-sub">${t('breakfast.sub')}</p>
      </div>
    </div>
  </div>`

  const back = `
  <div class="sheet dark">
    <div class="safe">
      ${logo('p-logo')}
      <h2 class="display pb-title">${t('breakfast.backTitle')}</h2>
      <p class="pb-text">${t('breakfast.backText')}</p>
      <div class="pb-when"><strong>${esc(offer.items[lang])} · ${price(offer.price, lang)}</strong><span>${esc(offer.when[lang])}</span></div>
      <div class="pb-bottom">
        <div class="qr pb-qr">${code}</div>
        <div class="pb-info">
          <p class="pb-url" dir="ltr">${esc(host())}</p>
          <p>${addressLines(lang).join('<br>')}</p>
        </div>
      </div>
      <p class="pb-small">${t('breakfast.showCard')} ${t('vatNote')}</p>
    </div>
  </div>`

  return documentHtml({ lang, title: 'Postkarte A6 – Backlover', width: '111mm', height: '154mm', pages: [front, back], css: POSTCARD_CSS })
}

const POSTCARD_CSS = `
  .safe { position: absolute; inset: 9mm; display: flex; flex-direction: column; }
  .warm { background: radial-gradient(80% 60% at 70% 40%, #f6d3a2, transparent 70%), linear-gradient(160deg, #f7ecdc, #f0d4ad); }
  .p-top { display: flex; align-items: baseline; justify-content: space-between; }
  .p-logo { font-size: 18pt; }
  .p-cup { width: 66mm; top: 20mm; inset-inline-start: 2mm; }
  .p-croissant { width: 58mm; top: 44mm; inset-inline-end: -10mm; transform: rotate(-14deg); }
  [dir="rtl"] .p-croissant { transform: rotate(14deg) scaleX(-1); }
  .p-offer { position: absolute; top: 21mm; inset-inline-end: 9mm; width: 30mm; height: 30mm; border-radius: 50%; background: var(--oven); color: var(--cream);
    display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; transform: rotate(8deg); padding: 3mm;
    box-shadow: 0 2mm 4mm rgba(40, 22, 8, 0.3); }
  .p-offer-label { font-size: 5.5pt; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--crust-light); }
  [lang="ar"] .p-offer-label { letter-spacing: 0; font-size: 6.5pt; }
  .p-offer-price { margin: 0.6mm 0; font: 400 17pt var(--display); color: var(--gold); }
  .p-offer-items { font-size: 5.6pt; line-height: 1.3; }
  [lang="ar"] .p-offer-items { font-size: 6.4pt; }
  .p-copy { margin-top: auto; position: relative; }
  .p-head { font-size: 25pt; }
  [lang="ar"] .p-head { font-size: 21pt; }
  .p-sub { margin-top: 2mm; font-size: 8pt; line-height: 1.5; color: var(--ink-2); }
  [lang="ar"] .p-sub { font-size: 8.8pt; }

  .pb-title { margin-top: 9mm; font-size: 22pt; }
  .pb-text { margin-top: 3mm; font-size: 8.4pt; line-height: 1.6; color: var(--cream-muted); }
  [lang="ar"] .pb-text { font-size: 9.2pt; }
  .pb-when { margin-top: 5mm; padding: 3mm 4mm; border-radius: 3mm; background: rgba(244, 236, 225, 0.07); display: grid; gap: 1mm; font-size: 8pt; }
  .pb-when strong { color: var(--gold); }
  .pb-bottom { margin-top: auto; display: flex; align-items: center; gap: 4mm; }
  .pb-qr { width: 20mm; height: 20mm; flex: none; }
  .pb-info { font-size: 7.4pt; line-height: 1.55; color: var(--cream-muted); }
  .pb-url { font-size: 8.4pt; font-weight: 700; color: var(--gold); margin-bottom: 1mm; }
  .pb-small { margin-top: 4mm; font-size: 5.8pt; color: var(--cream-muted); opacity: 0.8; }
`

// ---------------------------------------------------------------------------
// A3 window poster
// ---------------------------------------------------------------------------
export async function posterDocument(lang) {
  const t = (path, params) => text(lang, path, params)
  const code = await qr(shopUrl('/products'))
  const page = `
  <div class="sheet dark">
    <div class="safe">
      <header class="pp-top">${logo('pp-logo')}<span class="eyebrow pp-eyebrow">${t('bakery')} · ${t('placeLine')}</span></header>
      <div class="pp-stage">
        <img class="cutout pp-a" src="${photo('croissant-butter.png')}" alt="">
        <img class="cutout pp-b" src="${photo('pretzel.png')}" alt="">
        <img class="cutout pp-c" src="${photo('donut.png')}" alt="">
        <img class="cutout pp-d" src="${photo('macarons.png')}" alt="">
        <img class="cutout pp-e" src="${photo('cuppchtino.png')}" alt="">
      </div>
      <div class="pp-copy">
        <span class="badge pp-badge">${t('poster.kicker')}</span>
        <h1 class="display pp-head">${lines(t('poster.headline'))}</h1>
        <p class="pp-sub">${t('poster.sub')}</p>
      </div>
      <footer class="pp-foot">
        <div class="pp-qr-wrap"><div class="qr qr-card pp-qr">${code}</div><p>${t('poster.cta')}</p></div>
        <div class="pp-info">
          <p class="pp-url" dir="ltr">${esc(host())}</p>
          <div class="pp-hours"><p class="eyebrow">${t('hours')}</p>${hoursList(lang)}</div>
          <p class="pp-address">${addressLines(lang).join(' · ')}</p>
        </div>
      </footer>
    </div>
  </div>`
  return documentHtml({ lang, title: 'Plakat A3 – Backlover', width: '303mm', height: '426mm', pages: [page], css: POSTER_CSS })
}

const POSTER_CSS = `
  .safe { position: absolute; inset: 20mm 20mm 18mm; display: flex; flex-direction: column; }
  .accent { color: var(--crust-light); font-style: italic; }
  [lang="ar"] .accent { font-style: normal; }
  .badge { display: inline-block; padding: 2.4mm 6mm; border-radius: 12mm; background: var(--crust-light); color: var(--oven); font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; }
  .pp-badge { font-size: 13pt; }
  [lang="ar"] .pp-badge { letter-spacing: 0; font-size: 16pt; }
  .pp-top { display: flex; align-items: baseline; justify-content: space-between; }
  .pp-logo { font-size: 50pt; }
  .pp-eyebrow { --eyebrow: 11pt; }
  .pp-stage { position: relative; height: 150mm; margin-top: 6mm; }
  .pp-a { width: 150mm; top: 0; inset-inline-start: 50mm; transform: rotate(-8deg); }
  .pp-b { width: 82mm; top: 66mm; inset-inline-start: 0; transform: rotate(-12deg); }
  .pp-c { width: 74mm; top: 82mm; inset-inline-end: 0; transform: rotate(10deg); }
  .pp-d { width: 46mm; top: 6mm; inset-inline-end: 4mm; }
  .pp-e { width: 62mm; top: 4mm; inset-inline-start: 0; }
  .pp-copy { margin-top: 6mm; }
  .pp-head { margin-top: 6mm; font-size: 96pt; line-height: 0.95; }
  [lang="ar"] .pp-head { font-size: 76pt; line-height: 1.25; }
  .pp-sub { margin-top: 7mm; font-size: 20pt; color: var(--cream-muted); }
  .pp-foot { margin-top: auto; display: flex; align-items: flex-end; gap: 14mm; padding-top: 10mm; border-top: 0.4mm solid rgba(244, 236, 225, 0.15); }
  .pp-qr-wrap { display: grid; justify-items: center; gap: 3mm; font-size: 12pt; font-weight: 700; }
  .pp-qr { width: 68mm; height: 68mm; padding: 5mm; border-radius: 5mm; }
  .pp-info { flex: 1; display: grid; gap: 5mm; font-size: 13pt; line-height: 1.5; }
  .pp-url { font: 400 36pt 'Instrument Serif', serif; color: var(--gold); }
  .pp-hours { display: grid; gap: 1mm; max-width: 120mm; }
  .pp-hours .eyebrow { font-size: 10pt; margin-bottom: 1mm; }
  .pp-address { color: var(--cream-muted); font-size: 12pt; }
`

// ---------------------------------------------------------------------------
// Social media: Instagram post (1080 × 1350) and story (1080 × 1920)
// ---------------------------------------------------------------------------
export async function socialPostDocument(lang) {
  const t = (path, params) => text(lang, path, params)
  const page = `
  <div class="sheet dark">
    <div class="s-pad">
      <header class="s-top">${logo('s-logo')}<span class="s-kicker">${t('social.postKicker')}</span></header>
      <img class="cutout sp-a" src="${photo('croissant-chocolate.png')}" alt="">
      <img class="cutout sp-b" src="${photo('cuppchtino.png')}" alt="">
      <img class="cutout sp-c" src="${photo('macarons.png')}" alt="">
      <div class="s-copy">
        <h1 class="display sp-head">${lines(t('social.postHeadline'))}</h1>
        <p class="s-sub">${t('social.postSub')}</p>
        <p class="s-url" dir="ltr">${esc(host())}</p>
      </div>
    </div>
  </div>`
  return documentHtml({ lang, title: 'Social post', width: '1080px', height: '1350px', pages: [page], css: SOCIAL_CSS })
}

export async function socialStoryDocument(lang) {
  const t = (path, params) => text(lang, path, params)
  const page = `
  <div class="sheet dark">
    <div class="s-pad">
      <header class="s-top">${logo('s-logo')}</header>
      <span class="s-chip">${t('social.storyKicker')}</span>
      <h1 class="display st-head">${lines(t('social.storyHeadline'), 2)}</h1>
      <div class="st-stage">
        <img class="cutout st-a" src="${photo('croissant-butter.png')}" alt="">
        <img class="cutout st-b" src="${photo('pretzel.png')}" alt="">
        <img class="cutout st-c" src="${photo('donut-caramel.png')}" alt="">
      </div>
      <div class="st-phone">${phone(screen(lang, 'mobile-shop'))}</div>
      <div class="st-foot">
        <p class="s-sub">${t('social.storySub')}</p>
        <p class="st-link">${t('social.link')} ↑</p>
      </div>
    </div>
  </div>`
  return documentHtml({ lang, title: 'Social story', width: '1080px', height: '1920px', pages: [page], css: SOCIAL_CSS })
}

const SOCIAL_CSS = `
  .s-pad { position: absolute; inset: 80px; display: flex; flex-direction: column; }
  .accent { color: var(--crust-light); font-style: italic; }
  [lang="ar"] .accent { font-style: normal; }
  .s-top { display: flex; align-items: baseline; justify-content: space-between; }
  .s-logo { font-size: 64px; }
  .s-kicker { font-size: 26px; font-weight: 700; color: var(--crust-light); }
  .s-copy { margin-top: auto; position: relative; }
  .sp-head { font-size: 168px; line-height: 0.92; }
  [lang="ar"] .sp-head { font-size: 140px; line-height: 1.2; }
  .s-sub { margin-top: 28px; font-size: 38px; line-height: 1.4; color: var(--cream-muted); }
  .s-url { margin-top: 26px; font: 400 52px 'Instrument Serif', serif; color: var(--gold); }
  .sp-a { width: 640px; top: 150px; inset-inline-end: -110px; transform: rotate(-10deg); }
  .sp-b { width: 300px; top: 130px; inset-inline-start: 40px; }
  .sp-c { width: 200px; top: 420px; inset-inline-start: 250px; transform: rotate(-6deg); }
  [dir="rtl"] .sp-a { transform: rotate(10deg) scaleX(-1); }

  .s-chip { align-self: flex-start; margin-top: 120px; padding: 14px 30px; border-radius: 60px; background: var(--crust-light); color: var(--oven); font-size: 30px; font-weight: 800; }
  .st-head { margin-top: 40px; font-size: 150px; line-height: 0.95; }
  [lang="ar"] .st-head { font-size: 120px; line-height: 1.25; }
  .st-stage { position: relative; height: 420px; margin-top: 30px; }
  .st-a { width: 560px; top: 0; inset-inline-start: -40px; transform: rotate(-12deg); }
  .st-b { width: 280px; top: 220px; inset-inline-start: 420px; transform: rotate(8deg); }
  .st-c { width: 250px; top: -10px; inset-inline-end: -30px; }
  [dir="rtl"] .st-a { transform: rotate(12deg) scaleX(-1); }
  .st-phone { position: absolute; width: 330px; bottom: 90px; inset-inline-end: 80px; transform: rotate(5deg); }
  [dir="rtl"] .st-phone { transform: rotate(-5deg); }
  .st-phone .frame-phone { border-radius: 52px; padding: 13px; }
  .st-phone .frame-phone img { border-radius: 40px; }
  .st-phone .frame-phone::before { top: 22px; width: 80px; height: 20px; margin-left: -40px; border-radius: 20px; }
  .st-foot { margin-top: auto; max-width: 520px; }
  .st-link { margin-top: 30px; font-size: 30px; font-weight: 700; color: var(--gold); }
`
