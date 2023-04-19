import psycopg2


class PostgresqlControl:

    def __init__(self, password: str, dbname: str = 'rasa', user: str = 'root', host: str = 'localhost', port: int = 5432):
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

    def insert_into_table_commands(self, command):

        query = """
        INSERT INTO commands (command)
        VALUES (%s);
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (command, ))

        self.connection.commit()

    def select_last_n_commands(self, n: int):

        query = """
        SELECT command
        FROM commands
        ORDER BY id DESC
        LIMIT (%s);
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (n, ))
            data = cursor.fetchall()

        return data

    def count_commands(self):

        query = """
        SELECT COUNT (id)
        FROM commands;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()

        return data

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    db = PostgresqlControl(user="root", password="root")
    db.select_last_n_commands(3)
