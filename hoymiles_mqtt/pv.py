from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import Sensor, SensorInfo


class Pv:
    # pv_data {
    #   serial_number: 44122199071109
    #   port_number: 1
    #   energy_total: 335074
    #   energy_daily: 1036
    # }

    def __init__(self, mqtt_settings, pv_data, via_device: str):
        """Initialize MeterData class."""

        self.device_info = DeviceInfo(
            name=f"Solar panel {pv_data.serial_number} port {
                pv_data.port_number}",
            identifiers=f"{pv_data.serial_number}_p{pv_data.port_number}",
            model="",
            via_device=via_device,
        )

        energy_total_info = SensorInfo(
            device=self.device_info,
            unique_id=f"{
                self.device_info.identifiers}_energy_total",
            name=f"Energy total",
            device_class="energy",
            unit_of_measurement="kWh",
        )

        self.energy_total = Sensor(Settings(
            mqtt=mqtt_settings,
            entity=energy_total_info,
        ))

        energy_daily_info = SensorInfo(
            device=self.device_info,
            unique_id=f"{
                self.device_info.identifiers}_energy_daily",
            name=f"Energy daily",
            device_class="energy",
            unit_of_measurement="kWh",
        )

        self.energy_daily = Sensor(Settings(
            mqtt=mqtt_settings,
            entity=energy_daily_info,
        ))

    def handle_real_data_new(self, pv_data):
        """Extract and send data from real_data_new"""
        if pv_data.energy_total:
            self.energy_total.set_state(pv_data.energy_total/100.0)
        
        self.energy_daily.set_state(pv_data.energy_daily/100.0)
