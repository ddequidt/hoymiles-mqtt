from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import Sensor, SensorInfo
from ha_mqtt_discoverable.sensors import Switch, SwitchInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo


class Meter_3phases:

    #   device_type: 3
    #   serial_number: 61568409042945
    #   phase_total_power: -210
    #   phase_A_power: -76
    #   phase_B_power: -63
    #   phase_C_power: -69
    #   energy_total_power: 236349
    #   energy_phase_A: 69102
    #   energy_phase_B: 109353
    #   energy_phase_C: 57893
    #   energy_total_consumed: 287389
    #   energy_phase_A_consumed: 92790
    #   energy_phase_B_consumed: 104465
    #   energy_phase_C_consumed: 90133
    #   fault_code: 1
    #   voltage_phase_A: 23330
    #   voltage_phase_B: 22630
    #   voltage_phase_C: 23180
    #   current_phase_A: 479
    #   current_phase_B: 390
    #   current_phase_C: 454
    #   power_factor_total: -685
    #   power_factor_phase_A: -682
    #   power_factor_phase_B: -720
    #   power_factor_phase_C: -660

    def __init__(self, mqtt_settings, meterInfo, via_device: str):
        """Initialize MeterData class."""

        self.device_info = DeviceInfo(
            name="Hoymiles Meter",
            identifiers=str(meterInfo.meter_sn),
            model=str(meterInfo.meter_model),
            via_device=via_device,
        )

        self.power_info = dict()
        self.energy_info = dict()
        self.energy_consumed_info = dict()
        self.voltage_info = dict()
        self.current_info = dict()
        self.power_factor_info = dict()
        
        for phase in ['total', 'A', 'B', 'C']:
            """ phase_X_power """
            phase_power_info = SensorInfo(
                device=self.device_info,
                unique_id=f"{
                    self.device_info.identifiers}_phase_power_{phase}",
                name=f"Phase {phase} power",
                device_class="power",
                unit_of_measurement="kW",
            )

            self.power_info[phase] = Sensor(Settings(
                mqtt=mqtt_settings,
                entity=phase_power_info,
            ))

            """ energy_X """
            energy_info = SensorInfo(
                device=self.device_info,
                unique_id=f"{
                    self.device_info.identifiers}_energy_{phase}",
                name=f"Energy {'total' if phase ==
                               'total' else "phase " + phase}",
                device_class="energy",
                unit_of_measurement="kWh",
            )

            self.energy_info[phase] = Sensor(Settings(
                mqtt=mqtt_settings,
                entity=energy_info,
            ))

            """ energy_X_consumed """
            energy_consumed_info = SensorInfo(
                device=self.device_info,
                unique_id=f"{
                    self.device_info.identifiers}_energy_{phase}_consumed",
                name=f"Energy consumed {'total' if phase ==
                                        'total' else "phase " + phase}",
                device_class="energy",
                unit_of_measurement="kWh",
            )

            self.energy_consumed_info[phase] = Sensor(Settings(
                mqtt=mqtt_settings,
                entity=energy_consumed_info,
            ))

            """ power_factor_x """
            power_factor_info = SensorInfo(
                device=self.device_info,
                unique_id=f"{
                    self.device_info.identifiers}_power_factor_{phase}",
                name=f"Power factor {phase}",
                device_class="power_factor",
                unit_of_measurement="%",
            )

            self.power_factor_info[phase] = Sensor(Settings(
                mqtt=mqtt_settings,
                entity=power_factor_info,
            ))
        
        for phase in ['A', 'B', 'C']:
            """ voltage_X """
            voltage_info = SensorInfo(
                device=self.device_info,
                unique_id=f"{
                    self.device_info.identifiers}_voltage_{phase}",
                name=f"Voltage {'total' if phase ==
                               'total' else "phase " + phase}",
                device_class="voltage",
                unit_of_measurement="V",
            )

            self.voltage_info[phase] = Sensor(Settings(
                mqtt=mqtt_settings,
                entity=voltage_info,
            ))

            """ current_X """
            current_info = SensorInfo(
                device=self.device_info,
                unique_id=f"{
                    self.device_info.identifiers}_current_{phase}",
                name=f"Current {'total' if phase ==
                               'total' else "phase " + phase}",
                device_class="current",
                unit_of_measurement="A",
            )

            self.current_info[phase] = Sensor(Settings(
                mqtt=mqtt_settings,
                entity=current_info,
            ))

    def handle_real_data_new(self, meter_data):
        """Extract and send data from real_data_new"""
        for phase in ['total', 'A', 'B', 'C']:
            self.power_info[phase].set_state(
                getattr(meter_data, f'phase_{phase}_power')/100.0)

            self.energy_info[phase].set_state(
                getattr(meter_data, f'energy_{'total_power' if phase ==
                                              'total' else "phase_" + phase}')/100.0)

            self.energy_consumed_info[phase].set_state(
                getattr(meter_data, f'energy_{'total' if phase ==
                                              'total' else "phase_" + phase}_consumed')/100.0)
            
            self.power_factor_info[phase].set_state(
                getattr(meter_data, f'power_factor_{'total' if phase ==
                                              'total' else "phase_" + phase}')/10.0)
            
        for phase in ['A', 'B', 'C']:
            self.voltage_info[phase].set_state(
                getattr(meter_data, f'voltage_phase_{phase}')/100.0)
            
            self.current_info[phase].set_state(
                getattr(meter_data, f'current_phase_{phase}')/100.0)
