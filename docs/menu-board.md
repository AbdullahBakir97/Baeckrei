# Menu screens for the TVs in the shop

The shop shows its menu on any TV or monitor: products, prices, "sold out",
vegan and other labels, today's opening status and promotions. Everything is
managed in the admin under **Menu screens**; changes reach the TVs within a
minute.

## Designing a screen (admin → Menu screens)

Each screen has its own design and address (`/menu-board/<name>`), so the
counter, the window and the café corner can each show something different.

- **Layout:** *Columns with highlight* (large product left, menu right),
  *Photo tiles*, *Classic menu* (typographic, no photos) or *One product,
  large* (a slideshow of the featured products).
- **Look:** five colour themes or your own colours, an accent colour, an
  elegant or a modern typeface, and an optional background photo (darkened
  so the text stays readable).
- **Content:** which categories and in what order, products to feature or
  to hide on this screen, prices, descriptions, photos, labels, the QR code
  for ordering ahead, the clock and the opening status, a headline and a
  running ticker along the bottom (German, English and Arabic).
- **Promotions:** full-screen slides between the menu pages, e.g. a breakfast
  offer. Each one can have a product, a photo or just a big message, a price,
  and run only on certain dates, days of the week or times of day.
- **Language:** German, English or Arabic, or two in turn (German and
  English, or German and Arabic). Arabic screens read right to left; their
  headline, ticker and promotions have their own Arabic texts, products show
  their English names.
- **Orientation:** automatic, or turned for a TV mounted upright whose player
  still sends a landscape picture.

The editor shows a live preview; **Save & go live** sends it to the TVs.
The screen marked *Default* is also shown at `/menu-board`.

## Putting a screen on a TV

Every screen has a **4-digit code** (shown in the admin).

1. On the TV (or the stick or computer connected to it), open the browser
   and go to `https://<your domain>/tv`.
2. Type the code with the remote.
3. Done. The device remembers its screen: whenever it opens `/tv` again it
   starts that screen by itself after a few seconds.

Set the device's start page to `https://<your domain>/tv`, so the menu comes
back after every power cut.

### Which device? (best first)

| Device | Why | Setup |
| --- | --- | --- |
| **Fire TV Stick 4K or an Android TV box** | Cheap, plugs into any TV, reliable | Install **Fully Kiosk Browser** (via the *Downloader* app on Fire TV). Start URL `https://<your domain>/tv`; turn on *Launch on boot*, *Keep screen on* and *Reload on network reconnect*. |
| **Raspberry Pi 4 or 5** | Built for running all day; cheapest per screen with a wired network | Install Raspberry Pi OS with desktop, enable auto login (`sudo raspi-config` → System Options → Boot / Auto Login), then run `deploy/kiosk/setup-raspberry-pi.sh https://<your domain>/tv --nightly-reboot` and reboot. |
| **Mini PC / any Windows PC** | Uses hardware you already have | Edit the address in `deploy/kiosk/menu-screen-windows.bat` and copy it into the Startup folder (`Win+R` → `shell:startup`). Turn off sleep in the Windows power settings. |
| **The TV's own browser** | No extra device | Works for a start; many TV browsers forget the page after switching off and are slower. |

### TV settings

- Switch off the TV's energy saving, *auto power off* and screensaver.
- Picture mode *Standard* or *Natural* (not *Vivid*), so the photos look right.
- Use the TV's on/off timer to switch it on before opening and off after
  closing – the menu starts with it.

### Reliability

- **No internet?** The screen keeps showing the last menu it loaded and shows
  a small "no connection" note; it updates again by itself.
- **Is it running?** The admin shows each screen as *online* (it checks in
  every minute) with its resolution, or when it was last seen.
- **Reload remotely:** *Reload screen* in the admin restarts the page on the
  TV within a minute, e.g. after an update.
- The page also reloads itself twice a day and keeps the display awake where
  the browser allows it.
- In a shop without internet, the whole shop can run on a small computer in
  the local network (`docker compose up`); the TVs then open
  `http://<that computer's address>/tv`.

## Older links

Addresses with options still work and override the screen's design:
`/menu-board?lang=en` (or `de`, `ar`), `?alternate=1`, `?categories=pastries,cakes`
(category address names), `?seconds=15`.
