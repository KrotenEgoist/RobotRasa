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

    def __del__(self):
        self.cursor.close()
