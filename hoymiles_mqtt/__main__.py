"""Contains the main functionality of the hoymiles_wifi package."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict, dataclass

from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import Sensor, SensorInfo
from ha_mqtt_discoverable.sensors import Switch, SwitchInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo
from paho.mqtt.client import Client
from hoymiles_mqtt.meter import Meter_3phases
from hoymiles_mqtt.pv import Pv
from hoymiles_wifi.dtu import DTU  # type: ignore
from hoymiles_mqtt import logger


async def main() -> None:
    """Execute the main function for the mqtt package."""

    parser = argparse.ArgumentParser(description="Hoymiles DTU Monitoring")
    parser.add_argument(
        "--dtu-host",
        type=str,
        required=True,
        help="IP address or hostname of the DTU"
    )
    parser.add_argument(
        "--local_addr",
        type=str,
        required=False,
        help="IP address of the interface to bind to",
    )
    parser.add_argument(
        "--mqtt-host",
        type=str,
        default="localhost",
        help="MQTT Host",
    )
    parser.add_argument(
        "--mqtt-port",
        type=int,
        default=1883,
        help="MQTT Port",
    )
    parser.add_argument(
        "--mqtt-username",
        required=False,
        help="MQTT Login",
    )
    parser.add_argument(
        "--mqtt-password",
        required=False,
        help="MQTT Password",
    )
    parser.add_argument(
        "--mqtt-client-name",
        default="hoymiles-mqtt",
        help="MQTT Client name",
    )
    parser.add_argument(
        "--discovery-prefix",
        default="homeassistant",
        help="Homeassistant discovery prefix",
    )
    parser.add_argument(
        "--state-prefix",
        required=False,
        help="Homeassistant state prefix",
    )
    args = parser.parse_args()

    if args.state_prefix is None:
        args.state_prefix = args.mqtt_client_name

    print(args)

    # client = Client(args.mqtt_client_name)
    # client.username_pw_set(args.mqtt_username, args.mqtt_password)
    # client.connect(args.mqtt_host, args.mqtt_port)
    # client.loop_start()

    mqtt_settings = Settings.MQTT(
        # client=client,
        host=args.mqtt_host,
        port=args.mqtt_port,
        username=args.mqtt_username,
        password=args.mqtt_password,
        discovery_prefix=args.discovery_prefix,
        state_prefix=args.state_prefix,
    )

    dtu = DTU(args.dtu_host)

    info_data = await dtu.async_get_information_data()

    if not info_data:
        raise Exception("Unable to get response!")

    print(f"information_data: {info_data}")

    real_data_new = await dtu.async_get_real_data_new()

    if not real_data_new:
        raise Exception("Unable to get response!")

    print(f"real_data_new: {real_data_new}")

    dtu_device_info = DeviceInfo(
        name="Hoymiles DTU",
        identifiers=str(info_data.dtu_sn),
        hw_version=str(info_data.mDtuInfo.dtu_hw),
        sw_version=str(info_data.mDtuInfo.dtu_sw),
        manufacturer="",
        model="",
    )

    dtu_state_info = BinarySensorInfo(
        device=dtu_device_info,
        unique_id=dtu_device_info.identifiers + "_state",
        name="DTU state",
    )

    dtu_state_switch = BinarySensor(Settings(
        mqtt=mqtt_settings,
        entity=dtu_state_info,
    ))

    dtu_state_switch.on()

    meters = []

    for i, meter_info in enumerate(info_data.mMeterInfo):
        meter_data = real_data_new.meter_data[i]

        if meter_data.device_type == 3:
            meterData = Meter_3phases(
                mqtt_settings,
                meter_info,
                via_device=dtu_device_info.identifiers,
            )
            meterData.handle_real_data_new(meter_data)

            meters.append(meterData)

        else:
            logger.warning(f'Unsupported meter info device_type {
                meter_data.device_type}')

    inverters = []
    for pvInfo in info_data.mpvInfo:
        inverter_device_info = DeviceInfo(
            name=f"Inverter {pvInfo.pv_sn}",
            identifiers=str(pvInfo.pv_sn),
            via_device=dtu_device_info.identifiers,
            hw_version=str(pvInfo.pv_hw),
            sw_version=str(pvInfo.pv_sw),
            manufacturer="",
            model="",
        )
        print(inverter_device_info)

        inverters.append(inverter_device_info)

        inverter_state_info = BinarySensorInfo(
            device=inverter_device_info,
            unique_id=f"{inverter_device_info.identifiers}_state",
            name=f"State",
        )

        inverter_state_switch = BinarySensor(Settings(
            mqtt=mqtt_settings,
            entity=inverter_state_info,
        ))

        inverter_state_switch.on()

    pvs = []
    for pv_data in real_data_new.pv_data:
        pvData = Pv(
            mqtt_settings,
            pv_data,
            via_device=str(pv_data.serial_number),
        )
        pvData.handle_real_data_new(pv_data)

        pvs.append(pvData)

    while (True):
        await asyncio.sleep(35)

        real_data_new = await dtu.async_get_real_data_new()

        if not real_data_new:
            raise Exception("Unable to get response!")

        for i, meter_data in enumerate(real_data_new.meter_data):
            meters[i].handle_real_data_new(meter_data)

        for i, pv_data in enumerate(real_data_new.pv_data):
            pvs[i].handle_real_data_new(pv_data)


def run_main() -> None:
    """Run the main function for the hoymiles_wifi package."""
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
