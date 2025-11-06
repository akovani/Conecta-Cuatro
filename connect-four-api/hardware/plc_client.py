import snap7
import math
import json
from snap7.util import get_real, get_bool, set_bool, set_real
from core.constants import PLC_IP, PLC_RACK, PLC_SLOT, PLC_DB_NUMBER
from core.logger import logger


class PLCClient:
    def __init__(self):
        self.plc = snap7.client.Client()
        self.plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        self.db_number = PLC_DB_NUMBER
        # This property is None because the value will get initialised when the JSON file called machine_config.json gets read successfully
        self.machine_config = None
        try:
            with open("machine_config.json", "r") as file:
                self.machine_config = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading machine_config.json: {e}")

    def connect(self):
        self.plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        if self.plc.get_connected():
            logger.info("Connection successful.")
        else:
            logger.error("Connection failed.")

    def disconnect(self):
        self.plc.disconnect()
        logger.warning("Connection closed.")

    def prepare_data(self, x, y, stift_auf_ab, position_erreicht):
        data = bytearray(self.size)  # Size of the data in bytes

        # Set Real values (XAchse and YAchse)
        set_real(data, 0, x)  # Real value at offset 0.0 (XAchse)
        set_real(data, 4, y)  # Real value at offset 4.0 (YAchse)

        # Set Bool values (StiftAufAB and PositionErreicht)
        set_bool(data, 8, 0, stift_auf_ab)  # Bool at offset 8.0 (StiftAufAB)
        set_bool(data, 8, 1, position_erreicht)  # Bool at offset 8.1 (PositionErreicht)

        return data

    def send_coordinates_to_plc(self, x, y, stift_auf_ab=False, position_erreicht=True):
        data = self.prepare_data(x, y, stift_auf_ab, position_erreicht)
        self.write_db1_data(data)
        logger.info("Data successfully written.")

    def read_db1_data(self):
        data = self.plc.db_read(self.db_number, self.start, self.size)
        return data

    def parse_data(self, data):
        x_achse = get_real(data, 0)  # Real value at offset 0.0
        y_achse = get_real(data, 4)  # Real value at offset 4.0
        stift_auf_ab = get_bool(data, 8, 0)  # Bool at offset 8.0
        position_erreicht = get_bool(data, 8, 1)  # Bool at offset 8.1
        return x_achse, y_achse, stift_auf_ab, position_erreicht

    def write_db1_data(self, data):
        self.plc.db_write(self.db_number, self.start, data)

    def column_to_machine_coords(self, field_definition, is_cross):
        """
        Convert Connect Four field coordinates to machine coordinates.

        Parameters:
            field_definition (str): The field definition per the contour_recognition ("A2").
            is_cross (bool): True if the symbol is a cross.
        """

        start_x = self.machine_config.get("x", 0)
        start_y = self.machine_config.get("y", 0)
        distance = self.machine_config.get("inner_distance_in_px", 10)

        # Column letters and row number mapped to indices
        column_letter, row_number = field_definition[0], int(field_definition[1])
        col_index = ord(column_letter.upper()) - ord("A")
        row_index = row_number - 1

        # Use the starting coords and add them to the multiplied value of the distance and the halfed distance (center of field)
        center_x = start_x + col_index * distance + distance / 2
        center_y = start_y + (5 - row_index) * distance + distance / 2

        if is_cross:
            # half size defines how long the cross's diagonal lines should be (for a smaller cross, just increase the 1.5)
            half_size = distance / 1.5

            top_left = (center_x - half_size, center_y - half_size)
            bottom_right = (center_x + half_size, center_y + half_size)
            top_right = (center_x + half_size, center_y - half_size)
            bottom_left = (center_x - half_size, center_y + half_size)

            self.send_coordinates_to_plc(*top_left, True)
            self.send_coordinates_to_plc(*bottom_right, True)
            self.send_coordinates_to_plc(center_x, center_y, False)
            self.send_coordinates_to_plc(*top_right, True)
            self.send_coordinates_to_plc(*bottom_left, True)

        else:
            radius = distance / 3
            # 8 points should be enough to draw a circle-like shape
            num_points = 8

            circle_points = [
                (
                    center_x + radius * math.cos(theta),
                    center_y + radius * math.sin(theta),
                )
                for theta in [i * (2 * math.pi / num_points) for i in range(num_points)]
            ]

            for x, y in circle_points:
                self.send_coordinates_to_plc(x, y, True)
