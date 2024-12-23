"""Setup for the hoymiles-mqtt package."""

from setuptools import setup

setup(
    name="hoymiles-mqtt",
    packages=["hoymiles_mqtt"],
    install_requires=["hoymiles_wifi @ git+https://git@github.com/ddequidt/hoymiles-wifi.git#egg=hoymiles_wifi", "ha-mqtt-discoverable"],
    version="0.1.0",
    description="Intefracing Hoymiles DTUs and the HMS-XXXXW-2T HMS microinverters to MQTT especially designed for home assistant MQTT integration.",
    author="ddequidt",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "hoymiles-mqtt = hoymiles_mqtt.__main__:run_main",
        ],
    },
)
