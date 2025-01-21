import json
import time
import http.client
from datetime import datetime


class HttpConnection():

    def __init__(self, logger, address, auth, api_prefix):
        self.logger = logger
        self.api_prefix = api_prefix
        self.http_headers = {
            "Accept-Language": "en-EN",
            "Authorization": auth,
            "Content-Type": "application/json"}
        try:
            self.connection = http.client.HTTPConnection(
                host=address, timeout=5)
        except Exception as e:
            self.logger.warn('Creation of http connection failed')
            self.logger.warn(str(e))

    def __del__(self):
        if self.is_valid():
            self.connection.close()

    def is_valid(self):
        return self.connection is not None

    def get(self, path):
        if not self.is_valid():
            self.connection.connect()
        self.connection.request(
            "GET", self.api_prefix+path, headers=self.http_headers)
        resp = self.connection.getresponse()
        if resp.status < 200 or resp.status >= 300:
            self.logger.warn("GET failed with status {} and reason: {}".format(resp.status,
                             resp.reason))
        return resp

    def post(self, path, body):
        self.connection.request(
            "POST", self.api_prefix+path, body=body, headers=self.http_headers)
        resp = self.connection.getresponse()
        if resp.status < 200 or resp.status >= 300:
            self.logger.warn("POST failed with status {} and reason: {}".format(
                resp.status, resp.reason))
        return json.loads(resp.read())

    def put(self, path, body):
        self.connection.request(
            "PUT", self.api_prefix+path, body=body, headers=self.http_headers)
        resp = self.connection.getresponse()
        # self.logger.info(resp.read())
        if resp.status < 200 or resp.status >= 300:
            self.logger.warn("POST failed with status {} and reason: {}".format(
                resp.status, resp.reason))
        return json.loads(resp.read())

    def delete(self, path) -> int:
        self.connection.request(
            "DELETE", self.api_prefix + path, body=None, headers=self.http_headers
        )

        resp = self.connection.getresponse()
        if resp.status < 200 or resp.status >= 300:
            self.logger.warn("DELETE failed with status {} and reason: {}".format(
                resp.status, resp.reason))
        return resp.status

    def put_no_response(self, path, body):
        self.connection.request(
            "PUT", self.api_prefix+path, body=body, headers=self.http_headers)


