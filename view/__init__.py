import jwt
from sqlalchemy     import text 
from flask          import request, jsonify, current_app, Response, g, send_file, render_template, session
from sqlalchemy     import create_engine
from flask.json     import JSONEncoder
from functools      import wraps
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import json
from PIL import Image
from io import BytesIO
import config
## Default JSON encoder는 set를 JSON으로 변환할 수 없다.
## 그러므로 커스텀 엔코더를 작성해서 set을 list로 변환하여 
## JSON으로 변환 가능하게 해주어야 한다.

database = create_engine(config.DB_URL, encoding = 'utf-8', max_overflow = 0)
password_string='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-=_+'
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)

#########################################################
#       Decorators
#########################################################
def login_required(f):      
    @wraps(f)                   
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization') 
        if access_token is not None:  
            try:
                payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256') 
            except jwt.InvalidTokenError:
                payload = None     
            if payload is None: return '', 404
            user_id   = payload['user_id']  
            g.user_id = user_id
            g.token = access_token
            row = database.execute(text("""
                select id from blacklists where id =:id
            """),{'id':access_token}).fetchone()
            if row : return '', 401
            row = database.execute(text("""
                select id from blacklists where id =:id
            """),{'id':user_id}).fetchone()
            if row : return '', 404
        else:
            return '',401  
        return f(*args, **kwargs)
    return decorated_function

