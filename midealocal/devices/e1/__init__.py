"""Midea local E1 device."""

import logging
from enum import StrEnum
from typing import Any

from midealocal.const import DeviceType, ProtocolVersion
from midealocal.device import MideaDevice
from midealocal.exceptions import ValueWrongType

from .message import (
    MessageE1Response,
    MessageLock,
    MessagePower,
    MessageQuery,
    MessageStorage,
)

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    """Midea E1 device attributes."""

    power = "power"
    status = "status"
    mode = "mode"
    additional = "additional"
    door = "door"
    rinse_aid = "rinse_aid"
    salt = "salt"
    child_lock = "child_lock"
    uv = "uv"
    dry = "dry"
    dry_status = "dry_status"
    storage = "storage"
    storage_status = "storage_status"
    time_remaining = "time_remaining"
    progress = "progress"
    storage_remaining = "storage_remaining"
    temperature = "temperature"
    humidity = "humidity"
    waterswitch = "waterswitch"
    water_lack = "water_lack"
    error_code = "error_code"
    softwater = "softwater"
    wrong_operation = "wrong_operation"
    bright = "bright"
    door_auto_open = "door_auto_open"
    wash_region = "wash_region"
    version = "version"
    air = "air"
    air_status = "air_status"
    air_set_hour = "air_set_hour"
    air_left_hour = "air_left_hour"
    ion_level = "ion_level"
    ion_status = "ion_status"
    ion_time_remaining = "ion_time_remaining"

class MideaE1Device(MideaDevice):
    """Midea E1 device."""

    def __init__(
        self,
        name: str,
        device_id: int,
        ip_address: str,
        port: int,
        token: str,
        key: str,
        device_protocol: ProtocolVersion,
        model: str,
        subtype: int,
        customize: str,  # noqa: ARG002
    ) -> None:
        """Initialize Midea E1 device."""
        super().__init__(
            name=name,
            device_id=device_id,
            device_type=DeviceType.E1,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            device_protocol=device_protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.status: None,
                DeviceAttributes.mode: 0,
                DeviceAttributes.additional: 0,
                DeviceAttributes.uv: False,
                DeviceAttributes.dry: None,
                DeviceAttributes.dry_status: False,
                DeviceAttributes.door: False,
                DeviceAttributes.rinse_aid: False,
                DeviceAttributes.salt: False,
                DeviceAttributes.child_lock: False,
                DeviceAttributes.storage: False,
                DeviceAttributes.storage_status: False,
                DeviceAttributes.time_remaining: None,
                DeviceAttributes.progress: None,
                DeviceAttributes.storage_remaining: None,
                DeviceAttributes.temperature: None,
                DeviceAttributes.humidity: None,
                DeviceAttributes.waterswitch: False,
                DeviceAttributes.water_lack: False,
                DeviceAttributes.error_code: None,
                DeviceAttributes.softwater: 0,
                DeviceAttributes.wrong_operation: None,
                DeviceAttributes.bright: 0,
                DeviceAttributes.door_auto_open: False,
                DeviceAttributes.wash_region: 0,
                DeviceAttributes.version: None,
                DeviceAttributes.air: False,
                DeviceAttributes.air_status: False,
                DeviceAttributes.air_set_hour: None,
                DeviceAttributes.air_left_hour: None,
                DeviceAttributes.ion_level: None,
                DeviceAttributes.ion_status: None,
                DeviceAttributes.ion_time_remaining: None,

            },
        )
        self._modes = {
            0x00: "Neutral Gear",  # BYTE_MODE_NEUTRAL_GEAR
            0x01: "Auto Wash",  # BYTE_MODE_AUTO_WASH
            0x02: "Strong Wash",  # BYTE_MODE_STRONG_WASH
            0x03: "Standard Wash",  # BYTE_MODE_STANDARD_WASH
            0x04: "ECO Wash",  # BYTE_MODE_ECO_WASH
            0x05: "Glass Wash",  # BYTE_MODE_GLASS_WASH
            0x06: "90 Min Wash",  # BYTE_MODE_90MIN_WASH
            0x07: "Fast Wash",  # BYTE_MODE_FAST_WASH
            0x08: "Soak Wash",  # BYTE_MODE_SOAK_WASH
            0x09: "1 Hour Wash",  # BYTE_MODE_HOUR_WASH
            0x0A: "Self Clean",  # BYTE_MODE_SELF_CLEAN
            0x0B: "Fruit Wash",  # BYTE_MODE_FRUIT_WASH
            0x0C: "Self Define",  # BYTE_MODE_SELF_DEFINE
            0x0D: "Germ",  # BYTE_MODE_GERM ???
            0x0E: "Bowl Wash",  # BYTE_MODE_BOWL_WASH
            0x0F: "Kill Germ",  # BYTE_MODE_KILL_GERM
            0x10: "Sea Food Wash",  # BYTE_MODE_SEA_FOOD_WASH
            0x12: "Hot Pot Wash",  # BYTE_MODE_HOT_POT_WASH
            0x13: "Quiet Night Wash",  # BYTE_MODE_QUIET_NIGHT_WASH
            0x14: "Less Wash",  # BYTE_MODE_LESS_WASH
            0x16: "Oil Net Wash",  # BYTE_MODE_OIL_NET_WASH
            0x19: "Cloud Wash",  # BYTE_MODE_CLOUD_WASH
        }
        self._status = {
            0x00: "Power Off",
            0x01: "Cancel",
            0x02: "Delay",
            0x03: "Running",
            0x04: "Error",
            0x05: "Soft Gear",
        }
        self._progress = ["Idle", "Pre-wash", "Wash", "Rinse", "Dry", "Complete"]
        self._additional = {
            0x00: "None",
            0x01: "Extra Drying",
            0x03: "Express",
            0x04: "Power Wash",
        }
        self._wash_region = {
            0x00: "Both Zones",
            0x01: "Top Zone",
            0x02: "Bottom Zone",
        }

    def build_query(self) -> list[MessageQuery]:
        """Midea E1 device build query."""
        return [MessageQuery(self._message_protocol_version)]

    def process_message(self, msg: bytes) -> dict[str, Any]:
        """Midea E1 device process message."""
        message = MessageE1Response(msg)
        _LOGGER.debug("[%s] Received: %s", self.device_id, message)
        new_status = {}
        for status in self._attributes:
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.status:
                    self._attributes[status] = self._status.get(value)
                elif status == DeviceAttributes.progress:
                    if value < len(self._progress):
                        self._attributes[status] = self._progress[value]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.mode:
                    self._attributes[status] = self._modes.get(value)
                else:
                    self._attributes[status] = getattr(message, str(status))
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr: str, value: bool | int | str) -> None:
        """Midea E1 device set attribute."""
        if not isinstance(value, bool):
            raise ValueWrongType("[e1] Expected bool")
        message: MessagePower | MessageLock | MessageStorage | None = None
        if attr == DeviceAttributes.power:
            message = MessagePower(self._message_protocol_version)
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.child_lock:
            message = MessageLock(self._message_protocol_version)
            message.lock = value
            self.build_send(message)
        elif attr == DeviceAttributes.storage:
            message = MessageStorage(self._message_protocol_version)
            message.storage = value
            self.build_send(message)


class MideaAppliance(MideaE1Device):
    """Midea E1 appliance."""
