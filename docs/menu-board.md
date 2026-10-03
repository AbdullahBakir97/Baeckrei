# Menu board for the shop's screens

`/menu-board` shows the shop's products and prices full screen, made for TVs
and monitors in the shop. It reads the live catalog, so a new product, a price
change or "sold out" in the admin appears on the screen within a minute.

- Landscape (TV on the wall) and portrait (screen standing upright) are both
  supported; everything scales with the screen, from 1080p to 4K.
- Categories flow down the columns like a printed menu. When there is more
  than fits, the board turns the page every few seconds.
- The left side shows one product large, today's opening status, the time and
  a QR code that opens the online shop.
- Products with stock 0 show as "Ausverkauft".
- The screen stays on while the page is open (where the browser allows it),
  and the page reloads itself twice a day to pick up new versions of the site.

The admin sidebar has a **Menü-Bildschirm** link that opens it.

## Options

Add them to the address, e.g. `https://backlover.de/menu-board?lang=en&seconds=15`.

| Option | Example | Effect |
| --- | --- | --- |
| `lang` | `lang=en` | Language (German by default) |
| `alternate` | `alternate=1` | Switch between German and English after each round |
| `categories` | `categories=pastries,cakes` | Only these categories (one screen per counter) |
| `seconds` | `seconds=15` | Time per page (at least 5) |

Category slugs are shown in the admin under Categories.

## Setting up a screen

Any device with a current browser works.

- **Smart TV / Fire TV / Android TV box:** open the browser, go to
  `https://<your domain>/menu-board`, switch to full screen. On Fire TV the
  "Silk" browser works; "Fully Kiosk Browser" (Android) starts the page on its
  own after a power cut.
- **Mini PC or Raspberry Pi with Chromium:** start Chromium in kiosk mode,
  e.g. in the autostart:

  ```bash
  chromium --kiosk --noerrdialogs --disable-session-crashed-bubble \
    --autoplay-policy=no-user-gesture-required https://<your domain>/menu-board
  ```

- **Windows PC:** create a shortcut with
  `"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk https://<your domain>/menu-board`
  and put it in the Startup folder.

Turn off the TV's own screen saver / sleep timer, and set the TV's picture
mode to "Standard" or "Natural" (not "Vivid") so the photos look right.
