# Telegram Shop Bot

A simple e-commerce bot for Telegram, built with Python and
[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).
Customers browse a product catalog, build a cart, and check out through a
guided conversation. The shop owner gets a separate admin command with
sales reports and a 24-hour follow-up reminder is scheduled automatically
after every order.

## Features

- **Product catalog & cart** — inline-keyboard menu; adding an item shows
  a quick confirmation without closing the menu, so customers can keep
  browsing.
- **Guided checkout** — a multi-step conversation collects the customer's
  name, phone number, and address, with input validation on each step
  (name must be letters only, phone must be 11 digits starting with `09`).
- **Order history** — customers can view their own past orders with
  `/myorders`.
- **Admin reports** — `/report` (visible only to the admin account) shows
  daily, weekly, or monthly sales: order count, items sold, and revenue,
  computed live from stored orders.
- **Automatic reminder** — 24 hours after an order is placed, the bot
  sends the customer a short follow-up message.

## Requirements

- Python 3.10+
- [`python-telegram-bot`](https://pypi.org/project/python-telegram-bot/)
  (version 20+, since the bot uses `Application.builder()` and
  `context.job_queue`)

Install it with:

```bash
pip install python-telegram-bot --upgrade
```

## Setup

1. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram and
   copy the token it gives you.
2. Set the token as an environment variable instead of writing it in the
   code:

   **Windows (PowerShell):**
   ```powershell
   $env:BOT_TOKEN = "your-token-here"
   ```

   **macOS / Linux:**
   ```bash
   export BOT_TOKEN="your-token-here"
   ```

3. Set your own numeric Telegram user ID in `ADMIN_ID` (the bot uses this
   to decide who is allowed to run `/report`). You can get your ID from
   a bot like [@userinfobot](https://t.me/userinfobot).
4. Make sure the image path used in `start()` (`banner.jpg`) points to a
   real image file on your machine, or remove that part if you don't want
   a welcome photo.
5. Run the bot:

   ```bash
   python ARAMÉ_Shop_Bot.py
   ```

   You should see `Bot is running...` in the terminal.

## Commands

| Command     | Who         | What it does                          |
|-------------|-------------|----------------------------------------|
| `/start`    | everyone    | Shows the welcome photo and product menu |
| `/cart`     | everyone    | Shows the current cart and a checkout button |
| `/myorders` | everyone    | Shows the user's own past orders       |
| `/report`   | admin only  | Shows daily/weekly/monthly sales stats |

## Project structure

This is a single-file bot (`ARAMÉ_Shop_Bot.py`) — everything
(product catalog, cart logic, checkout conversation, and admin reports)
lives in one script for simplicity. Orders and carts are kept in memory
(Python dictionaries/lists), so they reset if the bot restarts; a real
production version would store them in a database (e.g. SQLite).

## Notes

- Product data (`products` dict) currently holds sample items
  (Wireless Mouse, Coffee Mug, Notebook) for demonstration — replace with
  your own catalog.
- Prices are shown with a `$` sign in this sample version; change the
  formatting in the code if you prefer another currency.
  
---

**Author:** Aramesh Rafiee
[github.com/aramesh-rafiee-dev](https://github.com/aramesh-rafiee-dev)
