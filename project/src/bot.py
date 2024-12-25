from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
# Импортируем необходимые библиотеки
import pandas as pd
import numpy as np
import streamlit as st
import joblib
# Загрузка обученной модели
model = joblib.load('divorce.pkl')


# Состояния для опроса
QUESTION, RESULT = range(2)

# Вопросы
questions = [
    "Когда один из нас извиняется, если наши обсуждения идут в плохом направлении, проблема не обостряется.",
    "Я знаю, что мы можем игнорировать наши различия, даже если иногда становится трудно.",
    "Когда это необходимо, мы с партнером можем начать обсуждение заново и исправить ситуацию.",
    "Когда я спорю с партнером, в конце концов, я всё равно свяжусь с ним.",
    "Время, проведенное с партнером, особенно важно для нас.",
    "Мы не проводим время дома как партнеры.",
    "Мы больше похожи на двух незнакомцев, которые делят одно пространство дома, а не на семью.",
    "Я наслаждаюсь нашими праздниками с партнером.",
    "Я люблю путешествовать с партнером.",
    "У моего партнера и у меня большинство целей совпадают.",
    "Я думаю, что однажды в будущем, оглядываясь назад, увижу, что мы с партнером гармоничны друг с другом.",
    "У моего партнера и у меня схожие ценности в вопросах личной свободы.",
    "У меня и моего партнера схожие интересы в плане развлечений.",
    "Большинство наших целей, связанных с людьми (детьми, друзьями и т.д.), совпадают.",
    "Наши мечты о совместной жизни с партнером схожи и гармоничны.",
    "Мы с партнером совместимы в понимании того, какой должна быть любовь.",
    "Мы с партнером разделяем одни и те же взгляды на то, что значит быть счастливым в жизни.",
    "У нас с партнером похожие представления о том, каким должен быть брак.",
    "У нас с партнером схожие взгляды на распределение ролей в браке.",
    "У нас с партнером схожие ценности в вопросах доверия.",
    "Я точно знаю, что нравится моему партнеру.",
    "Я знаю, как мой партнер хочет, чтобы за ним ухаживали, когда он болеет.",
    "Я знаю, какая еда нравится моему партнеру.",
    "Я могу сказать, с каким стрессом сталкивается мой партнер в жизни.",
    "Я знаю внутренний мир моего партнера.",
    "Я знаю основные беспокойства моего партнера.",
    "Я знаю, какие сейчас источники стресса у моего партнера.",
    "Я знаю надежды и желания моего партнера.",
    "Я очень хорошо знаю своего партнера.",
    "Я знаю друзей моего партнера и их социальные связи.",
    "Я чувствую агрессию, когда спорю с партнером.",
    "Обсуждая с партнером, я обычно использую такие выражения, как …..",
    "Я могу использовать негативные высказывания о личности моего партнера во время обсуждений.",
    "Я могу использовать оскорбительные выражения во время обсуждений.",
    "Я могу оскорблять в наших обсуждениях.",
    "Я могу быть унизительным во время споров.",
    "Мои споры с партнером не бывают спокойными.",
    "Я ненавижу манеру партнера поднимать тему.",
    "Ссоры часто возникают внезапно.",
    "Мы начинаем ссору прежде, чем я успеваю понять, что происходит.",
    "Когда я говорю с партнером о чем-то, мое спокойствие внезапно исчезает.",
    "Когда я спорю с партнером, я просто замыкаюсь и ничего не говорю.",
    "Я в основном жажду немного успокоить обстановку.",
    "Иногда я думаю, что мне было бы полезно уйти из дома на время.",
    "Я предпочел бы молчать, чем спорить с партнером.",
    "Даже если я прав в споре, я стараюсь не расстраивать другую сторону.",
    "Когда я спорю с партнером, я молчу, потому что боюсь не сдержать свой гнев.",
    "Я чувствую себя правым в наших обсуждениях.",
    "То, в чем меня обвиняют, ко мне не имеет никакого отношения.",
    "На самом деле я не виноват в том, в чем меня обвиняют.",
    "Я не виноват в проблемах дома.",
    "Я бы не колебался, чтобы рассказать партнеру о его недостатках.",
    "Когда мы обсуждаем, я напоминаю партнеру о его недостатках.",
    "Я не боюсь рассказать партнеру о его некомпетентности."
]

# Варианты ответа
choices = ["Не согласен", "Скорее нет", "Не знаю", "Скорее да", "Согласен"]
user_answers = []  # Хранение ответов

bot_message_id = None  # Хранение ID сообщения бота


