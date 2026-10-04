#!/usr/bin/env bash
# Turns a Raspberry Pi (Raspberry Pi OS with desktop, Bookworm or newer) into
# a menu screen: it starts the menu full screen after every boot, keeps the
# screen on, restarts the browser if it ever closes, and (optionally) reboots
# every night.
#
#   ./setup-raspberry-pi.sh https://backlover.de/tv            # pair with the code on screen
#   ./setup-raspberry-pi.sh https://backlover.de/menu-board/theke
#   ./setup-raspberry-pi.sh https://backlover.de/tv --nightly-reboot
#
# Run it as the user that logs in to the desktop (not with sudo).
set -euo pipefail

URL="${1:-}"
NIGHTLY="${2:-}"
if [ -z "$URL" ]; then
  echo "Usage: $0 https://your-shop/tv [--nightly-reboot]" >&2
  exit 1
fi

echo "› Installing the browser"
sudo apt-get update -qq
sudo apt-get install -y -qq chromium-browser >/dev/null 2>&1 || sudo apt-get install -y -qq chromium >/dev/null
BROWSER="$(command -v chromium-browser || command -v chromium)"

echo "› Keeping the screen on"
sudo raspi-config nonint do_blanking 1 >/dev/null 2>&1 || true

echo "› Writing the start script"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/menu-kiosk" <<SCRIPT
#!/bin/sh
# Started with the desktop: show the menu full screen and start it again
# if the browser ever closes. The browser profile keeps the screen code.
sleep 5
while true; do
  "$BROWSER" --kiosk --noerrdialogs --disable-infobars --disable-session-crashed-bubble \\
    --disable-features=Translate --check-for-update-interval=31536000 \\
    --autoplay-policy=no-user-gesture-required --password-store=basic \\
    --overscroll-history-navigation=0 "$URL"
  sleep 5
done
SCRIPT
chmod +x "$HOME/.local/bin/menu-kiosk"

echo "› Starting it with the desktop"
# Wayland with labwc (Raspberry Pi OS since late 2024)
mkdir -p "$HOME/.config/labwc"
touch "$HOME/.config/labwc/autostart"
grep -q menu-kiosk "$HOME/.config/labwc/autostart" || echo "$HOME/.local/bin/menu-kiosk &" >> "$HOME/.config/labwc/autostart"
# Wayland with wayfire (Bookworm before late 2024)
if [ -f "$HOME/.config/wayfire.ini" ] && ! grep -q menu-kiosk "$HOME/.config/wayfire.ini"; then
  printf '\n[autostart]\nmenu = %s\n' "$HOME/.local/bin/menu-kiosk" >> "$HOME/.config/wayfire.ini"
fi
# X11 (older systems)
mkdir -p "$HOME/.config/lxsession/LXDE-pi"
touch "$HOME/.config/lxsession/LXDE-pi/autostart"
grep -q menu-kiosk "$HOME/.config/lxsession/LXDE-pi/autostart" || echo "@$HOME/.local/bin/menu-kiosk" >> "$HOME/.config/lxsession/LXDE-pi/autostart"

if [ "$NIGHTLY" = "--nightly-reboot" ]; then
  echo "› Rebooting every night at 04:30"
  ( sudo crontab -l 2>/dev/null | grep -v 'menu-kiosk-reboot'; echo '30 4 * * * /sbin/shutdown -r now # menu-kiosk-reboot' ) | sudo crontab -
fi

echo "✓ Done. Restart the Pi (sudo reboot); the menu starts by itself."
echo "  Make sure the Pi logs in to the desktop automatically: sudo raspi-config → System Options → Boot / Auto Login."
