import sqlite3

from pathlib import Path


project_path = Path(__file__).parents[2]
db_path = project_path.joinpath("database/rasa.db")


def create_db():

    try:
        con = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(e)
        db_path.parent.mkdir(parents=True)
        con = sqlite3.connect(db_path)
    finally:
        con.close()


def create_table(script_path):
    script_path = project_path.joinpath(f"src/db/scripts/{script_path}")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    with open(script_path, 'r') as sqlite_file:
        sql_script = sqlite_file.read()

    try:
        cur.execute(sql_script)
    except sqlite3.OperationalError as e:
        print(e)
    finally:
        cur.close()
        con.close()


if __name__ == '__main__':
    create_db()

    create_table("sqlite_create_table_command.sql")
