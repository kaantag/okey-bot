import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from game import OkeyGame
from config import TOKEN
from tile_renderer import draw_hand

logging.basicConfig(level=logging.INFO)
games = {}

WEB_APP_URL = "https://kaantag.github.io/okey-bot"

async def send_hand(context, player, game):
    if player.is_bot:
        return
    joker_info = f"🃏 Joker: {game.joker_tile}" if game.joker_tile else ""
    text = f"{joker_info}\n\nTaş atmak için /at <numara> yaz"
    img = draw_hand(player.hand, game.joker_tile)
    await context.bot.send_photo(player.user_id, photo=img, caption=text)

async def announce(context, chat_id, text):
    await context.bot.send_message(chat_id, text)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎮 Oyna!", web_app=WebAppInfo(url=WEB_APP_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎮 101 Okey Botuna Hoş Geldin!\n\n"
        "/yenioxun — Yeni oyun başlat\n"
        "/katil — Oyuna katıl\n"
        "/baslat — Oyunu başlat\n"
        "/el — Elini gör\n"
        "/at <n> — Taş at\n"
        "/cek — Desteden taş çek\n"
        "/cop — Çöpten taş al\n"
        "/skor — Skorları gör",
        reply_markup=reply_markup
    )

async def cmd_yeni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in games and games[chat_id].started:
        await update.message.reply_text("⚠️ Zaten aktif bir oyun var!")
        return
    games[chat_id] = OkeyGame(chat_id)
    user = update.effective_user
    games[chat_id].add_player(user.id, user.first_name)
    await update.message.reply_text(
        f"✅ Yeni oyun oluşturuldu!\n"
        f"👤 {user.first_name} katıldı (1/4)\n\n"
        f"Diğerleri /katil yazsın. Hazır olunca /baslat"
    )

async def cmd_katil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games:
        await update.message.reply_text("❌ Önce /yenioxun ile oyun oluştur!")
        return
    game = games[chat_id]
    if game.started:
        await update.message.reply_text("❌ Oyun zaten başladı!")
        return
    user = update.effective_user
    if game.add_player(user.id, user.first_name):
        count = len(game.players)
        await update.message.reply_text(f"✅ {user.first_name} katıldı! ({count}/4)")
    else:
        await update.message.reply_text("❌ Oyun dolu veya zaten katıldın!")

async def cmd_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games:
        await update.message.reply_text("❌ Önce /yenioxun yaz!")
        return
    game = games[chat_id]
    if game.started:
        await update.message.reply_text("⚠️ Oyun zaten başladı!")
        return
    game.fill_with_bots()
    game.start_game()
    player_list = "\n".join(f"{'🤖' if p.is_bot else '👤'} {p.name}" for p in game.players)
    await update.message.reply_text(
        f"🎮 Oyun başlıyor!\n\n{player_list}\n\n"
        f"🃏 Joker: {game.joker_tile}\n\n"
        f"Sıra: {game.current_player.name}"
    )
    for p in game.players:
        await send_hand(context, p, game)
    await bot_turn_if_needed(context, game)

async def cmd_el(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games or not games[chat_id].started:
        await update.message.reply_text("❌ Aktif oyun yok!")
        return
    game = games[chat_id]
    user = update.effective_user
    player = next((p for p in game.players if p.user_id == user.id), None)
    if not player:
        await update.message.reply_text("❌ Bu oyunda değilsin!")
        return
    await send_hand(context, player, game)

async def cmd_at(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games or not games[chat_id].started:
        return
    game = games[chat_id]
    user = update.effective_user
    cp = game.current_player
    if cp.user_id != user.id:
        await update.message.reply_text(f"⏳ Sıra {cp.name}'de!")
        return
    if not game.waiting_discard:
        await update.message.reply_text("❌ Önce taş çek! /cek veya /cop")
        return
    try:
        idx = int(context.args[0]) - 1
    except (IndexError, ValueError):
        await update.message.reply_text("Kullanım: /at <taş numarası>")
        return
    tile = game.discard_tile(cp, idx)
    if not tile:
        await update.message.reply_text("❌ Geçersiz taş numarası!")
        return
    await announce(context, chat_id, f"🗑 {cp.name} taş attı: {tile}")
    game.next_turn()
    await announce(context, chat_id, f"🎯 Sıra: {game.current_player.name}")
    await bot_turn_if_needed(context, game)

async def cmd_cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games or not games[chat_id].started:
        return
    game = games[chat_id]
    user = update.effective_user
    cp = game.current_player
    if cp.user_id != user.id:
        await update.message.reply_text(f"⏳ Sıra {cp.name}'de!")
        return
    if game.waiting_discard:
        await update.message.reply_text("❌ Önce taş at! /at <n>")
        return
    tile = game.draw_tile(cp)
    if not tile:
        await update.message.reply_text("❌ Deste bitti!")
        return
    await update.message.reply_text(f"✅ Taş çektin: {tile}\nŞimdi /at <n> ile taş at")
    await send_hand(context, cp, game)

async def cmd_cop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games or not games[chat_id].started:
        return
    game = games[chat_id]
    user = update.effective_user
    cp = game.current_player
    if cp.user_id != user.id:
        await update.message.reply_text(f"⏳ Sıra {cp.name}'de!")
        return
    if game.waiting_discard:
        await update.message.reply_text("❌ Önce taş at!")
        return
    tile = game.take_from_discard(cp)
    if not tile:
        await update.message.reply_text("❌ Çöp boş!")
        return
    await update.message.reply_text(f"♻️ Çöpten aldın: {tile}\nŞimdi /at <n> ile taş at")
    await send_hand(context, cp, game)

async def cmd_skor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in games:
        return
    scores = games[chat_id].calculate_scores()
    text = "📊 El Değerleri:\n" + "\n".join(f"{n}: {s} puan" for n, s in scores.items())
    await update.message.reply_text(text)

async def bot_turn_if_needed(context, game):
    import asyncio
    while game.started and game.current_player.is_bot:
        bot = game.current_player
        await asyncio.sleep(1.5)
        tile = game.draw_tile(bot)
        await announce(context, game.chat_id, f"🤖 {bot.name} taş çekti")
        discard_tile = bot.choose_tile_to_discard()
        idx = bot.hand.index(discard_tile)
        game.discard_tile(bot, idx)
        await announce(context, game.chat_id, f"🗑 {bot.name} attı: {discard_tile}")
        game.next_turn()
        await announce(context, game.chat_id, f"🎯 Sıra: {game.current_player.name}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("yenioxun", cmd_yeni))
    app.add_handler(CommandHandler("katil", cmd_katil))
    app.add_handler(CommandHandler("baslat", cmd_baslat))
    app.add_handler(CommandHandler("el", cmd_el))
    app.add_handler(CommandHandler("at", cmd_at))
    app.add_handler(CommandHandler("cek", cmd_cek))
    app.add_handler(CommandHandler("cop", cmd_cop))
    app.add_handler(CommandHandler("skor", cmd_skor))
    print("🤖 Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
