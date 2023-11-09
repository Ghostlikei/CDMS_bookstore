import logging
import os
from flask import Flask
from flask import Blueprint
from flask import request
from be.view import auth
from be.view import seller
from be.view import buyer
from be.view import search
from be.model.store import init_database

bp_shutdown = Blueprint("shutdown", __name__)
bp_test = Blueprint("test", __name__)
connect_url = "mongodb://userName:daseCDMS2023@110.40.142.252:27017"

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@bp_shutdown.route("/shutdown")
def be_shutdown():
    shutdown_server()
    return "Server shutting down..."

# 可以通过这个测试接口测试功能函数的正确性
@bp_test.route("/test")
def be_test():
    # 这里可以调用功能函数进行测试
    ### res = somefunction()
    # 这里可以设置返回值
    # return f"{res}"

    return "Server test..."

def be_run():
    this_path = os.path.dirname(__file__)
    parent_path = os.path.dirname(this_path)
    log_file = os.path.join(parent_path, "app.log")
    init_database(connect_url)

    logging.basicConfig(filename=log_file, level=logging.ERROR)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    app = Flask(__name__)
    app.register_blueprint(bp_test)
    app.register_blueprint(bp_shutdown)
    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(seller.bp_seller)
    app.register_blueprint(buyer.bp_buyer)
    app.register_blueprint(search.bp_search)
    app.run()
