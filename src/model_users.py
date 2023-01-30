# from datetime import timedelta
from typing import Union

from pydantic import BaseModel

from .utility_general import get_default_db_resultset, \
    get_standard_base_exception_msg
from .utility_db import db


# users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "fakehashedsecret",
#         "disabled": False,
#     },
#     "alice": {
#         "username": "alice",
#         "full_name": "Alice Wonderson",
#         "email": "alice@example.com",
#         "hashed_password": "fakehashedsecret2",
#         "disabled": True,
#     },
# }


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


# Low level methods


def fetch_user_by_entryname(entry_name, entry_value, fields={}):
    resultset = get_default_db_resultset()
    # print(f'** DB ** fetch_user_by_entryname: {entry_name} {entry_value}')
    try:
        resultset['resultset'] = db.users.find_one(
            {entry_name: entry_value},
            projection=fields
        )
        resultset['found'] = resultset['resultset'] is not None
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(
            err, 'FUBEN1'
        )
        resultset['error'] = True
    # print(f'** DB ** fetch_user_by_entryname.resultset: {resultset}')
    return resultset
