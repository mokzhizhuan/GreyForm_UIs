import logging
import requests
import base64
import json
import warnings


warnings.filterwarnings("ignore")
userpass = "Default User:robotics"
encoded = base64.b64encode(userpass.encode())
auth = f"Basic {encoded.decode()}"
HEADERS = {
    "Accept": "application/hal+json;v=2.0",
    "Content-Type": "application/x-www-form-urlencoded;v=2.0",
    "Authorization": auth,
}
FORMAT = "%(asctime)-25s %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger("RWS")


def login(conn, proto="https://", host="192.168.1.200"):
    try:
        resp = conn.get(proto + host, headers=HEADERS, verify=False)
        logger.info(f"Login Done, Status Code:{resp.status_code}")
    except Exception as e:
        logger.info("Error:{}".format(e))


def get_request(conn, uri, proto="https://", host="192.168.1.200"):
    try:
        resp = conn.get(proto + host + uri, headers=HEADERS, verify=False)
        logger.info(f"Status Code:{resp.status_code}")
        if resp.json():
            print(json.dumps(resp.json(), indent=2))
        else:
            print(resp.text)
    except Exception as e:
        logger.info("Error:{}".format(e))


if __name__ == "__main__":
    conn = requests.Session()
    login(conn)
    print("---")
    get_request(conn, "/rw/motionsystem/mechunits/ROB_1/jointtarget")
    conn.close()
    # /rw/motionsystem/mechunits/ROB_1/robtarget ---> end-effector pose in xyz (mm) + quat (rad)
    # /rw/motionsystem/mechunits/ROB_1/jointtarget -> joint values in degrees
