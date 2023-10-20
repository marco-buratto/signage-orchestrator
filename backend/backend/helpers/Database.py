class Database:
    @staticmethod
    def asDict(cursor) -> list:
        # Returns all rows from a cursor as a dict.
        r = []
        columns = []

        if cursor:
            for col in cursor.description:
                columns.append(col[0])

            for row in cursor.fetchall():
                r.append(dict(zip(columns, row)))

        return r
