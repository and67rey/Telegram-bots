import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random
from telebot.apihelper import ApiTelegramException
from dotenv import load_dotenv

load_dotenv('.env')
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

user_sessions = {}
EMPTY_BOARD = [' '] * 9
WIN_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

EMOJI_MAP = {' ': '⬜️', 'X': '❌', 'O': '🟢'}

def check_winner(board, symbol):
    return any(all(board[i] == symbol for i in combo) for combo in WIN_COMBINATIONS)

def board_to_markup(board):
    markup = InlineKeyboardMarkup()
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            idx = i + j
            text = EMOJI_MAP[board[idx]]
            callback_data = str(idx) if board[idx] == ' ' else 'none'
            row.append(InlineKeyboardButton(text, callback_data=callback_data))
        markup.row(*row)
    return markup

def reset_board():
    return [' '] * 9

def ask_play_again(user_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Да", callback_data='play_again_yes'),
        InlineKeyboardButton("Нет", callback_data='play_again_no')
    )
    bot.send_message(user_id, "Спасибо за игру! Хотите сыграть ещё раз?", reply_markup=markup)

def choose_difficulty(user_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Начальный", callback_data='difficulty_easy'),
        InlineKeyboardButton("Средний", callback_data='difficulty_medium'),
        InlineKeyboardButton("Сложный", callback_data='difficulty_hard')
    )
    bot.send_message(user_id, "Выберите уровень сложности:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_game(message):
    user_id = message.from_user.id
    user_sessions[user_id] = {
        'board': reset_board(),
        'user_symbol': 'X',
        'bot_symbol': 'O',
        'user_wins': 0,
        'bot_wins': 0,
        'in_game': True,
        'message_id': None,
        'difficulty': 'easy'
    }
    choose_difficulty(user_id)

@bot.message_handler(commands=['level'])
def level_command(message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'board': reset_board(),
            'user_symbol': 'X',
            'bot_symbol': 'O',
            'user_wins': 0,
            'bot_wins': 0,
            'in_game': True,
            'message_id': None,
            'difficulty': 'easy'
        }
    choose_difficulty(user_id)

def start_new_round(user_id):
    session = user_sessions[user_id]
    session['board'] = reset_board()
    coin = random.choice(['орел', 'решка'])
    if coin == 'решка':
        text = f"Монетка подброшена... Выпала {coin}!\nБот ходит первым."
        bot_move(user_id)
    else:
        text = f"Монетка подброшена... Выпал {coin}!\nВы ходите первым."
    msg = bot.send_message(user_id, text, reply_markup=board_to_markup(session['board']))
    session['message_id'] = msg.message_id

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
/start — начать новую игру
/help — справка по игре
/quit — завершить игру
/level — выбрать уровень сложности

Ходы совершаются нажатием на клетки поля.
Вы играете за ❌, бот — за 🟢.

Уровни сложности:
- Начальный — бот делает случайные ходы
- Средний — бот использует стратегию: побеждает, блокирует, занимает центр и углы
- Сложный — бот использует алгоритм Минимакс и не допускает поражений
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['quit'])
def quit_game(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)
    if session and (session['user_wins'] > 0 or session['bot_wins'] > 0):
        text = f"Спасибо за игру! 🎮\nВаши победы: {session['user_wins']}\nПобеды бота: {session['bot_wins']}\nДо новых встреч!"
    else:
        text = "Игра завершена. Надеюсь, в следующий раз мы сыграем по-настоящему! ✨"
    bot.send_message(user_id, text)
    user_sessions.pop(user_id, None)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    session = user_sessions.get(user_id)

    if call.data == 'play_again_yes':
        bot.answer_callback_query(call.id)
        start_new_round(user_id)
        return

    if call.data == 'play_again_no':
        bot.answer_callback_query(call.id)
        quit_game(call)
        return

    if call.data.startswith('difficulty_'):
        difficulty = call.data.split('_')[1]
        session['difficulty'] = difficulty
        bot.answer_callback_query(call.id)
        start_new_round(user_id)
        return

    if not session or not session['in_game']:
        bot.answer_callback_query(call.id, "Начните игру с /start")
        return

    if call.data == 'none':
        bot.answer_callback_query(call.id, "Недопустимый ход")
        return

    index = int(call.data)
    board = session['board']
    if board[index] != ' ':
        bot.answer_callback_query(call.id, "Клетка занята")
        return

    board[index] = session['user_symbol']
    if check_winner(board, session['user_symbol']):
        session['user_wins'] += 1
        bot.edit_message_text(
            f"Вы выиграли! 🎉\nВаши победы: {session['user_wins']}\nПобеды бота: {session['bot_wins']}",
            user_id, session['message_id'],
            reply_markup=board_to_markup(board))
        ask_play_again(user_id)
        return

    if ' ' not in board:
        bot.edit_message_text("Ничья! 🙃", user_id, session['message_id'], reply_markup=board_to_markup(board))
        ask_play_again(user_id)
        return

    bot_move(user_id)
    try:
        bot.edit_message_reply_markup(user_id, session['message_id'], reply_markup=board_to_markup(session['board']))
    except ApiTelegramException as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise

