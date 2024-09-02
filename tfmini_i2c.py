"""

@Author: Wolfgang Schmied

# The MIT License (MIT)
#
# Copyright (c) 2020 Wolfgang Schmied
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""

import time

from smbus2 import SMBus, i2c_msg

__version__ = "0.0.1"


class TFminiI2C:
    """
    Interface to the Benewake TFmini distance (Lidar-like) sensor with I2C interface.
    Usage examples:

    Define sensor by giving I2C bus number and sensor address (default: 0x10)

    Sensor = TFminiI2C(1, 0x10)

    Sensor.read()
    """

    def __init__(self, i2cbus, address):
        self.reset_msg = None
        self.new_address = None
        self.range_units = None
        self.set_reg2 = None
        self.add_reg2 = None
        self._set_reg_msg = None
        self.add_reg_msg = None
        self.range_value = None
        self.Mode = None
        self.Strength = None
        self.Dist = None
        self.TrigFlag = None
        self.data = None
        self.read = None
        self.write = None

        self.i2cbus = i2cbus
        self.address = address

        # 0x0026, send adddress between 0x10-0x78
        self.reg_set_slave_msg = [0, 38, 1]

        # 0x0027, set trigger mode, default 0x00
        self.reg_trigger_mode = [0, 39, 1]

        # 0x0070, send 0x02 for reset. restore default values, leaves slave address and trigger mode intact
        self.reg_default_set = [0, 112, 1]

        # 0x0051, default 0x00, send 0x01 for fixed detection range limits
        self.reg_det_pattern = [0, 81, 1]

        # 0x0050, send 0x00 for short (0.3-2m),
        # 0x03 for middle (0.5-5m) or 0x07 for long (1-12m). Set to fixed detection range first.
        self.reg_det_range = [0, 80, 1]

        # 0x0066, send 0x00 for mm or 0x01 for cm (default)
        self.reg_dist_unit = [0, 102, 1]

    def _set_register(self, register, setvalue):
        """ helper function """

        self.register = register
        self.setvalue = setvalue
        self.add_reg_msg = i2c_msg.write(self.address, self.register)
        self.set_reg_read = i2c_msg.write(self.address, [setvalue])

        with SMBus(self.i2cbus) as bus:
            bus.i2c_rdwr(self.add_reg_msg, self.set_reg_read)
            time.sleep(0.01)

        return

    def read_all(self):
        """ Return the distance value in selected unit. Default: cm """

        self.write = i2c_msg.write(self.address, [1, 2, 7])
        self.read = i2c_msg.read(self.address, 7)

        with SMBus(self.i2cbus) as bus:
            bus.i2c_rdwr(self.write, self.read)
            # noinspection PyTypeChecker
            self.data = list(self.read)

            self.TrigFlag = self.data[0]
            self.Dist = self.data[3] << 8 | self.data[2]
            self.Strength = self.data[5] << 8 | self.data[4]
            self.Mode = self.data[6]

        return [self.TrigFlag, self.Dist, self.Strength, self.Mode]

    def read_distance(self):
        """ Return the distance value in selected unit. Default: cm """

        self.write = i2c_msg.write(self.address, [1, 2, 7])
        self.read = i2c_msg.read(self.address, 7)

        with SMBus(self.i2cbus) as bus:
            bus.i2c_rdwr(self.write, self.read)
            # noinspection PyTypeChecker
            self.data = list(self.read)

            self.Dist = self.data[3] << 8 | self.data[2]

        return self.Dist

    def reset(self):
        """reset sensor"""

        self.reset_msg = i2c_msg.write(self.address, [0x06])

        with SMBus(self.i2cbus) as bus:
            bus.i2c_rdwr(self.reset_msg)
            time.sleep(0.05)

        return

    def reset_default(self):

        """ reset sensor to factory settings, leave I2C address as is. """
        self._set_register(self.reg_default_set, 0x02)

    def set_address(self, address):
        """set new address, needs power cycle to become active - reset apparently not sufficient"""

        self.new_address = address

        self._set_register(self.reg_set_slave_msg, self.new_address)
        print(
            "After power cycle, TFmini "
            + hex(self.address)
            + " will be "
            + hex(self.new_address)
        )

        return

    def set_range(self, range_value):
        """
        Use to set a short, medium or long distance range mode.
        Default behaviour is automatic switching, with a loss in accuracy while changing.
        For some applications, fixed range mode might be more useful.
        Here, first automatic changes are disabled, then a specific range is locked in.
        Use 0x00, 0x03 or 0x07 for short, medium or long range.
        """

        self.range_value = range_value

        while range_value not in {0x00, 0x03, 0x07}:
            print("Use 0x00, 0x03 or 0x07 for short, medium or long range.")
            return

        self.add_reg_msg = i2c_msg.write(self.address, self.reg_det_pattern)
        self._set_reg_msg = i2c_msg.write(self.address, [0x01])
        """deactivate automatic range switching"""

        print("Set range mode to fixed.")
        with SMBus(self.i2cbus) as bus:
            bus.i2c_rdwr(self.add_reg_msg, self.set_reg_read)

        print("Set range distance.")
        self.add_reg2 = i2c_msg.write(self.address, self.reg_det_range)
        self.set_reg2 = i2c_msg.write(self.address, [self.range_value])
        """ set fixed range """

        with SMBus(self.i2cbus) as bus:
            bus.i2c_rdwr(self.add_reg2, self.set_reg2)
            time.sleep(0.01)

        return

    def setUnit(self, units):

        self.range_units = units

        while self.range_units not in {0x00, 0x01}:
            print("Use 0x00 for mm, or 0x01 for cm.")
            return

        self._set_register(self.reg_dist_unit, self.range_units)
        return


"""
Example usage:

Sensor0 = TFminiI2C(1, 0x10)
Sensor1 = TFminiI2C(1, 0x11)
Sensor2 = TFminiI2C(1, 0x12)

print(Sensor0.readDistance())
print(Sensor1.readAll())
print(Sensor2.readAll())

Sensor0.setUnit(0x00) #for mm
Sensor1.setUnit(0x01) #for cm

Sensor2.setRange(0x05)

"""
