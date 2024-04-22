from  dotenv import load_dotenv
import os
from database_utils import DB
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler,filters
import time

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')



async def start(update, context):
    bot = context.bot
    
    await bot.send_message(chat_id=update.effective_chat.id, text="Привет, я могу помочь тебе лучше понять себя. Ты можешь контроллировать меня следующими командами: \n\n /register_course - начать курс \n /continue - продолжить отвечать на ежедневные вопросы \n /show_progress - покажет прогресс прохождения(сколько дней осталось, предварительная оценка состояния) \n /stop - сбросить текущий прогресс", parse_mode="markdown")
async def echo(update, context):
    bot = context.bot
    if 'have_chat' in context.user_data and context.user_data['have_chat']:
        if context.user_data['question_number'] < len(context.user_data['questions']) - 1:
            context.user_data['question_number'] += 1
 #           print(context.user_data['questions'][context.user_data['question_number']])
            c = True
            if context.user_data['question_number'] >= 4 and context.user_data['question_number'] <= 6:
                if update.message.text.isdigit() and int(update.message.text) >= 1 and int(update.message.text) <=10:
                    if context.user_data['question_number'] == 4:
                        context.user_data['param_rate'] = int(update.message.text)
                    if context.user_data['question_number'] == 5:
                        context.user_data['param_two_rate'] = int(update.message.text)

                    if context.user_data['question_number'] == len(context.user_data['questions'])-1:
                    # context.user_data['total_rate'] = int(update.message.text)
                        db.increase_progress(update.message.from_user.id, int(update.message.text),context.user_data['param_rate'], context.user_data['param_two_rate'])
                else:
                    c = False
                    context.user_data['question_number'] -= 1
                    await bot.send_message(chat_id=update.effective_chat.id, text="Ответ должен быть числом от 1 до 10")

            if c:
                await bot.send_message(chat_id=update.effective_chat.id, text=context.user_data['questions'][context.user_data['question_number']][0])

        else:
            await bot.send_message(chat_id=update.effective_chat.id, text="Спасибо за твои ответы. На сегодня это все")
            message = db.if_last(update.message.from_user.id)
            if message != "":
                await bot.send_message(chat_id=update.effective_chat.id, text="Курс окончен. Сейчас вам будет предоставлны рекомендации\n")


                await bot.send_document(chat_id=update.effective_chat.id, document="./loading.mp4")
                time.sleep(3)
                await bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        await bot.send_message(chat_id=update.effective_chat.id, text="Что вы желаете сделать? Используете /start для списка команд")


async def register_user(update, context):
    result = db.register_user(update.message.from_user.id, update.message.from_user.username)
    bot = context.bot
    if result:
        await bot.send_message(chat_id=update.effective_chat.id, text=result)
async def delete_user(update, context):
    result = db.delete_user(update.message.from_user.id)
    print(result, update.message.from_user.id)
    bot = context.bot
    if not result:
        await bot.send_message(chat_id=update.effective_chat.id, text="Успешно удалено")


async def start_daily_conversation(update, context):
    isRegistred = db.isRegistred(update.message.from_user.id)
    bot = context.bot
    if isRegistred:
        if db.if_last(update.message.from_user.id):
            await bot.send_message(chat_id=update.effective_chat.id, text="Курс завершен! \n Используете /stop, если хотите сбросить прогресс")
            return

        context.user_data['question_number'] = 0
        context.user_data['have_chat'] = True
        context.user_data['param_two_rate'] = 0
        context.user_data['param_rate'] = 0  
        current_day = db.get_current(update.message.from_user.id)
        questions = db.get_daily_questions(str(current_day+1))
        context.user_data['questions'] = questions

        await bot.send_message(chat_id=update.effective_chat.id, text=f"День {current_day+1} \n")
        await bot.send_message(chat_id=update.effective_chat.id, text=context.user_data['questions'][context.user_data['question_number']][0])
    else:
        await bot.send_message(chat_id=update.effective_chat.id, text="В данный момент вы не проходите курс, используйте /registercourse, чтобы это исправить")


if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    db = DB()
    db.create_relations()

    
    start_handler = CommandHandler('start', start)
    stop_handler = CommandHandler('stop', delete_user)
    register_handler = CommandHandler('registercourse', register_user)
    continue_handler = CommandHandler('continue', start_daily_conversation)

    application.add_handler(start_handler)
    application.add_handler(stop_handler)
    application.add_handler(register_handler)
    application.add_handler(continue_handler)
    application.add_handler(echo_handler)

    
    application.run_polling()








