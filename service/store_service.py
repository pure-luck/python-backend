import os
import jwt
import bcrypt
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image
from werkzeug.utils import secure_filename

class StoreService:
    def __init__(self,store_dao, config, s3_client):
        self.store_dao = store_dao
        self.config   = config
        self.s3       = s3_client

    def create_new_store(self,new_store): 
        self.store_dao.insert_store(new_store)
        if ('pic' not in new_store):
            new_store['img_url'] = 'http://python-backend.s3.ap-northeast-2.amazonaws.com/default_image.png'
            self.store_dao.save_store_picture(new_store['img_url'],new_store['id'],new_store['name'])
        else :
            store = new_store
            if 'name' not in store:
                return 'store_name is missing', 404
            filename = (store['name'])
            f=BytesIO()
            im=Image.open(store['pic'])
            size = (900, 900)
            im.thumbnail(size)
            im.save(f,'png')
            f.seek(0)
            img_url=f"store-img/{store['id']}/"+filename+'.png'
            store['img_url']=img_url
            self.save_store_picture(f,img_url,new_store['id'],new_store['name'])
        return '', 200
    
    def update_store_info(self, store):
        if ('pic' not in store):
            store['img_url'] = self.get_store_picture(store)
            self.store_dao.update_store_info(store)
        else :
            if 'name' not in store:
                return 'store_name is missing', 404
            old_store=dict(store)
            old_store['name'] = store['old_name']
            old_picture = (self.store_dao.get_store_picture(old_store))[39:]
            if(old_picture!='default_image.png'):
                self.s3.delete_object(Bucket=self.config['S3_BUCKET'],Key=old_picture)
            filename = (store['name'])
            f=BytesIO()
            im=Image.open(store['pic'])
            size = (900, 900)
            im.thumbnail(size)
            im.save(f,'png')
            f.seek(0)
            img_url=f"store-img/{store['id']}/"+filename+'.png'
            store['img_url']=img_url
            self.store_dao.update_store_info(store)
            self.save_store_picture(f,img_url,store['id'],store['name'])
        
        return '', 200
    
    def del_store(self,store):
        key = (self.store_dao.get_store_picture(store))[39:]
        self.s3.delete_object(
                Bucket=self.config['S3_BUCKET'],
                Key=key
            )
        return self.store_dao.del_store(store)

    def get_stores(self,user_id):
        return self.store_dao.get_stores(user_id)

    def get_store_info(self,store):
        return self.store_dao.get_store_info(store)

    def save_store_picture(self, picture, filename, user_id, store_name):
        self.s3.upload_fileobj(
            picture,
            self.config['S3_BUCKET'],
            filename
        )
        
        image_url = f"{self.config['S3_BUCKET_URL']}{filename}"
        return self.store_dao.save_store_picture(image_url, user_id, store_name)

    def del_stores(self, user_id):
        keys=self.get_stores(user_id)
        if not keys : keys=[]
        for i in keys:
            key=i['img_url'][39:]
            self.s3.delete_object(
                Bucket=self.config['S3_BUCKET'],
                Key=key
            )
        
        self.store_dao.del_stores(user_id)

    def get_store_picture(self, store):
        return self.store_dao.get_store_picture(store)

    def get_all_stores(self):
        return self.store_dao.get_all_stores()