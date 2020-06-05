from sqlalchemy import text

class UserDao:
    def __init__(self, database):
        self.db = database
    
    def insert_user(self, user):
        self.db.execute(text("""
            INSERT INTO users (
                id,
                hashed_password,
                email,
                name,
                phone_number,
                birth_date,
                gender
            ) VALUES (
                :id,
                :password,
                :email,
                :name,
                :phone_number,
                :birth_date,
                :gender
            )
        """), user)
        return user['id']

    def get_user_id_and_password(self, Id):
        row = self.db.execute(text("""    
            SELECT
                id,
                hashed_password
            FROM users
            WHERE id = :id
        """), {'id' : Id}).fetchone()

        return {
            'id'              : row['id'],
            'hashed_password' : row['hashed_password']
        } if row else None
    
    def get_user(self, ID):
        row = self.db.execute(text("""    
            SELECT
                *
            FROM users
            WHERE id = :id
        """), {'id' : ID}).fetchone()

        return {
            'id'                : row['id'],
            'hashed_password'   : row['hashed_password'],
            'email'             : row['email'],
            'name'              : row['name'],
            'phone_number'      : row['phone_number'],
            'birth_date'        : row['birth_date'],
            'gender'               : row['gender']
        } if row else None


    def del_user(self, user_id):
        row = self.db.execute(text("""
            select * from users where id = :id
        """),{'id' : user_id}).fetchone()
        if not row : return False
        self.db.execute(text("""
        delete from users where id = :id
        """),{'id' : user_id})
        return True

    def insert_blacklist(self, ID):
        row = self.db.execute(text("""
            select * from blacklists where id = :id
        """),id=ID).fetchone()
        if row: return False
        self.db.execute(text("""
            insert into blacklists(
                id
            ) values(
                :id
            )
        """), {'id': ID})
        return True

    def chk_blacklist(self, ID):
        row = self.db.execute(text("""
            select * from blacklists where id = :id
        """),{'id':ID}).fetchone()
        return True if row else False

    def del_blacklist(self, ID):
        self.db.execute(text("""
            delete from blacklists where id = :id
        """),{'id': ID})
        return None