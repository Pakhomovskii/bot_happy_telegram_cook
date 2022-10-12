from telegram import Update
from telegram.ext import ContextTypes

from db.database import show_all_steps, show_all_user_steps


class Steps:
    async def show_all_steps_in_recipe(self: Update, context: ContextTypes.DEFAULT_TYPE):
        # TODO improve try catch and errors
        user_answer_before_split = self.message.text
        user_answer_after_split = user_answer_before_split.split(" ")
        first_value_from_user = int(user_answer_after_split[0])

        if len(user_answer_after_split) > 1:
            second_value = user_answer_after_split[1]
            if "." in second_value:
                second_value = float(second_value)
            else:
                second_value = int(second_value)
            steps = show_all_steps(first_value_from_user)
            # TODO: remove duplicate
            for step in steps:
                step = step[0].replace('[', '').replace(']', '')
                step_after_split = step.split(" ")
                index_in_step_after_split = 0
                for i in step_after_split:
                    if i.isnumeric():
                        i = int(i)
                        k = i * second_value
                        k = str(k)
                        step_after_split[index_in_step_after_split] = k
                    index_in_step_after_split += 1
                print(step_after_split)
                step_after_join = " ".join(step_after_split)
                step_after_join.replace('[', '').replace(']', '')
                await context.bot.send_message(chat_id=self.effective_chat.id,
                                               text=step_after_join)
        else:
            steps = show_all_steps(first_value_from_user)
            for step in steps:
                step = step[0].replace('[', '').replace(']', '')
                step_after_split = step.replace('[', '').replace(']', '')
                await context.bot.send_message(chat_id=self.effective_chat.id,
                                               text=step_after_split)

    async def show_all_steps_in_user_recipe(self: Update, context: ContextTypes.DEFAULT_TYPE):
        # TODO improve try catch and errors
        us_id = self.message.chat_id
        user_answer_before_split = self.message.text
        user_answer_after_split = user_answer_before_split.split(" ")
        first_value_from_user = int(user_answer_after_split[0])

        if len(user_answer_after_split) > 1:
            second_value = user_answer_after_split[1]
            if "." in second_value:
                second_value = float(second_value)
            else:
                second_value = int(second_value)
            steps = show_all_user_steps(first_value_from_user, us_id)
            # TODO: remove duplicate
            for step in steps:
                step = step[0].replace('[', '').replace(']', '')
                step_after_split = step.split(" ")
                index_in_step_after_split = 0
                for i in step_after_split:
                    if i.isnumeric():
                        i = int(i)
                        k = i * second_value
                        k = str(k)
                        step_after_split[index_in_step_after_split] = k
                    index_in_step_after_split += 1
                print(step_after_split)
                step_after_join = " ".join(step_after_split)
                step_after_join.replace('[', '').replace(']', '')
                await context.bot.send_message(chat_id=self.effective_chat.id,
                                               text=step_after_join)
        else:
            steps = show_all_user_steps(first_value_from_user, us_id)
            for step in steps:
                step = step[0].replace('[', '').replace(']', '')
                step_after_split = step.replace('[', '').replace(']', '')
                await context.bot.send_message(chat_id=self.effective_chat.id,
                                               text=step_after_split)

