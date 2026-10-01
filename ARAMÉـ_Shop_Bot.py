from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import datetime
import os
from telegram import BotCommand, BotCommandScopeChat
from telegram.ext import ConversationHandler, MessageHandler, filters
NAME, PHONE, ADDRESS = range(3)
# Never hardcode the token in the file. Set it as an environment variable instead:
#   Windows (PowerShell):  $env:BOT_TOKEN = "your-new-token-here"
#   then run: python Aramesh_mini_shop_bot_fixed.py
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
        f"📊 گزارش {period}:\n"
        f"تعداد سفارش: {total_orders}\n"
        f"تعداد اقلام: {total_items}\n"
        f"مجموع درآمد: ${total_revenue}\n"
    )
    if filtered:
        text += "\n👥 جزئیات سفارش‌ها:\n"
        for o in filtered:
            date_str = o["date"].strftime("%Y-%m-%d %H:%M")
            items_str = "، ".join(o["items"])
            text += (
                f"\n🗓 {date_str}\n"
                f"نام: {o['user_name']}\n"
                f"شماره: {o['phone']}\n"
                f"آدرس: {o['address']}\n"
                f"اقلام: {items_str}\n"
                f"جمع: ${o['total']}\n"
            )
    return text
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    keyboard = [
        [InlineKeyboardButton("روزانه", callback_data="report_daily")],
        [InlineKeyboardButton("هفتگی", callback_data="report_weekly")],
        [InlineKeyboardButton("ماهانه", callback_data="report_monthly")],
    ]
    await update.message.reply_text("کدوم گزارش رو می‌خوای؟", reply_markup=InlineKeyboardMarkup(keyboard))
async def setup_commands(app):
    public_commands = [
        BotCommand("start", "شروع و نمایش محصولات"),
        BotCommand("cart", "مشاهده سبد خرید"),
        BotCommand("myorders", "سفارش‌های قبلی من"),
    ]
    admin_commands = public_commands + [
        BotCommand("report", "گزارش فروش (فقط ادمین)"),
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
        await update.message.reply_text("سبد خرید شما خالی است.")
        return
    total = 0
    text = "🛍️ سبد خرید شما:\n\n"
    for pid in user_cart:
        product = products[pid]
        text += f"- {product['name']}: ${product['price']}\n"
        total += product['price']
    text += f"\nجمع کل: ${total}"
    keyboard = [[InlineKeyboardButton("ثبت سفارش ✅", callback_data="checkout")]]
    await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
async def my_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_orders = [o for o in orders if o["user_id"] == user_id]
    if not user_orders:
        await update.message.reply_text("هنوز سفارشی ثبت نکرده‌اید.")
        return
    text = "📦 سفارش‌های قبلی شما:\n\n"
    for order in user_orders:
        date_str = order["date"].strftime("%Y-%m-%d %H:%M")
        items_str = "، ".join(order["items"])
        text += f"🗓 {date_str}\nاقلام: {items_str}\nجمع: ${order['total']}\n\n"
    await update.message.reply_text(text)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for pid, product in products.items():
        text = f"{product['name']} - ${product['price']}"
        keyboard.append([
            InlineKeyboardButton(text, callback_data=f"add_{pid}")
        ])
    keyboard.append([
        InlineKeyboardButton("🛍 مشاهده سبد خرید", callback_data="view_cart")
    ])
    with open(r"E:\python\banner.jpg", "rb") as photo:
        await update.message.reply_photo(
        photo=photo,
        caption="✨ Welcome to ARAMÉ\nSimple. Personal. Yours."
    )
    await update.message.reply_text(
        "به فروشگاه ما خوش اومدید! محصول مورد نظرتون رو انتخاب کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data.startswith("add_"):
        pid = query.data.replace("add_", "")
        carts.setdefault(user_id, []).append(pid)
        await query.answer(f"{products[pid]['name']} ✅ به سبد خرید اضافه شد", show_alert=True)
    elif query.data == "view_cart":
        user_cart = carts.get(user_id, [])
        if not user_cart:
            await query.edit_message_text("سبد خرید شما خالی است.")
            return
        total = 0
        text = "🛍️ سبد خرید شما:\n\n"
        for pid in user_cart:
            product = products[pid]
            text += f"- {product['name']}: ${product['price']}\n"
            total += product['price']
        text += f"\nجمع کل: ${total}"
        keyboard = [[InlineKeyboardButton("ثبت سفارش ✅", callback_data="checkout")]]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith("report_"):
        if query.from_user.id != ADMIN_ID:
            return
        period = query.data.replace("report_", "")
        await query.edit_message_text(get_report(period))
async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(job.chat_id, text="یادآوری: وضعیت سفارش شما در حال پیگیریه ✅")
async def checkout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("لطفاً اسمتون رو بفرستید:")
    return NAME
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not name.replace(" ", "").isalpha():
        await update.message.reply_text("❌ اسم باید فقط حروف باشه. دوباره بفرستید:")
        return NAME
    context.user_data["name"] = name
    await update.message.reply_text("شماره تماستون رو بفرستید:")
    return PHONE
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not (phone.isdigit() and len(phone) == 11 and phone.startswith("09")):
        await update.message.reply_text("❌ شماره باید ۱۱ رقم و با ۰۹ شروع بشه؛ حتما اعداد را به انگلیسی وارد کنید. دوباره بفرستید:")
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("آدرستون رو بفرستید:")
    return ADDRESS
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    user_id = update.effective_user.id
    user_cart = carts.get(user_id, [])
    if not user_cart:
        await update.message.reply_text("سبد خرید شما خالی است.")
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
        "✅ سفارش شما با موفقیت ثبت شد! به‌زودی باهاتون تماس می‌گیریم."
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
