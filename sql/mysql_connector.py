# import mysql.connector
# from user import User
#
#
# class Database:
#     def __init__(self) -> None:
#         # self.db = mysql.connector.connect(host = "sherriice.mysql.pythonanywhere-services.com",
#         #                                   user = "sherriice",
#         #                                   password = "nHCp6XXaRr8MiC.",
#         #                                   database = "sherriice$users")
#
#         self.db = mysql.connector.connect(host = "localhost",
#                                           user = "root",
#                                           password = "nHCp6XXaRr8MiC.",
#                                           database = "bot_users")
#         self.cursor = self.db.cursor()
#
#     def get_user_by_id(self, id: int) -> User:
#         print(f"Getting user id... ID : {id}")
#         sql = f"(SELECT * FROM customers WHERE id ='{id}')"
#         self.cursor.execute(sql)
#         founded = self.cursor.fetchall()
#         print("Founded", founded)
#         return User(founded[0][0], founded[0][1]) if len(founded) > 0 else None
#
#     def insert_new_user(self, user: User) -> None:
#         print("Adding new user...")
#         sql = "INSERT INTO customers (id, username) VALUES (%s, %s)"
#         val = (user.id, user.name)
#         self.cursor.execute(sql, val)
#         self.db.commit()
#         print(self.cursor.rowcount, "record inserted.")
