import sys

from flask_script   import Manager
from app            import create_app
from flask_twisted  import Twisted
from twisted.python import log
from flask_socketio import SocketIO, send



if __name__ == "__main__":
    app, socket_io = create_app()
    twisted = Twisted(app)
    log.startLogging(sys.stdout)

    
    app.logger.info(f"Running the app...")
    manager = Manager(app)
    #manager.run()
    socket_io.run(app,host='0.0.0.0',port=5000)