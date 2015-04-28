from flask import Blueprint
from parse_rest.datatypes import Object
from parse_rest.connection import register

setup = Blueprint('setup', __name__)

# class FaceFa(Object):
    # pass

APPLICATION_ID = "h2Co5EGV2YoBuPL2Cl7axkcLE0s9FNKpaPcpSbNm"
REST_API_KEY = "o59euguskg7BBNZlFEuVxTNL0u93glStq7memfVH"

register(APPLICATION_ID, REST_API_KEY)

# gameScore = FaceFa(what=2, ass=1337, poop='shit', yolo=False)
# gameScore.save()
