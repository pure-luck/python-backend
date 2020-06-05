from sqlalchemy import text

class StoreDao:
    def __init__(self, database):
        self.db = database

    def insert_store(self, store_info):
        self.db.execute(text("""
            INSERT INTO stores (
                user_id,
                img_url,
                name,
                address
            ) VALUES (
                :id,
                '',
                :name,
                :address
            )
        """),store_info)

    def get_stores(self, user_id):
        rows = self.db.execute(text("""
            select 
                *
            from stores where user_id = :id
        """),id=user_id).fetchall()
        ret = []
        if not rows: return None
        for i in rows:
            ret.append({
                'id' :      i['user_id'],
                'name':     i['name'],
                'address':  i['address'],
                'img_url':  i['img_url']
            })
        return ret

    def get_store_count(self, user_id):
        cnt = self.db.execute(text("""
            select count(*) from stores where user_id = :id
        """),{'id' : user_id})
        return cnt[0]
    
    def update_store_info(self, store):
        self.db.execute(text("""
            update stores set img_url = :img_url, name = :name, address = :address where user_id = :id and name = :old_name
        """),store)
        return {
            'id'    :   store['id'],
            'img_url' : store['img_url'],
            'name'  :   store['name'],
            'address':  store['address']
        } if store else None

    def get_store_info(self,store):
        row = self.db.execute(text("""
            SELECT
                *
            FROM stores
            WHERE user_id = :id and name = :name
        """), store).fetchone()

        return {
            'id'        : row['user_id'],
            'name'      : row['name'],
            'address'   : row['address'],
            'img_url'   : row['img_url']
        } if row else None

    def del_store(self,store):
        row = self.db.execute(text("""
            select * from stores where user_id = :id and name = :name
        """),store).fetchone()
        if not row: return False
        self.db.execute(text("""
        delete from stores where user_id = :id and name = :name
        """),store)
        return True
    
    def del_stores(self,user_id):
        self.db.execute(text("""
            delete from stores where user_id = :id
        """),id = user_id)

    def save_store_picture(self, store_pic_path, user_id, name):
        self.db.execute(text("""
            UPDATE stores
            SET img_url = :store_pic_path
            WHERE user_id = :user_id and name = :name
        """), {
            'user_id'           : user_id,
            'store_pic_path'    : store_pic_path,
            'name'              : name
        })
        return None

    def get_store_picture(self, store):
        row = self.db.execute(text("""
            SELECT img_url
            FROM stores
            WHERE user_id = :id and name = :name
        """), store).fetchone()

        return row['img_url'] if row else None

    def reset_store_picture(self,store):
        store['img_url'] = "http://python-backend.s3.ap-northeast-2.amazonaws.com/default_image.png"
        row =self.db.execute(text("""
            update stores set img_url = :img_url where user_id: = id and name = :name
        """),store)
        return None
    
    def get_all_stores(self):
        rows = self.db.execute(text("""
            select * from stores
        """)).fetchall()
        ret=[]
        if not rows : return None
        for i in rows:
            ret.append({
                'id':       i['user_id'],
                'name':     i['name'],
                'address':  i['address'],
                'img_url':  i['img_url']
            })
        return ret
