import logging
import os

from telegram import Update
from telegram import __version__ as tg_ver

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ConversationHandler,
)

from constants import API_KEY
from db.database import (
    show_all_collective_recipes,
    add_new_user_recipe_in_db,
    select_last_recipe_id_added,
    add_new_user_step_recipe_in_db,
    show_all_user_recipes,
    dell_recipe,
    dell_recipe_steps
)
from step_actions import Steps

# check telegram version before initializing and starting the app
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This program is not compatible with your current PTB version {tg_ver}"
    )

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)  # TODO use this logger for functions

SHOW_RECIPE, SHOW_RECIPE_INFO, SHOW_USER_RECIPE = range(3)
ADD_USER_RECIPE, ADD_USER_RECIPE_STEP = range(2)
DEL_RECIPE_INFO, DEL_RECIPE = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inform user about what this bot can do"""
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'm a bot happy cook! You can see collective recipes "
                                        ""
                                        "/all_recipes or add yours /add. Click /info to see illustrated instruction"
                                        "or press 'menu' button to see all command")


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inform user how to use this bot"""
    pic = os.path.expanduser("pic/picture.png")
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(pic, 'rb'))


async def show_all_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all collective recipes"""
    recipes = show_all_collective_recipes()
    # TODO: remove duplicate
    for recipe in recipes:
        recipe = str(recipe[0]) + " - " + recipe[1].replace('[', '').replace(']', '').replace(',', '-')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=recipe)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="send a number of the recipe or press /cancel to cancel =)")

    return SHOW_RECIPE


async def all_user_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all user recipes"""
    us_id = update.message.chat_id
    recipes = show_all_user_recipes(us_id)
    # TODO: remove duplicate
    for recipe in recipes:
        recipe = str(recipe[0]) + " - " + recipe[1].replace('[', '').replace(']', '').replace(',', '-')
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=recipe)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="send a number of the recipe or press /cancel to cancel =)")

    return SHOW_USER_RECIPE


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels and ends the conversation"""
    return ConversationHandler.END


async def add_user_recipe_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new user recipe info"""
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="type your recept name or press /cancel to cancel =)")
    return ADD_USER_RECIPE


async def add_user_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new user recipe"""

    us_id = update.message.chat_id
    user_answer_before_split = update.message.text
    logger.info("adding new recipe for user %s.", us_id)

    matches = ["/cancel"]
    if any(x in user_answer_before_split for x in matches):
        return ConversationHandler.END
    else:
        add_new_user_recipe_in_db(us_id=us_id, user_recipe_name=user_answer_before_split)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Recipe, '{user_answer_before_split}',was added")
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='type each step in separated massage like this /"salt 1 spoon/ and type stop '
                                        'or press /cancel when you finish"')
    return ADD_USER_RECIPE_STEP


async def add_new_user_recipe_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add steps to the last added user recipe"""
    us_id = update.message.chat_id
    step = update.message.text.strip()
    last_recipe_id = select_last_recipe_id_added()
    print(step)
    for item in last_recipe_id:
        last_recipe_id = (int(item[0]))
    matches = ["stop", "Stop", "/close"]
    if any(x in step for x in matches):
        add_new_user_step_recipe_in_db(user_recipe_id=last_recipe_id, step=step, us_id=us_id)
        return ADD_USER_RECIPE_STEP
    else:
        return ConversationHandler.END


async def del_recipe_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete user recipe info"""
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='type id recipe that you want to delete')
    return DEL_RECIPE


async def dell_user_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete user recipe"""
    id = update.message.chat_id
    id = int(id)
    us_id = update.message.text
    us_id = int(us_id)
    dell_recipe_steps(us_id, id)
    dell_recipe(us_id)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f'recipe {us_id} was deleted')
    return ConversationHandler.END


if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    info_handler = CommandHandler('info', info)
    application.add_handler(info_handler)

    add_new_user_recipe_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_user_recipe_info)],
        states={
            ADD_USER_RECIPE: [
                MessageHandler(filters.TEXT | filters.Dice.ALL, add_user_recipe),
            ],
            ADD_USER_RECIPE_STEP: [
                MessageHandler(filters.TEXT | filters.Dice.ALL, add_new_user_recipe_step),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
        name='add_new_user_recipe',
        persistent=False,
    )
    application.add_handler(add_new_user_recipe_handler)

    all_recipes_handler = ConversationHandler(
        entry_points=[CommandHandler("all_recipes", show_all_recipes)],
        states={
            SHOW_RECIPE: [
                MessageHandler(filters.Regex(r'\d+'), Steps.show_all_steps_in_recipe),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
        name='show_all_recipes',
        persistent=False,
    )
    application.add_handler(all_recipes_handler)

    my_recipes_handler = ConversationHandler(
        entry_points=[CommandHandler("my_recipes", all_user_recipes)],
        states={
            SHOW_USER_RECIPE: [
                MessageHandler(filters.Regex(r'\d+'), Steps.show_all_steps_in_user_recipe),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
        name='show_all_steps_in_user_recipe',
        persistent=False,
    )
    application.add_handler(my_recipes_handler)

    del_recipe_handler = ConversationHandler(
        entry_points=[CommandHandler("dell_recipe", del_recipe_info)],
        states={
            DEL_RECIPE: [
                MessageHandler(filters.Regex(r'\d+'), dell_user_recipe),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_conversation)],
        name='dell_user_recipe',
        persistent=False,
    )
    application.add_handler(del_recipe_handler)

    register_cancel_handler = CommandHandler('cancel', cancel_conversation)
    application.add_handler(register_cancel_handler)
    application.run_polling()
