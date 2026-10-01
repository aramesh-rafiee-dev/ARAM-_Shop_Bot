from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import datetime
import os
from telegram import BotCommand, BotCommandScopeChat
from telegram.ext import ConversationHandler, MessageHandler, filters
NAME, PHONE, ADDRESS = range(3)
TOKEN = os.environ["BOT_TOKEN"]
products = {
    "p1": {"name": "Wireless Mouse", "price": 25},
    "p2": {"name": "Coffee Mug", "price": 12},
    "p3": {"name": "Notebook", "price": 8},
}
carts = {}
orders = []
ADMIN_ID = 5561120665  
def get_report(period="daily"):
    now = datetime.datetime.now()
    if period == "daily":
        filtered = [o for o in orders if o["date"].date() == now.date()]
    elif period == "weekly":
        week_ago = now - datetime.timedelta(days=7)
        filtered = [o for o in orders if o["date"] >= week_ago]
    elif period == "monthly":
        month_ago = now - datetime.timedelta(days=30)
        filtered = [o for o in orders if o["date"] >= month_ago]
    else:
        filtered = []
    total_orders = len(filtered)
    total_items = sum(len(o["items"]) for o in filtered)
    total_revenue = sum(o["total"] for o in filtered)
    text = (
        f"📊 report {period}:\n"
        f"numbers of orders: {total_orders}\n"
        f" numbers of products: {total_items}\n"
        f" total income: ${total_revenue}\n"
    )
    if filtered:
        text += "\n👥 details of orders :\n"
        for o in filtered:
            date_str = o["date"].strftime("%Y-%m-%d %H:%M")
            items_str = "، ".join(o["items"])
            text += (
                f"\n🗓 {date_str}\n"
                f"Name: {o['user_name']}\n"
                f"Phone Number: {o['phone']}\n"
                f"Address: {o['address']}\n"
                f"Product: {items_str}\n"
                f"total: ${o['total']}\n"
            )
    return text
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    keyboard = [
        [InlineKeyboardButton("Daily", callback_data="report_daily")],
        [InlineKeyboardButton("Weekly", callback_data="report_weekly")],
        [InlineKeyboardButton("Monthly", callback_data="report_monthly")],
    ]
    await update.message.reply_text("Which rebort do you want?", reply_markup=InlineKeyboardMarkup(keyboard))
async def setup_commands(app):
    public_commands = [
        BotCommand("start", "Start and show products."),
        BotCommand("cart", "Veiw shopping cart"),
        BotCommand("myorders", "My previous ordres"),
    ]
    admin_commands = public_commands + [
        BotCommand("report", "Sale report (Just Admin)"),
    ]
    await app.bot.set_my_commands(public_commands)
    await app.bot.set_my_commands(
        admin_commands,
        scope=BotCommandScopeChat(chat_id=ADMIN_ID),
    )
async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_cart = carts.get(user_id, [])
    if not user_cart:
        await update.message.reply_text("Your shopping cart is empty.")
        return
    total = 0
    text = "🛍️ Your shopping cart. :\n\n"
    for pid in user_cart:
        product = products[pid]
        text += f"- {product['name']}: ${product['price']}\n"
        total += product['price']
    text += f"\n total: ${total}"
    keyboard = [ order registration[InlineKeyboardButton(" ✅", callback_data="checkout")]]
    await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
async def my_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_orders = [o for o in orders if o["user_id"] == user_id]
    if not user_orders:
        await update.message.reply_text("You haven't registered any orders yet.")
        return
    text = "📦 Your previous ordres:\n\n"
    for order in user_orders:
        date_str = order["date"].strftime("%Y-%m-%d %H:%M")
        items_str = "، ".join(order["items"])
        text += f"🗓 {date_str}\n products: {items_str}\n total: ${order['total']}\n\n"
    await update.message.reply_text(text)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for pid, product in products.items():
        text = f"{product['name']} - ${product['price']}"
        keyboard.append([
            InlineKeyboardButton(text, callback_data=f"add_{pid}")
        ])
    keyboard.append([
        InlineKeyboardButton("🛍 View shopping cart", callback_data="view_cart")
    ])
    with open(r"E:\python\banner.jpg", "rb") as photo:
        await update.message.reply_photo(
        photo=photo,
        caption="✨ Welcome to ARAMÉ\nSimple. Personal. Yours."
    )
    await update.message.reply_text(
        "Welcome to our shop!Please choose products.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data.startswith("add_"):
        pid = query.data.replace("add_", "")
        carts.setdefault(user_id, []).append(pid)
        await query.answer(f"{products[pid]['name']} ✅ Added to your shopping cart.", show_alert=True)
    elif query.data == "view_cart":
        user_cart = carts.get(user_id, [])
        if not user_cart:
            await query.edit_message_text("Your shopping cart is empty.")
            return
        total = 0
        text = "🛍️ Your shopping cart.:\n\n"
        for pid in user_cart:
            product = products[pid]
            text += f"- {product['name']}: ${product['price']}\n"
            total += product['price']
        text += f"\ntotal: ${total}"
        keyboard = [[InlineKeyboardButton(" Register the order. ✅", callback_data="checkout")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith("report_"):
        if query.from_user.id != ADMIN_ID:
            return
        period = query.data.replace("report_", "")
        await query.edit_message_text(get_report(period))
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(job.chat_id, text="Reminder:Your order is being processed. ✅")
async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Plaese type ypur name:")
    return NAME
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not name.replace(" ", "").isalpha():
        await update.message.reply_text("❌ The name should contain letters.Type it again.:")
        return NAME
    context.user_data["name"] = name
    await update.message.reply_text("Plaese type ypur phone number:")
    return PHONE
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
        await update.message.reply_text("❌ The number must be 11 digits and start with 09.Be sure to enter the number in English.Type it again:")
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("Plaese type ypur address:")
    return ADDRESS
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    user_id = update.effective_user.id
    user_cart = carts.get(user_id, [])
    if not user_cart:
        await update.message.reply_text("Your shopping cart is empty.")
        return ConversationHandler.END
    order_record = {
        "user_id": user_id,
        "user_name": context.user_data["name"],
        "phone": context.user_data["phone"],
        "address": context.user_data["address"],
        "items": [products[pid]['name'] for pid in user_cart],
        "total": sum(products[pid]['price'] for pid in user_cart),
        "date": datetime.datetime.now(),
    }
    orders.append(order_record)
    carts[user_id] = []
    await update.message.reply_text(
        "✅ Your order has been successfully placed. We will contacy you soon."
    )
    context.job_queue.run_once(
        send_reminder,
        when=86400,
        chat_id=update.effective_chat.id,
    )
    return ConversationHandler.END
def main():
    app = Application.builder().token(TOKEN).post_init(setup_commands).connect_timeout(30).read_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report_command))
    conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(checkout_start, pattern="^checkout$")],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
    },
    fallbacks=[],
)
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("cart", cart_command))
    app.add_handler(CommandHandler("myorders", my_orders_command))
    print("Bot is running...")
    app.run_polling()
if __name__ == "__main__":
    main()
