from sqlalchemy import text
import json

class MenuDao:
    def __init__(self, database):
        self.db = database

    def insert_menu(self, menu):
        menu['topping']=str(menu['topping'])
        self.db.execute(text("""
            insert into menus (
                user_id,
                category,
                menu_name,
                img_url,
                price,
                topping,
                description,
                store_name
            ) values (
                :id,
                :category,
                :name,
                '',
                :price,
                cast(:topping as json),
                :description,
                :store_name
            )
        """), menu)

    def get_menus(self, category):
        rows = self.db.execute(text("""
        select * from menus where store_name = :store_name and category = :category and user_id =:id
        """),category).fetchall()
        ret = []
        if not rows: return None
        for i in rows:
            ret.append({
                'name'      :   i['menu_name'],
                'img_url'   :   i['img_url'],
                'price'     :   i['price'],
                'topping'   :   json.loads(i['topping']),
                'description':  i['description']
            })
        return ret


    def get_menu_info(self, menu):
        row = self.db.execute(text("""
            select * from menus where user_id = :id and category = :category and menu_name = :name and store_name = :store_name
        """),menu).fetchone()
        return {
            'name'      :   row['menu_name'],
            'img_url'   :   row['img_url'],
            'price'     :   row['price'],
            'topping'   :   json.loads(row['topping']),
            'description':  row['description']
        } if row else None

    def update_menu(self,menu):
        self.db.execute(text("""
            update menus set 
            menu_name = :name,
            img_url = :img_url,
            price = :price,
            topping = cast(:topping as json),
            description = :description
            where user_id = :id and category = :category and menu_name = :old_name and store_name = :store_name
        """), menu)

    def update_store_name(self,store):
        self.db.execute(text("""
            update menus set store_name = :name where user_id = :id and store_name = :old_name
        """),store)

    def update_category_name(self,category):
        self.db.execute(text("""
            update menus set category = :new_name where user_id = :id and store_name = :store_name and category=:old_name
        """),category)

    def insert_topping(self, menu):
        row = self.db.execute(text("""
            update menus set topping = json_array_append(
                topping, 
                '$',
                json_object(
                    "name",:topping_name,
                    "price",:price
                    )
                ) where user_id = :id and category = :category and menu_name = :name and store_name = :store_name
        """),menu)

    def get_toppings(self, menu):
        rows = self.db.execute(text("""
            select toppings from menus where user_id = :id and category = :category and menu_name = :name and store_name :store_name
        """),menu).fetchone()
        if not rows : return None
        else : rows = json.loads(rows)
        ret = []
        for i in rows:
            ret.append({
                'name'  :   i['menu_name'],
                'price' :   i['price']
            })
        return ret if ret else None

    def get_topping(self, menu):
        row = self.db.execute(text("""
            select json_extract(topping,'$[:i]') from menus where user_id =:id and category = :category and menu_name = :name and store_name =:store_name
        """),menu).fetchone()
        return {
            'name'  :   row['menu_name'],
            'price' :   row['price']
        } if row else None
        

    def del_topping(self, menu):
        self.db.execute(text("""
            update menus set topping = json_remove(topping,'$[:i]') from menus where user_id =:id and category = :category and menu_name = :name and store_name =:store_name
        """),menu)


    def del_menu(self, menu):
        row = self.db.execute(text("""
            delete from menus where user_id =:id and category= :category and menu_name = :name and store_name =:store_name
        """),menu)
    
    
    def del_menus(self, menu):
        if menu.get('category'):
            row = self.db.execute(text("""
                select img_url from menus where user_id =:id and category= :category and store_name =:store_name
            """),menu).fetchall()
            self.db.execute(text("""
                delete from menus where user_id =:id and category= :category and store_name =:store_name
            """),menu)
        elif menu.get('store_name'):
            row = self.db.execute(text("""
                select img_url from menus where user_id =:id and store_name = :store_name
            """),menu).fetchall()
            self.db.execute(text("""
                delete from menus where user_id =:id and store_name = :store_name
            """),menu)
        elif menu.get('id'):
            row = self.db.execute(text("""
                select img_url from menus where user_id =:id
            """),menu).fetchall()
            self.db.execute(text("""
                delete from menus where user_id =:id
            """),menu)
        else: row = []
        if not row : return None
        ret =[]
        for i in row:
            ret.append( i['img_url'])

        return ret if ret else None
    
    def save_menu_picture(self,menu):
        self.db.execute(text("""
            update menus set img_url = :img_url where store_name =:store_name and menu_name =:name and user_id =:id and category =:category
        """),menu)

    def get_menu_picture(self,menu):
        ret = self.db.execute(text("""
            select img_url from menus where menu_name = :name and store_name = :store_name and user_id = :id and category = :category
        """),menu).fetchone()
        return ret['img_url'] if ret else None