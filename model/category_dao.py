from sqlalchemy import text

class CategoryDao:
    def __init__(self, database):
        self.db = database
    
    def insert_category(self, category):
        return self.db.execute(text("""
            INSERT INTO categories (
                user_id,
                name,
                store_name
            ) VALUES (
                :id,
                :name,
                :store_name
            )
        """),category).lastrowid

    def get_categories(self, store):
        rows = self.db.execute(text("""
            select 
                * from categories
            where user_id = :id and store_name = :store_name
        """),store).fetchall()
        ret = []
        for i in rows:
            ret.append({
                'id':i['user_id'], 'store_name' : i['store_name'], 'name':i['name']
            })
        return ret if ret else None

    def del_categories(self,store):
        self.db.execute(text("""
            delete from categories where user_id = :id and store_name = :store_name
        """),store)
        return None
    
    def del_categories_with_id(self,user_id):
        self.db.execute(text("""
            delete from categories where user_id = :id
        """),id=user_id)
        return None

    def get_category(self,category):
        row = self.db.execute(text("""
            select name from categories
            where user_id = :id and name = :name and store_name = :store_name
        """),category).fetchone()
        
        return {
            'name' : row['name']
        } if row else None
    
    def update_category(self,category):
        row = self.db.execute(text("""
            update categories set name = :new_name where user_id = :id and name = :old_name and store_name = :store_name
        """),category)

    def update_store_name(self,store):
        row = self.db.execute(text("""
            update categories set store_name = :name where user_id = :id and store_name = :old_name
        """),store)


    def del_category(self, category):
        self.db.execute(text("""
            delete from categories where user_id= :id and name = :name and store_name = :store_name
        """),category).lastrowid