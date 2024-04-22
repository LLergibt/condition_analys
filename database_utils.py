import sqlite3
#from sqlmodel import Field, Session, SQLModel, create_engine, select


#from typing import Optional

#engine = create_engine("sqlite:///condition.db")


#class users(SQLModel, table=True):
#    id: int = Field(primary_key=True)
#    name: str
#    current_day: int
#    since_last: Optional[int] = None
#class questions(SQLModel, table=True):
#    id: int = Field(primary_key=True)
#    data: str
#class days(SQLModel, table=True):
#    id: int = Field(primary_key=True)
#    question_id: int
#    current_day: int
#    since_last: Optional[int] = None
#class users_average(SQLModel, table=True):
#    user_id: int
#    total_rate: int
#    param_rate: int
#    param_two_rate: int



class DB():
    def __init__(self):
        self.con = sqlite3.connect("conditon.db")
        self.cur = self.con.cursor()
    def create_relations(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS users(tg_user_id INTEGER UNIQUE , name TEXT NOT NULL, current_day INTEGER, since_last DATE DEFAULT NULL)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS questions(id INTEGER UNIQUE PRIMARY KEY , data TEXT NOT NULL)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS days(day_number INTEGER NOT NULL, question_id INTEGER,  FOREIGN KEY(question_id) REFERENCES questions(id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS users_average(user_id INTEGER UNIQUE, total_rate INTEGER NOT NULL, param_rate INTEGER, param_two_rate INTEGER, FOREIGN KEY(user_id) REFERENCES users(tg_user_id))")
        self.cur.execute("CREATE TABLE IF NOT EXISTS param_suggestions(id INTEGER UNIQUE, rate INTEGER NOT NULL, data TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS param_two_suggestions(id INTEGER UNIQUE, rate INTEGER NOT NULL, data TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS total_suggestions(id INTEGER UNIQUE, rate INTEGER NOT NULL, data TEXT)")

    def isRegistred(self, user_id):
        user_id = self.cur.execute(f'SELECT * from users WHERE tg_user_id={user_id}')
        data = user_id.fetchone()
        return bool(data)
    def get_daily_questions(self, current_day):
        user_id = self.cur.execute('SELECT data  from questions   WHERE id<=? and id >=?', (int(current_day)*7, (int(current_day)*7)-6))
        data = user_id.fetchall()
        print(data)
        return data

    def register_user(self, user_id, username):
        try: 
            self.cur.execute(f"INSERT INTO users (tg_user_id, name, current_day) values({user_id}, '{username}', 0)")
            self.cur.execute(f"INSERT INTO users_average (user_id, total_rate) values({user_id}, 0 )")
            self.con.commit()
            return "Вы успешно зачислены на курс!"
        except sqlite3.IntegrityError:
            return "Вы уже проходите курс"
    def delete_user(self, user_id):
        self.cur.execute(f"DELETE FROM users WHERE tg_user_id='{user_id}'")
        self.cur.execute(f"DELETE FROM users_average WHERE user_id='{user_id}'")
        self.con.commit()
    def get_current(self, user_id):
        data = self.cur.execute(f'SELECT current_day from users WHERE tg_user_id={user_id}')
        current_day = data.fetchone()[0]
        return int(current_day)
    def if_last(self, user_id):
        data = self.cur.execute(f'SELECT current_day from users WHERE tg_user_id={user_id}')
        current_day = data.fetchone()[0]
        if int(current_day) == 7:
            data_av = self.cur.execute(f'SELECT * from users_average WHERE user_id={user_id}')
            average = data_av.fetchone()
            message = self.get_suggestions(average[1], average[2], average[3])
            return message 
        else:
            return ""

    def increase_progress(self, user_id, total_rate, param_rate=0, param_two_rate=0):
        data = self.cur.execute(f'SELECT current_day from users WHERE tg_user_id={user_id}')
        current_day = data.fetchone()[0]
        data_av = self.cur.execute(f'SELECT * from users_average WHERE user_id={user_id}')
        average = data_av.fetchone()
     #   print(current_day, average)
        self.cur.execute("UPDATE users set current_day=? where users.tg_user_id=?", (int(current_day)+1, user_id) )
        if int(current_day)>0:
            total_rate=round((average[1]+total_rate) / 2)
            param_rate=round((param_rate+average[2])/2) if average[2]>0 else param_rate 
            print(param_rate)
            param_two_rate=round((param_two_rate+average[3])/2) if average[3]>0 else param_two_rate
        self.cur.execute(f"UPDATE users_average set total_rate=? where user_id=?", (total_rate, user_id))
        self.cur.execute(f"UPDATE users_average set param_rate=? where user_id=?", (param_rate, user_id))
        self.cur.execute(f"UPDATE users_average set param_two_rate=? where user_id=?", (param_two_rate, user_id))
        self.con.commit()
    def get_suggestions(self, total_rate, param_rate, param_two_rate):
        print(total_rate, param_rate, param_two_rate)
        total = self.cur.execute(f'SELECT data from total_suggestions where rate={total_rate}')
        total = total.fetchone()[0]
        param = self.cur.execute(f'SELECT data from param_suggestions WHERE rate={param_rate}')
        param = param.fetchone()[0]
        param_two = self.cur.execute(f'SELECT data from param_two_suggestions WHERE rate={param_two_rate}')
        param_two = param_two.fetchone()[0]
        return f"{total}. {param}. {param_two}"









