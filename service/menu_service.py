import os
import jwt
import bcrypt
import json
from io import BytesIO
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

class MenuService:
    def __init__(self,menu_dao,config,s3_client):
        self.menu_dao = menu_dao
        self.config   = config
        self.s3       = s3_client

    def insert_menu(self, new_menu):
        self.menu_dao.insert_menu(new_menu)
        if ('pic' not in new_menu):
            new_menu['img_url'] = 'http://python-backend.s3.ap-northeast-2.amazonaws.com/default_image.png'
            self.menu_dao.save_menu_picture(menu)
        else : 
            menu = new_menu           
            if 'name' not in menu:
                return 'menu_name is missing', 400

            filename = (menu['name'])
            f=BytesIO()
            im=Image.open(menu['pic'])
            size = (900, 900)
            im=im.resize(size,Image.LANCZOS)
            im.save(f,'png')
            f.seek(0)
            img_url=f"menu-img/{menu['id']}/{menu['store_name']}/{menu['category']}/"+filename+'.png'
            menu['img_url']=img_url
            self.save_menu_picture(f,img_url,menu)

    def update_menu(self, menu):

        if ('pic' not in menu):
            old_menu=dict(menu)
            old_menu['name'] = menu['old_name']
            old_menu['img_url'] = self.menu_dao.get_menu_picture(old_menu)
            self.menu_dao.update_menu(menu)
        else : 
            if 'name' not in menu:
                return 'store_name is missing', 404
            old_menu=dict(menu)
            old_menu['name'] = menu['old_name']
            old_picture = (self.menu_dao.get_menu_picture(old_menu))[39:]
            if(old_picture!='default_image.png'):
                self.s3.delete_object(Bucket=self.config['S3_BUCKET'],Key=old_picture)
            filename = (menu['name'])
            f=BytesIO()
            im=Image.open(menu['pic'])
            size = (900, 900)
            im=im.resize(size,Image.LANCZOS)
            im.save(f,'png')
            f.seek(0)
            img_url=f"menu-img/{menu['id']}/{menu['store_name']}/{menu['category']}/"+filename+'.png'
            menu['img_url']=img_url
            self.menu_dao.update_menu(menu)
            self.save_menu_picture(f,img_url,menu)



    def del_menu(self, menu):
        key = (self.get_menu_picture(menu))[39:]
        if(key!='default_image.png'):
            self.s3.delete_object(Bucket=self.config['S3_BUCKET'],Key=key)
        self.menu_dao.del_menu(menu)

    def del_menus(self,menu):
        urls = self.menu_dao.del_menus(menu)
        if not urls : return None
        for i in urls:
            key=i[39:]
            if(key!='default_image.png'):
                self.s3.delete_object(Bucket=self.config['S3_BUCKET'],Key=key)


    def insert_topping(self, menu):
        self.menu_dao.insert(menu)
    
    def del_topping(self, menu):
        self.menu_dao.del_topping(menu)

    def get_menus(self, category):
        return self.menu_dao.get_menus(category)

    def get_menu_info(self, menu):
        return self.menu_dao.get_menu_info(menu)

    def get_toppings(self, menu):
        return self.menu_dao.get_toppings(menu)

    def get_topping(self,menu):
        return self.menu_dao.get_topping(menu)

    def save_menu_picture(self, picture, filename, menu):
        self.s3.upload_fileobj(
            picture,
            self.config['S3_BUCKET'],
            filename
        )
        menu['img_url'] = f"{self.config['S3_BUCKET_URL']}{filename}"
        self.menu_dao.save_menu_picture(menu)

    def get_menu_picture(self, menu):
        return self.menu_dao.get_menu_picture(menu)

    def update_store_name(self,store):
        self.menu_dao.update_store_name(store)

    def update_category_name(self,category):
        self.menu_dao.update_category_name(category)