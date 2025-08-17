import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import time
from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

games = {}
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1),          (0, 1),
              (1, -1),  (1, 0), (1, 1)]

def create_board():
    board = [['.' for _ in range(8)] for _ in range(8)]
    board[3][3], board[3][4] = 'W', 'B'
    board[4][3], board[4][4] = 'B', 'W'
    return board

def get_symbol(cell):
    return '🟡' if cell == 'W' else '⚫' if cell == 'B' else '⬜'

def generate_board_markup(board):
    markup = InlineKeyboardMarkup()
    for i in range(8):
        row = []
        for j in range(8):
            symbol = get_symbol(board[i][j])
            row.append(InlineKeyboardButton(symbol, callback_data=f"{i},{j}"))
        markup.row(*row)
    return markup

def get_flips(board, row, col, player):
    if board[row][col] != '.':
        return []
    opponent = 'W' if player == 'B' else 'B'
    flips = []
    for dx, dy in DIRECTIONS:
        x, y = row + dx, col + dy
        line = []
        while 0 <= x < 8 and 0 <= y < 8 and board[x][y] == opponent:
            line.append((x, y))
            x += dx
            y += dy
        if line and 0 <= x < 8 and 0 <= y < 8 and board[x][y] == player:
            flips.extend(line)
    return flips

def make_move(board, row, col, player):
    flips = get_flips(board, row, col, player)
    if not flips:
        return False
    board[row][col] = player
    for x, y in flips:
        board[x][y] = player
    return True

def get_valid_moves(board, player):
    return [(i, j) for i in range(8) for j in range(8) if get_flips(board, i, j, player)]

def count_pieces(board):
    b = sum(row.count('B') for row in board)
    w = sum(row.count('W') for row in board)
    return b, w

def update_board_message(chat_id, text, board):
    markup = generate_board_markup(board)
    if 'message_id' in games[chat_id]:
        bot.edit_message_text(
            text,
            chat_id,
            games[chat_id]['message_id'],
            reply_markup=markup
        )
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup)
        games[chat_id]['message_id'] = msg.message_id

def end_game(chat_id):
    board = games[chat_id]['board']
    b, w = count_pieces(board)
    result = "🤝 Ничья!" if b == w else "🎉 Вы победили!" if b > w else "🤖 Победа бота!"
    final_message = (
        f"🏁 *Игра окончена!*\n\n"
        f"⚫ Ваши фишки: {b}\n"
        f"🟡 Фишки бота: {w}\n\n"
        f"{result}\n\n"
        f"Спасибо за игру! Вы можете начать новую партию командой /start"
    )
    update_board_message(chat_id, final_message, board)
    del games[chat_id]

def bot_move(chat_id):
    board = games[chat_id]['board']
    moves = get_valid_moves(board, 'W')
    if not moves:
        return False
    i, j = moves[0]
    make_move(board, i, j, 'W')
    games[chat_id]['turn'] = 'B'
    return True

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    board = create_board()
    player_starts = random.choice([True, False])
    current_turn = 'B' if player_starts else 'W'

    games[chat_id] = {
        'board': board,
        'turn': current_turn
    }

    first = "Вы ходите первым!" if current_turn == 'B' else "Бот ходит первым..."
    markup = generate_board_markup(board)
    msg = bot.send_message(chat_id, f"🎲 {first}\n\nХод: {'⚫ Вы' if current_turn == 'B' else '🟡 Бот'}", reply_markup=markup)
    games[chat_id]['message_id'] = msg.message_id

    if current_turn == 'W':
        if bot_move(chat_id):
            update_board_message(chat_id, "Ваш ход: ⚫", board)
        else:
            end_game(chat_id)

@bot.message_handler(commands=['help'])
def handle_help(message):
    text = (
        "🧩 *Реверси (Отелло)* — стратегическая настольная игра 8x8.\n"
        "Вы — ⚫, бот — 🟡. Цель — занять больше клеток.\n\n"
        "*Команды:*\n"
        "/start — начать новую игру\n"
        "/help — показать справку"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_click(call):
    chat_id = call.message.chat.id
    if chat_id not in games:
        bot.answer_callback_query(call.id, "Сначала начните игру с /start.")
        return

    game = games[chat_id]
    board = game['board']
    turn = game['turn']

    if turn != 'B':
        bot.answer_callback_query(call.id, "Сейчас ход бота.")
        return

    i, j = map(int, call.data.split(','))
    if make_move(board, i, j, 'B'):
        bot.answer_callback_query(call.id, f"Ваш ход: {chr(j+65)}{i+1}")
        game['turn'] = 'W'
        update_board_message(chat_id, "Ход: 🟡 Бот", board)

        time.sleep(1)

        if bot_move(chat_id):
            update_board_message(chat_id, "Ваш ход: ⚫", board)
        else:
            b_moves = get_valid_moves(board, 'B')
            if not b_moves:
                end_game(chat_id)
                return
            else:
                update_board_message(chat_id, "Бот пропустил ход. Ваш ход: ⚫", board)
                game['turn'] = 'B'
    else:
        bot.answer_callback_query(call.id, "Неверный ход.")

    # Проверка ситуации, если у пользователя нет доступных ходов
    if game['turn'] == 'B':
        player_moves = get_valid_moves(board, 'B')
        if not player_moves:
            update_board_message(chat_id, "У вас нет допустимых ходов. Ход переходит к боту...", board)
            time.sleep(3)
            game['turn'] = 'W'
            if bot_move(chat_id):
                update_board_message(chat_id, "Ваш ход: ⚫", board)
                game['turn'] = 'B'
            else:
                update_board_message(chat_id, "Бот также не может ходить...", board)
                time.sleep(2)
                end_game(chat_id)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
