import os
import jwt
import bcrypt

from datetime import datetime, timedelta

class UserService:
    def __init__(self, user_dao, config, s3_client):       
        self.user_dao = user_dao
        self.config   = config
        self.s3       = s3_client

    def create_new_user(self, new_user):      
        new_user['password'] = bcrypt.hashpw(  
            new_user['password'].encode('UTF-8'),
            bcrypt.gensalt()
        )

        new_user_id = self.user_dao.insert_user(new_user)
        
        return new_user_id

    def login(self, credential):
        ID              = credential['id']
        password        = credential['password']
        self.user_dao.del_blacklist(ID)
        user_credential = self.user_dao.get_user_id_and_password(ID)
        authorized = user_credential and bcrypt.checkpw(password.encode('UTF-8'), user_credential['hashed_password'].encode('UTF-8'))
        return authorized

    def generate_access_token(self, user_id):
        payload = {     
            'user_id' : user_id,
            'exp'     : datetime.utcnow() + timedelta(seconds = 60 * 60 * 24)
        }
        token = jwt.encode(payload, self.config['JWT_SECRET_KEY'], 'HS256') 

        return token.decode('UTF-8')

    def get_user_id_and_password(self, ID):
        return self.user_dao.get_user_id_and_password(ID)

    def get_user(self,ID):
        return self.user_dao.get_user(ID)

    def del_user(self,ID):
        return self.user_dao.del_user(ID)

    def logout(self,ID):
        return self.user_dao.insert_blacklist(ID)
    
    def chk_blacklist(self,ID):
        return self.user_dao.chk_blacklist(ID)