def create_endpoints(app, services,socket_io):
    app.json_encoder = CustomJSONEncoder
    user_service  = services.user_service
    store_service = services.store_service
    category_service = services.category_service
    menu_service = services.menu_service
    order_service = services.order_service

    @app.route("/ping", methods=['GET'])
    def ping():
        return 'pong'

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = dict(request.json)
        if 'id' not in new_user:
            return 'no id',400
        elif 'password' not in new_user:
            return 'no password',400
        elif 'email' not in new_user:
            return 'no email',400
        elif 'name' not in new_user:
            return 'no name',400
        elif 'phone_number' not in new_user:
            return 'no phone_number',400
        elif 'birth_date' not in new_user:
            return 'no birth_date',400
        elif 'gender' not in new_user:
            return 'no gender',400

        if user_service.get_user(new_user['id']): return "ID overlap",400
        for i in new_user['password']:
            if not (i in password_string):
                return 'invalid password',400
        new_user_id = user_service.create_new_user(new_user)
        new_user = user_service.get_user(new_user_id)
        
        return jsonify(new_user)
        
    @app.route('/login', methods=['POST'])
    def login():
        credential = request.json
        authorized = user_service.login(credential) 

        if authorized:
            user_credential = user_service.get_user_id_and_password(credential['id'])
            user_id         = user_credential['id']
            token           = user_service.generate_access_token(user_id)
            return jsonify({
                'user_id'      : user_id,
                'access_token' : token
            })
        else:
            return '', 401

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        user_id = g.user_id
        if user_service.logout(g.token):
            return '', 200
        else: 
            return '', 401

    @app.route('/sign-out', methods=['POST'])
    @login_required
    def sign_out():
        user_id = g.user_id
        if user_service.get_user(user_id):
            user=dict()
            user['id']=user_id
            store_service.del_stores(user_id)
            menu_service.del_menus(user)
            order_service.del_tables(user)
            category_service.del_categories_with_id(user_id)
            order_service.del_histories(user)
            user_service.del_user(user_id)
            user_service.logout(user_id)
            return '', 200
        else: 
            return '', 401
    

    @app.route('/user-info', methods=['GET'])
    @login_required
    def get_user_info():
        user_id = g.user_id
        return jsonify(user_service.get_user(user_id))

    @app.route('/store-picture', methods=['POST'])
    @login_required
    def upload_store_picture():
        user_id = g.user_id
        store=dict(request.form)
        store['id'] = user_id
        if 'pic' not in request.files:
            return 'File is missing', 404
        store['pic']=request.files['pic']
        if 'name' not in store:
            return 'store_name is missing', 404
        
        filename = secure_filename(store['name'])
        f=BytesIO()
        im=Image.open(store['pic'].stream._file)
        size = (900, 900)
        im.thumbnail(size)
        im.save(f,'png')
        f.seek(0)
        
        store_service.save_store_picture(f, f"menu-img/{store['id']}/{store['name']}/"+filename+'.png', store['id'],store['name'])

        return '', 200

    @app.route('/store-picture/<string:store_name>', methods=['GET'])
    def get_store_picture(store_name):
        Args = dict(request.args)
        ID = Args.get('id')
        address = Args.get('address')
        store=dict(request.args)
        store['id'] =ID
        store['name']=store_name
        store['address'] = address
        store_picture = store_service.get_store_picture(store)
        if store_picture:
            return jsonify({'img_url' : store_picture})
        else:
            return '', 404

    @app.route('/create-store',methods=['POST'])
    @login_required
    def create_store():
        new_store = dict(request.form)
        new_store['id'] = g.user_id
        if 'pic' in request.files:
            new_store['pic']=request.files['pic']
        if store_service.get_store_info(new_store):return 'store name overlap',400
        store_service.create_new_store(new_store)
        return '', 200

    @app.route('/update-store', methods=['POST'])
    @login_required
    def update_store():
        user_id = g.user_id
        store=dict(request.form)
        store['id'] = user_id
        if 'pic' in request.files:
           store['pic']=request.files['pic']
        if store['old_name']!=store['name'] and store_service.get_store_info(store):return 'store name overlap',400
        store_service.update_store_info(store)
        category_service.update_store_name(store)
        menu_service.update_store_name(store)
        return '', 200

    @app.route('/store-info', methods=['GET'])
    def get_store_info():
        store_dict = dict(request.args)
        ret = store_service.get_store_info(store_dict)
        if ret :return jsonify(ret)
        else: return '',404

    @app.route('/del-store', methods=['POST'])
    @login_required
    def del_store():
        store_dict=dict(request.json)
        store_dict['id'] = g.user_id
        store_service.del_store(store_dict)
        store_dict['store_name']=store_dict['name']
        menu_service.del_menus(store_dict)
        order_service.del_tables(store_dict)
        category_service.del_categories(store_dict)
        order_service.del_order_histories(store_dict)
        return '', 200

    @app.route("/stores", methods=['GET'])
    def get_store():
        ARGS=dict(request.args)
        user_id = ARGS.get('id')
        name = ARGS.get('name')
        if name and user_id: 
            ret = store_service.get_store_info(ARGS)
            if ret:return jsonify(ret)
            else: '', 404
        elif user_id: 
            ret = store_service.get_stores(user_id)
            if ret:return jsonify(ret)
            else: '', 404
        else :
            ret = store_service.get_all_stores()
            if ret:return jsonify(ret) 
            else: '', 404

    @app.route("/create-category", methods=['POST'])
    @login_required
    def create_new_category():
        new_category=dict(request.json)
        new_category['id']=g.user_id
        if category_service.get_category(new_category):
            return 'category name overlap', 400
        category_service.insert_category(new_category)
        ret  = (new_category)
        if ret:return jsonify(ret) 
        else: '', 404

    @app.route("/update-category", methods=['POST'])
    @login_required
    def update_category():
        category = dict(request.json)
        category['id']=g.user_id
        if category_service.update_category(category):
            menu_service.update_category_name(category)
            return '', 200
        else : return 'category name overlap', 400

    @app.route("/categories", methods=['GET'])
    def get_categories():
        a = request.args
        category=dict()
        user_id = a.get('id')
        name = a.get('name')
        store_name = a.get('store_name')
        if user_id: category['id'] = user_id
        if name: category['name'] = name
        if store_name: category['store_name'] = store_name
        if name : 
            ret = category_service.get_category(category)
            if ret:return jsonify(ret) 
            else: '', 404
        elif store_name: 
            ret = category_service.get_categories(category)
            if ret:return jsonify(ret) 
            else: '', 404
        else: return '', 404

    @app.route("/del-category", methods=['POST'])
    @login_required
    def del_category():
        category = dict(request.json)
        category['id'] = g.user_id
        category_service.del_category(category)
        category['category']=category['name']
        menu_service.del_menus(category)
        return '', 200


    @app.route('/menu-picture', methods=['POST'])
    @login_required
    def upload_menu_picture():
        user_id = g.user_id
        menu['id']=user_id
        menu = dict(request.form)
        if 'pic' not in request.files:
            return 'File is missing', 404  
        menu['pic'] = request.files['pic']
        if 'name' not in menu:
            return 'menu name is missing', 404  
        filename = secure_filename(menu['name'])
        f=BytesIO()
        im=Image.open(menu['pic'].stream._file)
        size = (900, 900)
        im.thumbnail(size)
        im.save(f,'png')
        f.seek(0)
        menu_service.save_menu_picture(f, f"menu-img/{menu['id']}/{menu['store_name']}/{menu['category']}/"+filename+'.png', menu)

        return '', 200

    @app.route('/menu-picture/<string:menu_name>', methods=['GET'])
    def get_menu_picture(menu_name):
        Args = dict(request.args)
        ID = Args.get('id')
        store_name = Args.get('store_name')
        category = Args.get('category')
        menu=dict()
        menu['id'] = ID
        menu['name'] = menu_name
        menu['store_name'] = store_name
        menu['category'] = category
        menu_picture = menu_service.get_menu_picture(menu)
        if menu_picture:
            return jsonify({'img_url' : menu_picture})
        else:
            return '', 404    

    @app.route("/create-menu", methods=['POST'])
    @login_required
    def create_new_menu():
        new_menu = dict(request.form)
        new_menu['topping'] = str(new_menu['topping'])
        new_menu['id'] = g.user_id
        if 'pic' in request.files:
            new_menu['pic'] = request.files['pic']
        if menu_service.get_menu_info(new_menu):return 'menu name overlap',400
        menu_service.insert_menu(new_menu)
        return '', 200

    @app.route("/del-menu", methods=['POST'])
    @login_required
    def del_menu():
        menu = dict(request.json)
        menu['id'] = g.user_id
        menu_service.del_menu(menu)
        return '', 200

    @app.route("/update-menu", methods = ['POST'])
    @login_required
    def update_menu():
        menu = dict(request.form)
        menu['topping'] = str(menu['topping'])
        menu['id'] = g.user_id
        if 'pic' in request.files:
            menu['pic'] = request.files['pic']
        if menu['old_name']!=menu['name'] and menu_service.get_menu_info(menu):return 'menu name overlap',400
        menu_service.update_menu(menu)
        return '', 200

    @app.route("/menus", methods=['GET'])
    def get_menus():
        a = dict(request.args)
        user_id = a.get('id')
        store_name = a.get('store_name')
        category = a.get('category')
        menu=dict()
        menu['id']=user_id
        if not user_id : return 'no id', 400
        elif not store_name: return 'no store_name', 400
        elif not category: return 'no category', 400 
        menu['store_name']=store_name
        menu['category'] = category
        ret = menu_service.get_menus(menu)
        if ret:return jsonify(ret)
        else: return '', 404

    @app.route("/insert-topping", methods=['POST'])
    @login_required
    def insert_topping():
        menu = dict(request.json)
        menu['id']=g.user_id
        menu_service.insert_topping(menu)
        return '',200
    
    @app.route("/del-topping",methods=['POST'])
    @login_required
    def del_topping():
        menu = dict(request.json)
        menu['id']=g.user_id
        menu_service.del_topping(menu)
        return '',200

    @app.route("/create-table", methods = ['POST'])
    def create_new_table():
        table = dict(request.json)
        if 'id' not in table:
            return 'missing id', 400
        elif 'password' not in table:
            return 'missing password',400
        credential = dict()
        credential['id']=table['id']
        credential['password']=table['password']
        authorized = user_service.login(credential)     

        if not authorized:
            return 'invalid id pw', 400
        if 'store_name' not in table:
            return 'missing store_name', 400
        elif 'table_number' not in table:
            return 'missing table_number', 400 

        if order_service.get_table(table):
            return 'already existing table', 400
        order_service.create_new_table(table)
        return '',200

    @app.route("/tables", methods = ['GET'])
    def get_tables():
        a = dict(request.args)
        user_id = a.get('id')
        store_name = a.get('store_name')
        table_nubmer = a.get('table_number')
        Orders=dict()
        if user_id: Orders['id'] = user_id
        else: return '',400
        if store_name: Orders['store_name'] = store_name
        else: return '',400
        if table_nubmer: Orders['table_number'] = table_nubmer
        else: return '',400
        ret = order_service.get_table(Orders)
        if ret:return jsonify(ret) 
        else: '', 404

        
    @app.route("/orders", methods = ['GET'])
    def get_orders():
        a = dict(request.args)
        table=dict()
        table['id'] = a.get('id')
        table['store_name'] = a.get('store_name')
        table['table_number'] = a.get('table_number')
        ret = order_service.get_orders(table)
        if ret: return jsonify(ret)
        else: return '', 404

    @app.route("/del-table", methods=['POST'])
    def del_table():

        table = dict(request.json)
        if 'id' not in table:
            return 'missing id', 400
        elif 'password' not in table:
            return 'missing password',400
        
        credential = dict()
        credential['id']=table['id']
        credential['password']=table['password']
        authorized = user_service.login(credential) 

        if not authorized:
            return 'invalid id pw', 400
        if 'store_name' not in table:
            return 'missing store_name', 400
        elif 'table_number' not in table:
            return 'missing table_number', 400 
        order_service.del_table(table)

        return '', 200
    
    @app.route("/change-table",methods=['POST'])
    def change_table():
        table = dict(request.json)
        
        if 'id' not in table:
            return 'missing id', 400
        elif 'password' not in table:
            return 'missing password',400
        
        credential = dict()
        credential['id']=table['id']
        credential['password']=table['password']
        authorized = user_service.login(credential) 

        if not authorized:
            return 'invalid id pw', 400
        if 'store_name' not in table:
            return 'missing store_name', 400
        elif 'current_number' not in table:
            return 'missing current_number', 400 
        elif 'new_number' not in table:
            return 'missing new_number', 400
        elif table['new_number'] == table['current_number']:
            return "number hasn't changed", 400
        old_table=dict(table)
        old_table['table_number']=table['current_number']
        new_table=dict(table)
        new_table['table_number']=table['new_number']
        if order_service.get_table(new_table):
            return 'this number already exists', 400
        order_service.change_table(table)
        return '',200


    @app.route("/del-order", methods=['POST'])
    def del_order():
        order = dict(request.json)
        order_service.del_order(order)
        return '', 200

    @app.route("/cancel-order", methods=['POST'])
    def cancel_order():
        order=dict(request.json)
        order_service.cancel_order(order)
        return '',200

    @app.route("/clear-order", methods=['POST'])
    def clear_order():
        order=dict(request.json)
        order_service.clear_order(order)
        return '',200

    @app.route("/insert-order", methods=['POST'])
    def insert_order():
        table = dict(request.json)
        if not order_service.get_table(table): return '',404
        table['order_lists']=str(table['order_lists']).replace("'",'"')
        order_service.insert_order(table)
        return '', 200

    @app.route("/order-histories", methods=['GET'])
    def get_order_histories():
        a = dict(request.args)
        store = dict()
        store['id']=a.get('id')
        store['store_name']=a.get('store_name')
        ret = order_service.get_order_histories(store)
        return jsonify(ret) if ret else '', 404

    @app.route('/order-history-with-date',methods=['GET'])
    def get_order_histories_with_date():
        date = dict(request.args)
        if 'day' in date:
            if date['month'] < 10:
                date['month']='0'+str(date['month'])
            if date['day'] < 10:
                date['day']='0'+str(date['day'])
            date['start_time']=str(date['year'])+date['month']+date['day']+"000000"
            date['end_time']=str(date['year'])+date['month']+date['day']+"235959"
        elif 'month' in date:
            if date['month'] < 10:
                if date['month'] == 12: nextmonth = 1
                elif date['month'] < 9:
                    nextmonth='0'+str(date['month']+1)
                else : nextmonth=str(date['month']+1)
                date['month']='0'+str(date['month'])
            date['start_time']=str(date['year'])+str(date['month'])+"01000000"
            date['end_time']=str(date['year'])+str(nextmonth)+"01000000"
        else: return '', 400
        order_service.get_order_history_with_date(date)
        return '',200

    @app.route('/chat')
    def chat():
        return render_template('chat.html')

    @socket_io.on("message")
    def request1(message):
        to_client=dict()
        print(message)
        if type(message) is dict :
            to_client['message']=message
            to_client['type'] = 'json'
            send(to_client,broadcast=False)
            return ''
        if(message[0]=='{'):
            to_client['v']= json.loads(message)
        if message == 'table':
            room = session.get('room1')
            to_client['message'] = 'new_table'
            to_client['type'] = 'connect'
        else:
            to_client['message'] = message
            to_client['type']   = 'normal'
        send(to_client,broadcast=False)
        
        return "received!"

    @socket_io.on('connect')
    def connect():
        to_client = dict()
        to_client['message']='who are you?'
        send(to_client)
        emit('identify',to_client,broadcast=False)
        return "who are you?"

    @socket_io.on('disconnect')
    def disconnect():
        print('disconnected')
        return ''

    @socket_io.on('identify')
    def identify(identity):
        username = identity['id']+'/'+identity['store_name']
        if identity['manager']:
            room = username+'/'+'manager'
        else :
            room = username+'/'+'table/'+str(identity['table_number'])
        join_room(room)
        return ''
    
    @socket_io.on('order')
    def order(order_info):
        room=order_info['id']+'/'+order_info['store_name']+'/'+'manager'
        emit('receive-order',order_info,room=room)
        return ''

    @socket_io.on('order-completed')
    def completed(call_info):
        room=call_info['id']+'/'+call_info['store_name']+'/'+'table/'+str(call_info['table_number'])
        emit('call',call_info['order'],room=room)
        return ''

    @app.route('/chata')
    def chata():
        return render_template('chata2.html')

    @app.route('/chatb')
    def chatb():
        return render_template('chat3.html')


    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/store')
    def store():
        return render_template('store.html')

    @app.route('/register')
    def register():
        return render_template('register.html')
