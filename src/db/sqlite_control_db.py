import sqlite3


class ControlDB:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def insert_into_table_commands(self, command):

        query = """
        INSERT INTO commands (command)
        VALUES (?);
        """
        insert_data = (command, )

        try:
            self.cursor.execute(query, insert_data)
        except sqlite3.OperationalError as e:
            print(e)

        self.connection.commit()

    def select_last_n_commands(self, n: int):

        query = """
        SELECT command
        FROM commands
        ORDER BY id DESC
        LIMIT (?);
        """
        insert_data = (n, )

        try:
            data = self.cursor.execute(query, insert_data).fetchall()
        except sqlite3.OperationalError as e:
            data = None
            print(e)

        self.connection.commit()

        return data

    def count_commands(self):

        query = """
        SELECT COUNT(id)
        FROM commands;
        """

        try:
            data = self.cursor.execute(query).fetchall()
        except sqlite3.OperationalError as e:
            data = None
            print(e)

        self.connection.commit()

        return data

    def __del__(self):
        self.cursor.close()
        self.connection.close()
