import os
from falcon import API
from openapi_core.shortcuts import create_spec
from openapi_spec_validator.schemas import read_yaml_file
from openapi_core.contrib.falcon.middlewares import FalconOpenAPIMiddleware

from auth import Auth, User

app = None

def main():
    global app
    specfile = './api.yaml'
    specurl = "file://" + os.path.abspath(specfile)
    specdict = read_yaml_file(specfile)
    openapi_spec = create_spec(specdict, spec_url=specurl)

    openapi_middleware = FalconOpenAPIMiddleware.from_spec(openapi_spec)

    app = API(middleware=[openapi_middleware])

    auth_server = Auth()
    user_server = User()

    app.add_route('/user', user_server)
    app.add_route('/token', auth_server)

main()
