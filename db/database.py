import sqlite3

conn = sqlite3.connect('db/database', check_same_thread=False)
cursor = conn.cursor()


def show_all_collective_recipes():
    cursor.execute('SELECT * FROM all_recipes')
    return cursor.fetchall()


def show_all_user_recipes(us_id: int):
    cursor.execute('SELECT user_recipe_id, user_recipe_name FROM users_recipes where us_id="%s"' % us_id)
    return cursor.fetchall()


def show_all_steps(all_recipe_id: int):
    cursor.execute('SELECT step FROM recipe_steps WHERE all_recipe_id="%s"' % all_recipe_id)
    return cursor.fetchall()


def show_all_user_steps(user_recipe_id: int, us_id: int):
    cursor.execute("SELECT step FROM user_recipe_steps WHERE user_recipe_id=(?) and us_id=(?)", (user_recipe_id, us_id))
    return cursor.fetchall()


def add_new_user_recipe_in_db(us_id: int, user_recipe_name: str):
    cursor.execute(' INSERT INTO users_recipes(user_recipe_name, us_id) VALUES(?, ?)', (user_recipe_name, us_id))
    conn.commit()


def add_new_user_step_recipe_in_db(user_recipe_id: int, step: str, us_id: int):
    cursor.execute(' INSERT INTO user_recipe_steps(user_recipe_id, step, us_id) VALUES(?, ?, ?)',
                   (user_recipe_id, step, us_id))
    conn.commit()


def dell_recipe_steps(us_id: int, id: int):
    cursor.execute(' DELETE FROM user_recipe_steps WHERE user_recipe_id=(?) and us_id=(?)', (id, us_id))
    conn.commit()


def dell_recipe(us_id: int):
    cursor.execute(' DELETE FROM users_recipes WHERE user_recipe_id="%s"' % us_id)
    conn.commit()


def select_last_recipe_id_added():
    cursor.execute('SELECT user_recipe_id FROM users_recipes ORDER BY user_recipe_id DESC LIMIT 1')
    return cursor.fetchall()