def build_keyboard(start_only=False) -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопками."""
    if start_only:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Начать опрос", callback_data="start_survey")],
            [InlineKeyboardButton(text="Тестировать (хороший результат)", callback_data="test_bad")],
            [InlineKeyboardButton(text="Тестировать (плохой результат)", callback_data="test_good")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text=choices[i], callback_data=str(i))] for i in range(len(choices))
        ])


async def start(update: Update, context: CallbackContext) -> int:
    """Приветствие с выбором между опросом и тестированием."""
    global bot_message_id

    bot_message = await update.message.reply_text(
        "Привет! Вы можете пройти опрос и узнать шанс развода в ваших отношениях\n (*так как была малая выборка и машина не разбирается в отношениях, опрос лучше использовать только в развлекательных целях).\n\nВыберите действие:",
        reply_markup=build_keyboard(start_only=True)
    )
    bot_message_id = bot_message.message_id
    return QUESTION


async def start_survey(update: Update, context: CallbackContext) -> int:
    """Начало опроса."""
    global user_answers, bot_message_id
    user_answers = []  # Очистка ответов

    query = update.callback_query
    await query.answer()

    # Отправка первого вопроса
    await query.edit_message_text(
        f"{questions[0]}\n\nОсталось вопросов: {len(questions) - 1}",
        reply_markup=build_keyboard()
    )
    return QUESTION


async def test_bad(update: Update, context: CallbackContext) -> int:
    """Режим тестирования: автоматическое заполнение ответов."""
    global user_answers

    query = update.callback_query
    await query.answer()

    # Генерация тестовых данных
    user_answers = [4,2,3,4,3,0,1,2,3,3,3,2,3,2,1,0,4,2,1,0,2,1,3,3,2,2,2,2,2,2,4,3,3,2,3,3,3,3,4,1,1,2,2,2,2,1,3,2,1,1,2,2,1,3]
  
    # Результат для теста
    return await result(update, context)

async def test_good(update: Update, context: CallbackContext) -> int:
    """Режим тестирования: автоматическое заполнение ответов."""
    global user_answers

    query = update.callback_query
    await query.answer()

    # Генерация тестовых данных
    user_answers = [0,0,0,0,0,0,0,0,0,2,0,1,1,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,1,0,2,0,0,1,0,0,1,0,2,0,1,3,2,0,1,3,3,2,2,1,1,2,0,0]
  
    # Результат для теста
    return await result(update, context)

async def question(update: Update, context: CallbackContext) -> int:
    """Обработка ответов пользователя и редактирование сообщений бота."""
    global user_answers, bot_message_id

    query = update.callback_query
    await query.answer()

    # Сохранение ответа
    user_answers.append(int(query.data))

    # Проверка: закончились ли вопросы
    if len(user_answers) < len(questions):
        await query.edit_message_text(
            f"{questions[len(user_answers)]}\n\nОсталось вопросов: {len(questions) - len(user_answers)}",
            reply_markup=build_keyboard()
        )
        return QUESTION
    else:
        return await result(update, context)


async def result(update: Update, context: CallbackContext) -> int:
    """Расчет результата на основе модели."""
    global user_answers
    all_columns = ['Atr1', 'Atr2', 'Atr3', 'Atr4', 'Atr5', 'Atr6', 'Atr7', 'Atr8', 'Atr9', 'Atr10', 'Atr11', 'Atr12', 'Atr13', 'Atr14', 'Atr15', 'Atr16', 'Atr17', 'Atr18', 'Atr19', 'Atr20', 'Atr21', 'Atr22', 'Atr23', 'Atr24', 'Atr25', 'Atr26', 'Atr27', 'Atr28', 'Atr29', 'Atr30', 'Atr31', 'Atr32', 'Atr33', 'Atr34', 'Atr35', 'Atr36', 'Atr37', 'Atr38', 'Atr39', 'Atr40', 'Atr41', 'Atr42', 'Atr43', 'Atr44', 'Atr45', 'Atr46', 'Atr47', 'Atr48', 'Atr49', 'Atr50', 'Atr51', 'Atr52', 'Atr53', 'Atr54']
    query = update.callback_query
    await query.answer()

    # Удаление клавиатуры с последнего сообщения
    await query.edit_message_text("Подождите, идет расчет результата...")

    # Вычисление вероятностей
    input_data = dict(zip(all_columns, user_answers))

    # Заполняем отсутствующие признаки нулями
    input_df = pd.DataFrame([input_data], columns=all_columns).fillna(0)

    probabilities = model.predict_proba(input_df)[0]  # [P(развод), P(не развод)]
    divorce_chance = probabilities[0] * 100  # Вероятность развода в процентах
    stay_together_chance = probabilities[1] * 100  # Вероятность остаться вместе в процентах

    try:
        with open("answers.txt", "a") as file:
            answers_line = ";".join(map(str, user_answers))
            file.write(f"{answers_line}\n")
    except Exception as e:
        return ConversationHandler.END
    
    await query.edit_message_text(
        f"Опрос завершен!\n"
        f"Шанс развода: {divorce_chance:.2f}%\n"
        f"Шанс остаться вместе: {stay_together_chance:.2f}%\n\n"
        f"Хотите пройти опрос заново? Отправьте команду /start."
    )
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Отмена опроса."""
    await update.message.reply_text("Опрос отменен. До свидания!")
    return ConversationHandler.END


def main():
    """Запуск бота."""
    # Создание приложения
    application = Application.builder().token("7865995370:AAGWNitB93Y6wKKBOSKyclGSsZyLO3lcwT8").build()

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUESTION: [
                CallbackQueryHandler(start_survey, pattern="^start_survey$"),
                CallbackQueryHandler(test_good, pattern="^test_good$"),
                CallbackQueryHandler(test_bad, pattern="^test_bad$"),
                CallbackQueryHandler(question),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Запуск long-polling
    application.run_polling()


if __name__ == "__main__":
    main()