import os
import jwt
import bcrypt

from datetime import datetime, timedelta

class OrderService:
    def __init__(self,order_dao):
        self.order_dao = order_dao
        
    def create_new_table(self,new_table):
        self.order_dao.insert_table(new_table)
        return None

    def insert_order(self,table):
        time = self.order_dao.insert_order(table)
        table['time']=time
        self.order_dao.insert_order_history(table)
    
    def del_order(self,order):
        self.order_dao.del_order(order)

    def cancel_order(self,order):
        time,order_lists = self.order_dao.del_order(order)
        time=time.strip('"')
        order['order_lists']=order_lists
        order['time'] = time
        self.order_dao.del_order_history(order)    
    
    def change_table(self,table):
        self.order_dao.change_table(table)

    def del_table(self,table):
        self.order_dao.del_table(table)
    
    def del_tables(self,table):
        self.order_dao.del_tables(table)

    def clear_order(self,table):
        self.order_dao.clear_order(table)

    def get_table(self,table):
        return self.order_dao.get_table(table)

    def get_orders(self,table):
        return self.order_dao.get_orders(table)
    
    def del_order_histories(self,store):
        self.order_dao.del_order_histories(store)

    def get_order_histories(self,store):
        return self.order_dao.get_order_histories(store)

    def del_histories(self,user):
        self.order_dao.del_histories(user)

    def get_order_history_with_date(self,date):
        return self.order_dao.get_order_history_with_date(date)
