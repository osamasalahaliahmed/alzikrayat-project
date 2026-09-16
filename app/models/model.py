from app.database import getConnection


class Model:
    @staticmethod
    def fetch(sql, values=(), one=False):
        with getConnection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                if one:
                    return cursor.fetchone()
                return cursor.fetchall()

    @staticmethod
    def execute(sql, values=()):
        with getConnection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                recordId = cursor.lastrowid
            connection.commit()
            return recordId

