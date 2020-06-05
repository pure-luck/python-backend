import config
import boto3
import botocore

from flask      import Flask
from sqlalchemy import create_engine
from flask_cors import CORS
from flask_socketio import SocketIO, send
from model   import UserDao, StoreDao, OrderDao, CategoryDao, MenuDao
from service import UserService, StoreService, OrderService, CategoryService, MenuService
from view    import create_endpoints

class Services:
    pass

################################
# Create App
################################
def create_app(test_config = None):
    app = Flask(__name__)
    
    cors = CORS(app,resources={r"/*":{"origins":"*"}})

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)

    ## Persistenace Layer
    user_dao  = UserDao(database)
    store_dao = StoreDao(database)
    category_dao = CategoryDao(database)
    menu_dao = MenuDao(database)
    order_dao = OrderDao(database)
    
    ## Business Layer
    s3_client = boto3.client(
        "s3",
        aws_access_key_id     = app.config['S3_ACCESS_KEY'],
        aws_secret_access_key = app.config['S3_SECRET_KEY'],
        region_name='ap-northeast-2'
    )
    services                    = Services
    services.user_service       = UserService(user_dao, app.config, s3_client)
    services.store_service      = StoreService(store_dao, app.config, s3_client)
    services.menu_service       = MenuService(menu_dao, app.config, s3_client)
    services.order_service      = OrderService(order_dao)
    services.category_service   = CategoryService(category_dao)
    socket_io=SocketIO(app,cors_allowed_origins="*")
    ## 엔드포인트들을 생성
    create_endpoints(app, services,socket_io)
    

    return app, socket_io