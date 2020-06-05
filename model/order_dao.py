from sqlalchemy import text
import json
class OrderDao:
    def __init__(self, database):
        self.db = database

    def insert_table(self, table):
        self.db.execute(text("""
            insert into orders (
                user_id,
                store_name,
                table_number,
                order_lists
            ) values (
                :id,
                :store_name,
                :table_number,
                '[]'
            )
        """), table).lastrowid

    def insert_order(self, order):
        order["order_lists"]=str(order["order_lists"])
        time = self.db.execute(text("""select current_timestamp""")).fetchone()
        order['time']=time[0]
        self.db.execute(text("""
            update orders set order_lists = json_array_append(order_lists, '$', json_object("order",cast(:order_lists as json),'order_time',:time))
            where user_id = :id and table_number = :table_number and store_name = :store_name
        """),order)

        return order['time']
    
    def del_order(self, order):
        time = self.db.execute(text("""
            select json_extract(order_lists,'$[:i].order_time') from orders
            where user_id = :id and table_number = :table_number and store_name = :store_name
        """),order).fetchone()
        order_lists = self.db.execute(text("""
            select json_extract(order_lists,'$[:i].order') from orders
            where user_id = :id and table_number = :table_number and store_name = :store_name
        """),order).fetchone()
        self.db.execute(text("""
            update orders set order_lists = json_remove(order_lists,'$[:i]')
            where user_id = :id and table_number = :table_number and store_name = :store_name
        """),order)
        if not time : return None 
        return time[f"json_extract(order_lists,'$[{order['i']}].order_time')"],order_lists[f"json_extract(order_lists,'$[{order['i']}].order')"]
    
    def get_order(self, order):
        row = self.db.execute(text("""
            select json_extract(order_lists,'$[:i].order_time') from orders
            where user_id = :id and table_number = :table_number and store_name = :store_name
        """),order).fetchone()
        return json.loads(row[f"json_extract(row,'$[{order['i']}].order_time')"]) if row else None

    def clear_order(self, table):
        self.db.execute(text("""
            update orders set order_lists = json_array() where user_id = :id and table_number = :table_number and store_name = :store_name
        """),table)

    def del_table(self,table):
        self.db.execute(text("""
            delete from orders where user_id = :id and table_number = :table_number and store_name = :store_name
        """),table)
        
    def change_table(self,table):
        self.db.execute(text("""
            update orders set table_number =:new_number where table_number = :current_number and store_name =:store_name and user_id=:id
        """),table)

    def del_tables(self,table):
        if table.get('table_number'):
            self.db.execute(text("""
                delete from orders where user_id = :id and table_number = :table_number and store_name = :store_name
            """),table)
        elif table.get('store_name'):
            self.db.execute(text("""
                delete from orders where user_id = :id and store_name = :store_name
            """),table)
        else :
            self.db.execute(text("""
                delete from orders where user_id=:id
            """),table)

    def get_table(self, table):
        row = self.db.execute(text("""
            select * from orders where user_id = :id and table_number = :table_number and store_name = :store_name
        """),table).fetchone()
        if not row:return None
        return {
            'id':row['user_id'], 'table_number': row['table_number'], 'store_name': row['store_name'], 'order_lists':json.loads(row['order_lists'])
        }
        
    def get_tables(self,table):
        if table['table_number']:
            rows = self.db.execute(text("""
                select * from orders where user_id = :id and store_name = :store_name and table_number = :table_number
            """),table).fetchall()
        else:
            rows = self.db.execute(text("""
                select * from orders where user_id = :id and store_name = :store_name order by table_number
            """),table).fetchall()
        ret=[]
        if not rows: return None
        for i in rows:
            ret.append({
                'id':row['user_id'], 'table_number': row['table_number'], 'store_name': row['store_name'], 'order_lists':json.loads(row['order_lists'])
            })
        return ret if ret else None
    
    def get_orders(self,table):
        row = self.db.execute(text("""
            select order_lists from orders where user_id = :id and store_name = :store_name and table_number = :table_number
        """),table).fetchone()
        if not row: return None
        return json.loads(row['order_lists'])

    
    def insert_order_history(self,order):
        self.db.execute(text("""
            insert into order_history(
                user_id,
                store_name,
                table_number,
                orderlist,
                order_time
            ) values(
                :id,
                :store_name,
                :table_number,
                cast( :order_lists as json),
                :time
            )
        """),order) 


    def del_order_history(self,order):
        self.db.execute(text("""
            delete from order_history where user_id =:id and store_name = :store_name and order_time = :time and table_number =:table_number
        """),order)
        print(1)


    def del_order_histories(self,store):
        self.db.execute(text("""
            delete from order_history where user_id =:id and store_name = :store_name
        """),store)

    def get_order_histories(self,store):
        rows = self.db.execute(text("""
            select * from order_history where user_id =:id and store_name = :store_name order by order_time desc
        """).store).fetchall()
        if not rows: return None
        ret=[]
        for i in rows:
            ret.append({
                'id' : i['user_id'], 'store_name' : i['store_name'], 'table_number':i['table_number'],'order_lists':json.loads(i['orderlist']),'time':i['order_time']
            })

        return ret if ret else None
    
    def get_order_history_with_date(self,date):
        if 'day' in date:
            rows = self.db.execute(text("""
                select * from order_history where user_id =:id where order_time >= cast(:start_time as datetime) and order_time <= cast(:end_time as datetime)
            """),date).fetchall()
        else:
            rows = self.db.execute(text("""
                select * from order_history where user_id =:id where order_time >= cast(:start_time as datetime) and order_time < cast(:end_time as datetime)
            """),date).fetchall()
        if not rows: return None
        for i in rows:
            ret.append({
                'id' : i['user_id'], 'store_name' : i['store_name'], 'table_number':i['table_number'],'order_lists':json.loads(i['orderlist']),'time':i['order_time']
            })
        ret = []
        return ret if ret else None

    def del_histories(self,user):
        self.db.execute(text("""
            delete from order_history where user_id =:id
        """),user)