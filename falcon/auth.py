import json
import base64
from jwt import encode, decode, exceptions
from datetime import datetime, timedelta
from falcon.uri import parse_query_string
from falcon import Request, Response, API, HTTP_200, HTTP_201, HTTP_204, HTTP_400, HTTP_401, HTTP_409, HTTPNotImplemented, HTTPUnauthorized

SECRET = "secret"
users = [{"username":'marius', "password":'marius', "profile_picture": "xxx"}]
        
class Auth:
    def __validate_auth_credentials(self, encoded_param):
        username, password = base64.b64decode(encoded_param).decode("UTF-8").split(":")
        return {"username": username, "password": password}

    def __user_exists(self, credentials):
        username = credentials["username"]
        password = credentials["password"]

        user_found = next(filter(lambda x: x["username"] == username, users))
        if user_found is None:
            return False

        if user_found["password"] != password:
            return False
        return True

    def __generate_jwt(self, username):
        expiration_time = datetime.utcnow() + timedelta(minutes=30)
        token_payload = {'user': username, 'exp': expiration_time}
        token = encode(token_payload, SECRET)
        decoded_token = token.decode('UTF-8')
        return decoded_token

    def on_get(self, req: Request, res: Response):
        if req.auth is None:
            raise HTTPNotImplemented('Not Implemented', 'Use Basic Auth method!')
        
        auth_type, encoded_str = req.auth.split(' ')
        if auth_type.lower() != 'basic':
            raise HTTPUnauthorized("Unauthorized")

        credentials = self.__validate_auth_credentials(encoded_str)
        user_exists = self.__user_exists(credentials)

        if user_exists is False:
            raise HTTPUnauthorized("Unauthorized")

        username = credentials["username"]
        token = self.__generate_jwt(username)
        
        res.status = HTTP_200
        res.body = json.dumps({'token': token})

class User:
    def __validate_token(self, token):
        try:
            jwt_payload = decode(token, SECRET, algorithms=["HS256"])
            return jwt_payload
        except exceptions.ExpiredSignatureError:
            raise HTTPUnauthorized('Invalid Credentials', 'Token has been expired')
        except:
            raise HTTPUnauthorized('Invalid Credentials', 'Invalid token')
    
    def __get_user(self, username):
        user = next(filter(lambda x: x["username"] == username, users))

        return {"username": user["username"], "profile_picture":user["profile_picture"]}
    
    def __find_user(self, username): 
        user = list(filter(lambda x: x["username"] == username, users))
        return user[0] if len(user) > 0 else None

    def __username_is_available(self, username):
        user = self.__find_user(username)
        return True if user == None else False

    def __insert_user(self, username, password):
        users.append({"username": username, "password":password})

    def on_get(self, req: Request, res: Response):
        if req.auth is None:
            raise HTTPNotImplemented('Not Implemented', 'Use Basic Auth method!')

        auth_type, token = req.auth.split(' ')
        if auth_type.lower() != 'bearer':
            raise HTTPUnauthorized("Unauthorized")

        jwt_payload = self.__validate_token(token)

        user = self.__get_user(jwt_payload["user"])

        res.status = HTTP_200
        res.body = json.dumps(user)

    def on_post(self, req: Request, res: Response):
        username = req.media.get("username")
        password = req.media.get("password")
        print(username, password)
        if username == None or password == None:
            res.status = HTTP_401
            res.body = json.dumps({"error":True, "message": "One or more required params were not provided!"})
            return
        
        username_is_available = self.__username_is_available(username)
        print(username_is_available)
        if username_is_available == False:
            res.status = HTTP_409
            res.body = json.dumps({"error":True, "message": "Username already in use!"})
            return
        
        self.__insert_user(username, password)

        res.status = HTTP_201
        res.body = json.dumps({"success": True})