def smart_bot_choice(board, bot_symbol, user_symbol):
    for i in range(9):
        if board[i] == ' ':
            board[i] = bot_symbol
            if check_winner(board, bot_symbol):
                return i
            board[i] = ' '
    for i in range(9):
        if board[i] == ' ':
            board[i] = user_symbol
            if check_winner(board, user_symbol):
                return i
            board[i] = ' '
    if board[4] == ' ':
        return 4
    for i in [0, 2, 6, 8]:
        if board[i] == ' ':
            return i
    for i in [1, 3, 5, 7]:
        if board[i] == ' ':
            return i
    return random.choice([i for i, cell in enumerate(board) if cell == ' '])

def minimax_ab(board, depth, is_maximizing, bot_symbol, user_symbol, alpha, beta):
    if check_winner(board, bot_symbol):
        return 10 - depth
    if check_winner(board, user_symbol):
        return depth - 10
    if ' ' not in board:
        return 0

    if is_maximizing:
        max_eval = -float('inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = bot_symbol
                eval = minimax_ab(board, depth + 1, False, bot_symbol, user_symbol, alpha, beta)
                board[i] = ' '
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(9):
            if board[i] == ' ':
                board[i] = user_symbol
                eval = minimax_ab(board, depth + 1, True, bot_symbol, user_symbol, alpha, beta)
                board[i] = ' '
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

def hard_bot_choice(board, bot_symbol, user_symbol):
    best_score = -float('inf')
    move = None
    for i in range(9):
        if board[i] == ' ':
            board[i] = bot_symbol
            score = minimax_ab(board, 0, False, bot_symbol, user_symbol, -float('inf'), float('inf'))
            board[i] = ' '
            if score > best_score:
                best_score = score
                move = i
    return move

def bot_move(user_id):
    session = user_sessions[user_id]
    board = session['board']
    difficulty = session.get('difficulty', 'easy')
    if difficulty == 'medium':
        choice = smart_bot_choice(board, session['bot_symbol'], session['user_symbol'])
    elif difficulty == 'hard':
        choice = hard_bot_choice(board, session['bot_symbol'], session['user_symbol'])
    else:
        available = [i for i, cell in enumerate(board) if cell == ' ']
        choice = random.choice(available)
    board[choice] = session['bot_symbol']
    if check_winner(board, session['bot_symbol']):
        session['bot_wins'] += 1
        bot.edit_message_text(
            f"Бот выиграл! 🤖\nВаши победы: {session['user_wins']}\nПобеды бота: {session['bot_wins']}",
            user_id, session['message_id'],
            reply_markup=board_to_markup(board))
        ask_play_again(user_id)
        return
    if ' ' not in board:
        bot.edit_message_text("Ничья! 🙃", user_id, session['message_id'], reply_markup=board_to_markup(board))
        ask_play_again(user_id)

bot.infinity_polling()