class MirRestAPI():

    def __init__(self, logger, hostname, auth=""):
        self.logger = logger
        if hostname is not None:
            address = hostname + ":80"
        # else:
        #     address="192.168.12.20:80"
        self.http = HttpConnection(logger, address, auth, "/api/v2.0.0")

    def close(self):
        self.http.__del__()
        self.logger.info("REST API: Connection closed")

    def is_connected(self, print=True):
        if not self.http.is_valid():
            self.logger.warn('REST API: Http-Connection is not valid')
            return False
        try:
            self.http.connection.connect()
            self.http.connection.close()
            if print:
                self.logger.info("REST API: Connected!")
        except Exception as e:
            if print:
                self.logger.warn(
                    'REST API: Attempt to connect failed: ' + str(e))
            return False
        return True

    def is_available(self):
        status = json.dumps(self.get_status())
        if "service_unavailable" in status:
            return False
        else:
            return True

    def wait_for_available(self):
        while True:
            if self.is_connected(print=False):
                if self.is_available():
                    self.logger.info('REST API: available')
                    break
                else:
                    self.logger.info('REST API: unavailable... waiting')
                    time.sleep(1)

    def get_status(self):
        response = self.http.get("/status")
        return json.loads(response.read())

    def get_state_id(self):
        status = self.get_status()
        state_id = status["state_id"]
        return state_id
    """ Choices are: {3, 4, 11}, State: {Ready, Pause, Manualcontrol}
    """

    def set_state_id(self, stateId):
        return self.http.put("/status", json.dumps({'state_id': stateId}))

    def is_ready(self):
        status = self.get_status()
        if status["state_id"] != 3:  # 3=Ready, 4=Pause, 11=Manualcontrol
            self.logger.warn("MIR currently occupied. System state: {}".format(
                status["state_text"]))
            return False
        else:
            return True

    def get_all_settings(self, advanced=False, listGroups=False):
        if advanced:
            response = self.http.get("/settings/advanced")
        elif listGroups:
            response = self.http.get("/setting_groups")
        else:
            response = self.http.get("/settings")
        return json.loads(response.read())

    def get_group_settings(self, groupID):
        response = self.http.get("/setting_groups/" + groupID + "/settings")
        return json.loads(response.read())

    def set_setting(self, settingID, settingData):
        return self.http.put("/setting", json.dumps({settingID: settingData}))

    def sync_time(self):
        timeobj = datetime.now()
        dT = timeobj.strftime("%Y-%m-%dT%X")
        response = 'REST API: '
        try:
            response += str(self.http.put("/status",
                            json.dumps({'datetime': dT})))
        except Exception as e:
            if str(e) == "timed out":
                # setting datetime over REST API seems not to be intended
                # that's why there is no response accompanying the PUT request,
                # therefore a time out occurs, however time has been set correctly
                response += "Set datetime to " + dT
                self.logger.warn("REST API: Setting time Mir triggers emergency stop, \
                                  please unlock.")
                self.logger.info(response)

                # this is needed, because a timeset restarts the restAPI
                self.wait_for_available()

                return response
        response += " Error setting datetime"
        return response

    def get_distance_statistics(self):
        response = self.http.get("/statistics/distance")
        return json.loads(response.read())

    def get_positions(self):
        response = self.http.get("/positions")
        return json.loads(response.read())

    def get_pose_guid_by_name(self, pos_name):
        positions = self.get_positions()
        return next((pos["guid"] for pos in positions if pos["name"] == pos_name), None)

    def get_all_map_info(self):
        response = self.http.get("/maps")
        return json.loads(response.read())

    def get_map_guid_by_name(self, map_name):
        map_info = self.get_all_map_info()
        return next((info["guid"] for info in map_info if info["name"] == map_name), None)

    def get_missions(self):
        response = self.http.get("/missions")
        return json.loads(response.read())

    def get_mission_guid(self, mission_name):
        missions = self.get_missions()
        return next((mis["guid"] for mis in missions if mis["name"] == mission_name), None)

    def get_sounds(self):
        response = self.http.get("/sounds")
        return json.loads(response.read())

    def move_to(self, position, mission="move_to"):
        mis_guid = self.get_mission_guid(mission)
        pos_guid = self.get_pose_guid_by_name(position)

        for (var, txt, name) in zip((mis_guid, pos_guid), ("Mission", "Position"),
                                    (mission, position)):
            if var is None:
                self.logger.warn(
                    "No {} named {} available on MIR - Aborting move_to".format(txt, name))
                return

        body = json.dumps({
            "mission_id": mis_guid,
            "message": "Externally scheduled mission from the MIR Python Client",
            "parameters": [{
                "value": pos_guid,
                "input_name": "target"
            }]})

        data = self.http.post("/mission_queue", body)
        self.logger.info(
            "Mission scheduled for execution under id {}".format(data["id"]))

        while data["state"] != "Done":
            resp = self.http.get("/mission_queue/{}".format(data["id"]))
            data = json.loads(resp.read())
            if data["state"] == "Error":
                self.logger.warn("Mission failed as robot is in error")
                return
            self.logger.info(data["state"])
            time.sleep(2)

        self.logger.info("Mission executed successfully")

    def add_position(self, name, x, y, orientation, map_id, type_id=0):
        # type_id = 0 -> "normal" position
        # type_id = 1 -> position of type "cart"
        body = json.dumps({
            "name": name,
            "pos_x": x,
            "pos_y": y,
            "orientation": orientation,
            "map_id": map_id,
            "type_id": type_id
        })
        return self.http.post("/positions", body)

    def delete_position(self, position_guid):
        return self.http.delete(f"/positions/{position_guid}")

    def add_mission_to_queue(self, mission_name):
        mis_guid = self.get_mission_guid(mission_name)
        if mis_guid is None:
            self.logger.warn(
                "No Mission named '{}' available on MIR - Aborting move_to".format(mission_name))
            return False, -1

        # put in mission queue
        body = json.dumps({"mission_id": str(mis_guid),
                           "message": "Mission scheduled by ROS node mir_restapi_server",
                          "priority": 0})

        data = self.http.post("/mission_queue", body)
        try:
            self.logger.info(
                "Mission scheduled for execution under id {}".format(data["id"]))
            return True, int(data["id"])
        except KeyError:
            self.logger.warn("Couldn't schedule mission")
            self.logger.warn(str(data))
        return False, -1

    def is_mission_done(self, mission_queue_id):
        try:
            # mis_guid = self.get_mission_guid(mission_name)
            response = self.http.get("/mission_queue")

        except http.client.ResponseNotReady or http.client.CannotSendRequest:
            self.logger.info(
                "Http error: Mission with queue_id {} is still in queue".format(mission_queue_id))
            self.http.__del__()
            return False

        # self.logger.info("Mission with queue_id {} is in queue".format(mission_queue_id))
        # self.logger.info("Response status {}".format(response.status))
        data = json.loads(response.read())

        for d in data:
            if d["id"] == mission_queue_id:
                if d["state"] == 'Done':
                    self.logger.info(
                        "Mission {} is done".format(mission_queue_id))
                    return True

        self.logger.info(
            "Mission with queue_id {} is still in queue".format(mission_queue_id))
        return False

    def get_system_info(self):
        response = self.http.get("/system/info")
        return json.loads(response.read())


if __name__ == "__main__":
    import os
    from logging import Logger
    auth_token = os.environ["MIR_AUTH_TOKEN"]
    # print(auth_token)
    api_handle = MirRestAPI(hostname="192.168.12.20",
                            logger=Logger("test"), auth=auth_token)
    all_maps = api_handle.get_all_map_info()

    map_guid = api_handle.get_map_guid_by_name("Versuchsfeld")
    api_handle.add_position(name="test_pose_1", x=2,
                            y=2, orientation=0, map_id=map_guid)
    test_guid = api_handle.get_pose_guid_by_name("test_pose_1")
    del_resp = api_handle.delete_position(
        test_guid)
