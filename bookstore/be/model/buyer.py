# import sqlite3 as sqlite
import pymongo
from pymongo.errors import PyMongoError

import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, 
        user_id: str, 
        store_id: str, 
        id_and_count: [(str, int)]
    ) -> (int, str, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            total_price = 0
            order_details = []
            store_collection = self.db["store"]
            order_id = uid

            for book_id, count in id_and_count:
                single_store_info = store_collection.find_one({"sid": store_id, "bid": book_id})
                if not single_store_info:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = single_store_info['stock_level']
                if stock_level < count:
                    # No enough supplement
                    return error.error_stock_level_low(book_id) + (order_id,)

                price = single_store_info['price']
                total_price += price * count

                # Update the stock level
                result = store_collection.update_one(
                    {"_id": single_store_info['_id'], "stock_level": {"$gte": count}},
                    {"$inc": {"stock_level": -count}}
                )
                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                order_details.append({
                    "oid": order_id,
                    "bid": book_id,
                    "count": count,
                    "price": price,
                })

            self.db.order.insert_one({
                "oid": order_id,
                "uid": user_id,
                "sid": store_id,
                "state": "Pending",  # assuming the initial state
                "total_price": total_price,  # if you want to store total price
            })

            # Insert order details
            if order_details:
                self.db.order_detail.insert_many(order_details)

        except PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order_collection = self.db["order"]
            user_collection = self.db["user"]
            order_detail_collection = self.db["order_detail"]

            # Check if the order exists
            order = order_collection.find_one({"oid": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)
            
            if order["uid"] != user_id:
                return error.error_authorization_fail()
            
            # Validate user credentials and get user's balance
            user = user_collection.find_one({"uid": user_id})
            if user is None or user["password"] != password:
                return error.error_authorization_fail()

            # Get the seller's information
            store_collection = self.db["store"]
            store = store_collection.find_one({"sid": order["sid"]})
            if store is None:
                return error.error_non_exist_store_id(order["sid"])
            seller_id = store["owner"]

            # Check if the seller exists
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # Calculate total price
            total_price = order.get("total_price", 0)

            # Check if the buyer has enough funds
            if user["balance"] < total_price:
                return error.error_not_sufficient_funds(order_id)

            # Proceed with payment transaction
            # Start a session and a transaction to ensure atomicity
            # with self.db.client.start_session() as session:
            #     with session.start_transaction():
            # Deduct balance from buyer
            update_result = user_collection.update_one(
                {"uid": user_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}},
                # session=session
            )
            if update_result.modified_count == 0:
                raise pymongo.errors.OperationFailure("Not enough funds")

            # Add balance to seller
            update_result = user_collection.update_one(
                {"uid": seller_id},
                {"$inc": {"balance": total_price}},
                # session=session
            )
            if update_result.modified_count == 0:
                raise pymongo.errors.OperationFailure("Seller user update failed")

            # Update order status
            update_result = order_collection.update_one(
                {"oid": order_id},
                {"$set": {"state": "ToShip"}},
                # session=session
            )
            if update_result.modified_count == 0:
                raise pymongo.errors.OperationFailure("Order update failed")
            
        except pymongo.errors.PyMongoError as e:
            return 528, f"MongoDB error: {str(e)}"
        except Exception as e:
            # print(f"Unexpected error: {str(e)}")
            return 530, f"Unexpected error: {str(e)}"

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user_collection = self.db["user"]

            user = user_collection.find_one({"uid": user_id}, {"_id": 0, "password": 1, "balance": 1})
            if user is None:
                return error.error_non_exist_user_id(user_id)
            
            if user['password'] != password:
                return error.error_authorization_fail()

            # Update the user's balance
            result = user_collection.update_one(
                {"uid": user_id},
                {"$inc": {"balance": add_value}}
            )
            
            if result.modified_count == 0:
                # If no document has been modified, the user_id does not exist
                return error.error_non_exist_user_id(user_id)

        except Exception as e:
            return 528, f"Unexpected error: {str(e)}"
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    
    def confirm(self, user_id: str, password: str, order_id: str) -> (int, str):
        """
        1. Check userid, password, orderid
        2. Check order state, is it Shipped or not?
        3. Set order state to be Received.

        """
        try:          
            order_collection = self.db["order"]
            user_collection = self.db["user"]
            
            # Check if the order exists
            order = order_collection.find_one({"oid": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)
            
            if order["uid"] != user_id:
                return error.error_authorization_fail()
            
            if order["state"] != "Shipped":
                return error.error_wrong_state(order_id)
            
            # Validate user credentials and get user's balance
            user = user_collection.find_one({"uid": user_id})
            if user is None or user["password"] != password:
                return error.error_authorization_fail()
            
            # set the state of `order` to be Received
            update_result = order_collection.update_one(
                {"oid": order_id}, 
                {"$set": {"state": "Received"}})
            
            if update_result.modified_count == 0:
                raise pymongo.errors.OperationFailure("Order update failed")

        except PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    def list_orders(self, user_id: str, password: str) -> (int, str, list):
        return 200, "ok", []
    
    def cancel(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:          
            order_collection = self.db["order"]
            user_collection = self.db["user"]
            
            # Check if the order exists
            order = order_collection.find_one({"oid": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)
            
            if order["uid"] != user_id:
                return error.error_authorization_fail()
            
            # Validate user credentials and get user's balance
            user = user_collection.find_one({"uid": user_id})
            if user is None or user["password"] != password:
                return error.error_authorization_fail()
            
            # set the state of `order` to be Received
            update_result = order_collection.update_one(
                {"oid": order_id}, 
                {"$set": {"state": "Cancelled"}})
            
            if update_result.modified_count == 0:
                raise pymongo.errors.OperationFailure("Order update failed")

        except PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e))
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e))
        return 200, "ok"

