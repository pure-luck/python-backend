import os
import jwt
import bcrypt

from datetime import datetime, timedelta

class CategoryService:
    def __init__(self,category_dao):
        self.category_dao = category_dao
    
    def insert_category(self,new_category):
        self.category_dao.insert_category(new_category)

    def del_category(self,category):
        self.category_dao.del_category(category)

    def update_category(self,category):
        category['name']=category['new_name']
        if category['old_name']!=category['new_name'] and self.category_dao.get_category(category):
            return False
        self.category_dao.update_category(category)
        return True
    
    def get_categories(self,category):
        return self.category_dao.get_categories(category)

    def get_category(self, category):
        return self.category_dao.get_category(category)
    
    def del_categories(self,store):
        self.category_dao.del_categories(store)

    def del_categories_with_id(self,user_id):
        self.category_dao.del_categories_with_id(user_id)