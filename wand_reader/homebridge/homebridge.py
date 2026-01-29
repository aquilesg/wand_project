import logging
import os
import requests
from urllib.parse import urljoin
from typing import Any, TypedDict, cast

logger = logging.getLogger(__name__)

# Constants
ENV_USER_NAME = "HOMEBRIDGE_USERNAME"
ENV_PASSWORD = "HOMEBRIDGE_PASSWORD"
RASPBERRY_PI_URL = "http://raspberrypi1.local:8581"


class HomebridgeAPIError(os.error):
    """
    Errors created when Homebridge encounters an API error
    """


class AccessoryInfo(TypedDict, total=False):
    Manufacturer: str
    Model: str
    SerialNumber: str


class AccessoryData(TypedDict, total=False):
    uniqueId: str
    aid: int
    iid: int
    serviceName: str
    accessoryInformation: AccessoryInfo
    values: dict[str, object]


class HomebridgeAccessory:
    def __init__(self, raw_data: dict[str, object]) -> None:
        """
        Expects a dictionary (parsed JSON) representing one Homebridge accessory.
        """

        data = cast(AccessoryData, raw_data)

        self.unique_id: str | None = data.get("uniqueId")
        self.aid: int | None = data.get("aid")
        self.iid: int | None = data.get("iid")

        self.name: str = data.get("serviceName", "Unknown Device")
        self.info: AccessoryInfo = data.get("accessoryInformation", {})
        self.manufacturer: str = self.info.get("Manufacturer", "Unknown")
        self.model: str | None = self.info.get("Model")
        self.current_values: dict[str, object] = data.get("values", {})

        on_val = self.current_values.get("On")
        self.is_on: bool = bool(on_val) if on_val is not None else False

    def get_toggle_payload(self) -> dict[str, str | bool]:
        """Generates the JSON payload to flip the current power state."""
        new_state: bool = not self.is_on
        return {"characteristicType": "On", "value": new_state}


class HomebridgeAPI:
    def __init__(self, base_url: str = RASPBERRY_PI_URL) -> None:
        self.base_url: str = base_url.rstrip("/") + "/"
        self.session: requests.Session = requests.Session()
        self.available: bool = False

        # 1. Authenticate and update the session headers
        self.__authenticate()

        # Populate accessories
        self.__accessories = self.refresh_accessories()

    def __authenticate(self) -> None:
        """
        Logs in and updates the session with the Authorization header.
        """
        auth_endpoint = "api/auth/login"

        user_name = os.environ.get(ENV_USER_NAME)
        password = os.environ.get(ENV_PASSWORD)

        if not user_name or not password:
            missing = []
            if not user_name:
                missing.append(ENV_USER_NAME)
            if not password:
                missing.append(ENV_PASSWORD)

            error_msg = f"Missing environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise HomebridgeAPIError(error_msg)

        logger.info("creating session token for authentication")
        request_headers = {"accept": "*/*", "Content-Type": "application/json"}
        payload = {"username": user_name, "password": password, "otp": "string"}
        login_url = urljoin(self.base_url, auth_endpoint)

        response = self.session.post(login_url, json=payload, headers=request_headers)
        response.raise_for_status()  # Raises error for 4xx or 5xx responses
        token = response.json().get("access_token")

        logger.info("successfully created authentication token")
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "accept": "*/*",
            }
        )
        self.available = True

    def request(self, method, endpoint, **kwargs) -> requests.Response:
        """A wrapper for all requests to handle token expiration."""
        url = urljoin(self.base_url, endpoint)
        logger.info(f"making request: {url}")
        if method.upper() in ["POST", "PUT", "PATCH"]:
            if "json" not in kwargs and "data" not in kwargs:
                kwargs["json"] = {}
        response = self.session.request(method, url, **kwargs)
        # If token expired, re-auth once and retry
        if response.status_code != 200:
            logger.warning(
                f"Request to {url} failed with status code: {response.status_code}"
            )
            logger.warning(
                f"message: {response.text}",
            )
        return response

    def refresh_accessories(self) -> dict:
        """
        Fetches List of accessories connected to this Homebridge
        """
        return self.request("GET", "api/accessories").json()

    def get_plugin_List(self) -> Any:
        return self.request(
            "PUT",
            "api/server/reset-cached-accessories",
            headers={"accept": "*/*"},
        )

    def get_outlets(self) -> list[HomebridgeAccessory]:
        """
        Returns list of outlets
        """
        items = []
        for item in self.__accessories:
            if item["humanType"].lower() == "outlet":
                OutLetDevice = HomebridgeAccessory(item)
                logger.info(f"discovered outlet: {OutLetDevice.name}")
                items.append(OutLetDevice)
        return items

    def toggle_outlet(self, unique_id: str, outlet_payload: dict) -> bool:
        """
        Toggles the specified outlet, returns true if successful
        """
        request_url = f"/api/accessories/{unique_id}"
        response = self.request("PUT", request_url, json=outlet_payload)
        if response.status_code != 200:
            logger.warning("received non 200 response")
            logger.warning(f"status: {response.status_code}\ntext: {response.text}")
            return False
        return True

    def is_available(self) -> bool:
        """
        Check if the API is online
        """
        return self.available
