#!/usr/bin/env python3
"""

   pytic

   Copyright 2014 2018 Dan Tyrrell

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

   Class for the tic stepper drivers.

    # commands

    # status

    # change the settings
"""


import usb.core
import usb.util
import usb.control
import logging
import decimal
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)d-%(name)s-%(threadName)s-%(levelname)s %(message)s',
                    datefmt='%M:%S')
log = logging.getLogger(__name__)


TIC_PRODUCT_T825 = 1
TIC_PRODUCT_T834 = 2
TIC_PRODUCT_T500 = 3

#A setup packet bRequest value from USB 2.0 Table 9-4
USB_REQUEST_GET_DESCRIPTOR = 6

# A descriptor type from USB 2.0 Table 9-5
USB_DESCRIPTOR_TYPE_STRING = 3

# Generated by h2py e/tic_protocol.h with some spacing added manually
TIC_VENDOR_ID = 0x1FFB
TIC_PRODUCT_ID_T825 = 0x00B3
TIC_PRODUCT_ID_T834 = 0x00B5
TIC_PRODUCT_ID_T500 = 0x00BD

TIC_FIRMWARE_MODIFICATION_STRING_INDEX = 4

TIC_OPERATION_STATE_RESET = 0
TIC_OPERATION_STATE_DEENERGIZED = 2
TIC_OPERATION_STATE_SOFT_ERROR = 4
TIC_OPERATION_STATE_WAITING_FOR_ERR_LINE = 6
TIC_OPERATION_STATE_STARTING_UP = 8
TIC_OPERATION_STATE_NORMAL = 10

TIC_MISC_FLAGS1_ENERGIZED = 0
TIC_MISC_FLAGS1_POSITION_UNCERTAIN = 1

TIC_ERROR_INTENTIONALLY_DEENERGIZED = 0
TIC_ERROR_MOTOR_DRIVER_ERROR = 1
TIC_ERROR_LOW_VIN = 2
TIC_ERROR_KILL_SWITCH = 3
TIC_ERROR_REQUIRED_INPUT_INVALID = 4
TIC_ERROR_SERIAL_ERROR = 5
TIC_ERROR_COMMAND_TIMEOUT = 6
TIC_ERROR_SAFE_START_VIOLATION = 7
TIC_ERROR_ERR_LINE_HIGH = 8
TIC_ERROR_SERIAL_FRAMING = 16
TIC_ERROR_SERIAL_RX_OVERRUN = 17
TIC_ERROR_SERIAL_FORMAT = 18
TIC_ERROR_SERIAL_CRC = 19
TIC_ERROR_ENCODER_SKIP = 20

TIC_INPUT_STATE_NOT_READY = 0
TIC_INPUT_STATE_INVALID = 1
TIC_INPUT_STATE_HALT = 2
TIC_INPUT_STATE_POSITION = 3
TIC_INPUT_STATE_VELOCITY = 4

TIC_RESPONSE_DEENERGIZE = 0
TIC_RESPONSE_HALT_AND_HOLD = 1
TIC_RESPONSE_DECEL_TO_HOLD = 2
TIC_RESPONSE_GO_TO_POSITION = 3

TIC_PIN_NUM_SCL = 0
TIC_PIN_NUM_SDA = 1
TIC_PIN_NUM_TX = 2
TIC_PIN_NUM_RX = 3
TIC_PIN_NUM_RC = 4

TIC_PLANNING_MODE_OFF = 0
TIC_PLANNING_MODE_TARGET_POSITION = 1
TIC_PLANNING_MODE_TARGET_VELOCITY = 2

TIC_RESET_POWER_UP = 0
TIC_RESET_BROWNOUT = 1
TIC_RESET_RESET_LINE = 2
TIC_RESET_WATCHDOG = 4
TIC_RESET_SOFTWARE = 8
TIC_RESET_STACK_OVERFLOW = 16
TIC_RESET_STACK_UNDERFLOW = 32

TIC_PIN_STATE_HIGH_IMPEDANCE = 0
TIC_PIN_STATE_PULLED_UP = 1
TIC_PIN_STATE_OUTPUT_LOW = 2
TIC_PIN_STATE_OUTPUT_HIGH = 3

TIC_MIN_ALLOWED_BAUD_RATE = 200
TIC_MAX_ALLOWED_BAUD_RATE = 115385

TIC_DEFAULT_COMMAND_TIMEOUT = 1000
TIC_MAX_ALLOWED_COMMAND_TIMEOUT = 60000

TIC_MAX_ALLOWED_CURRENT = 3968
TIC_MAX_ALLOWED_CURRENT_T825 = 3968
TIC_MAX_ALLOWED_CURRENT_T834 = 3456
TIC_MAX_ALLOWED_CURRENT_T500 = 3093
TIC_MAX_ALLOWED_CURRENT_CODE_T500 = 32
TIC_CURRENT_LIMIT_UNITS_MA = 32

TIC_MIN_ALLOWED_ACCEL = 100
TIC_MAX_ALLOWED_ACCEL = 0x7FFFFFFF
TIC_MAX_ALLOWED_SPEED = 500000000

TIC_MAX_ALLOWED_ENCODER_PRESCALER = 0x7FFFFFFF
TIC_MAX_ALLOWED_ENCODER_POSTSCALER = 0x7FFFFFFF

TIC_SPEED_UNITS_PER_HZ = 10000
TIC_ACCEL_UNITS_PER_HZ2 = 100

TIC_CONTROL_MODE_SERIAL = 0
TIC_CONTROL_MODE_STEP_DIR = 1
TIC_CONTROL_MODE_RC_POSITION = 2
TIC_CONTROL_MODE_RC_SPEED = 3
TIC_CONTROL_MODE_ANALOG_POSITION = 4
TIC_CONTROL_MODE_ANALOG_SPEED = 5
TIC_CONTROL_MODE_ENCODER_POSITION = 6
TIC_CONTROL_MODE_ENCODER_SPEED = 7

TIC_SCALING_DEGREE_LINEAR = 0
TIC_SCALING_DEGREE_QUADRATIC = 1
TIC_SCALING_DEGREE_CUBIC = 2

TIC_STEP_MODE_FULL = 0
TIC_STEP_MODE_HALF = 1
TIC_STEP_MODE_MICROSTEP1 = 0
TIC_STEP_MODE_MICROSTEP2 = 1
TIC_STEP_MODE_MICROSTEP4 = 2
TIC_STEP_MODE_MICROSTEP8 = 3
TIC_STEP_MODE_MICROSTEP16 = 4
TIC_STEP_MODE_MICROSTEP32 = 5

TIC_DECAY_MODE_MIXED = 0
TIC_DECAY_MODE_SLOW = 1
TIC_DECAY_MODE_FAST = 2
TIC_DECAY_MODE_MODE3 = 3
TIC_DECAY_MODE_MODE4 = 4
TIC_DECAY_MODE_T825_MIXED = 0
TIC_DECAY_MODE_T825_SLOW = 1
TIC_DECAY_MODE_T825_FAST = 2
TIC_DECAY_MODE_T834_MIXED50 = 0
TIC_DECAY_MODE_T834_SLOW = 1
TIC_DECAY_MODE_T834_FAST = 2
TIC_DECAY_MODE_T834_MIXED25 = 3
TIC_DECAY_MODE_T834_MIXED75 = 4
TIC_DECAY_MODE_T500_AUTO = 0

TIC_PIN_PULLUP = 7
TIC_PIN_ANALOG = 6

TIC_PIN_FUNC_POSN = 0
TIC_PIN_FUNC_MASK = 0x0F
TIC_PIN_FUNC_DEFAULT = 0
TIC_PIN_FUNC_USER_IO = 1
TIC_PIN_FUNC_USER_INPUT = 2
TIC_PIN_FUNC_POT_POWER = 3
TIC_PIN_FUNC_SERIAL = 4
TIC_PIN_FUNC_RC = 5
TIC_PIN_FUNC_ENCODER = 6
TIC_PIN_FUNC_KILL_SWITCH = 7

TIC_CMD_SET_TARGET_POSITION = 0xE0
TIC_CMD_SET_TARGET_VELOCITY = 0xE3
TIC_CMD_HALT_AND_SET_POSITION = 0xEC
TIC_CMD_HALT_AND_HOLD = 0x89
TIC_CMD_RESET_COMMAND_TIMEOUT = 0x8C
TIC_CMD_DEENERGIZE = 0x86
TIC_CMD_ENERGIZE = 0x85
TIC_CMD_EXIT_SAFE_START = 0x83
TIC_CMD_ENTER_SAFE_START = 0x8F
TIC_CMD_RESET = 0xB0
TIC_CMD_CLEAR_DRIVER_ERROR = 0x8A
TIC_CMD_SET_MAX_SPEED = 0xE6
TIC_CMD_SET_STARTING_SPEED = 0xE5
TIC_CMD_SET_MAX_ACCEL = 0xEA
TIC_CMD_SET_MAX_DECEL = 0xE9
TIC_CMD_SET_STEP_MODE = 0x94
TIC_CMD_SET_CURRENT_LIMIT = 0x91
TIC_CMD_SET_DECAY_MODE = 0x92
TIC_CMD_GET_VARIABLE = 0xA1
TIC_CMD_GET_VARIABLE_AND_CLEAR_ERRORS_OCCURRED = 0xA2
TIC_CMD_GET_SETTING = 0xA8
TIC_CMD_SET_SETTING = 0x13
TIC_CMD_REINITIALIZE = 0x10
TIC_CMD_START_BOOTLOADER = 0xFF
TIC_CMD_GET_DEBUG_DATA = 0x20

# offsets/indexes
TIC_VAR_OPERATION_STATE = 0x00
TIC_VAR_MISC_FLAGS1 = 0x01
TIC_VAR_ERROR_STATUS = 0x02
TIC_VAR_ERRORS_OCCURRED = 0x04
TIC_VAR_PLANNING_MODE = 0x09
TIC_VAR_TARGET_POSITION = 0x0A
TIC_VAR_TARGET_VELOCITY = 0x0E
TIC_VAR_STARTING_SPEED = 0x12
TIC_VAR_MAX_SPEED = 0x16
TIC_VAR_MAX_DECEL = 0x1A
TIC_VAR_MAX_ACCEL = 0x1E
TIC_VAR_CURRENT_POSITION = 0x22
TIC_VAR_CURRENT_VELOCITY = 0x26
TIC_VAR_ACTING_TARGET_POSITION = 0x2A
TIC_VAR_TIME_SINCE_LAST_STEP = 0x2E
TIC_VAR_DEVICE_RESET = 0x32
TIC_VAR_VIN_VOLTAGE = 0x33
TIC_VAR_UP_TIME = 0x35
TIC_VAR_ENCODER_POSITION = 0x39
TIC_VAR_RC_PULSE_WIDTH = 0x3D
TIC_VAR_ANALOG_READING_SCL = 0x3F
TIC_VAR_ANALOG_READING_SDA = 0x41
TIC_VAR_ANALOG_READING_TX = 0x43
TIC_VAR_ANALOG_READING_RX = 0x45
TIC_VAR_DIGITAL_READINGS = 0x47
TIC_VAR_PIN_STATES = 0x48
TIC_VAR_STEP_MODE = 0x49
TIC_VAR_CURRENT_LIMIT = 0x4A
TIC_VAR_DECAY_MODE = 0x4B
TIC_VAR_INPUT_STATE = 0x4C
TIC_VAR_INPUT_AFTER_AVERAGING = 0x4D
TIC_VAR_INPUT_AFTER_HYSTERESIS = 0x4F
TIC_VAR_INPUT_AFTER_SCALING = 0x51
#not currently implemented -- only implemented on TIC_PRODUCT_T249
TIC_VAR_LAST_MOTOR_DRIVER_ERROR = 0x55
TIC_VAR_AGC_MODE = 0x56
TIC_VAR_AGC_BOTTOM_CURRENT_LIMIT = 0x57
TIC_VAR_AGC_CURRENT_BOOST_STEPS = 0x58
TIC_VAR_AGC_FREQUENCY_LIMIT = 0x59
TIC_VARIABLES_SIZE = 0x5A

# indexes
TIC_SETTING_NOT_INITIALIZED = 0x00
TIC_SETTING_CONTROL_MODE = 0x01
TIC_SETTING_NEVER_SLEEP = 0x02
TIC_SETTING_DISABLE_SAFE_START = 0x03
TIC_SETTING_IGNORE_ERR_LINE_HIGH = 0x04
TIC_SETTING_SERIAL_BAUD_RATE_GENERATOR = 0x05
TIC_SETTING_SERIAL_DEVICE_NUMBER = 0x07
TIC_SETTING_AUTO_CLEAR_DRIVER_ERROR = 0x08
TIC_SETTING_COMMAND_TIMEOUT = 0x09
TIC_SETTING_SERIAL_CRC_ENABLED = 0x0B
TIC_SETTING_LOW_VIN_TIMEOUT = 0x0C
TIC_SETTING_LOW_VIN_SHUTOFF_VOLTAGE = 0x0E
TIC_SETTING_LOW_VIN_STARTUP_VOLTAGE = 0x10
TIC_SETTING_HIGH_VIN_SHUTOFF_VOLTAGE = 0x12
TIC_SETTING_VIN_CALIBRATION = 0x14
TIC_SETTING_RC_MAX_PULSE_PERIOD = 0x16
TIC_SETTING_RC_BAD_SIGNAL_TIMEOUT = 0x18
TIC_SETTING_RC_CONSECUTIVE_GOOD_PULSES = 0x1A
TIC_SETTING_INVERT_MOTOR_DIRECTION = 0x1B
TIC_SETTING_INPUT_ERROR_MIN = 0x1C
TIC_SETTING_INPUT_ERROR_MAX = 0x1E
TIC_SETTING_INPUT_SCALING_DEGREE = 0x20
TIC_SETTING_INPUT_INVERT = 0x21
TIC_SETTING_INPUT_MIN = 0x22
TIC_SETTING_INPUT_NEUTRAL_MIN = 0x24
TIC_SETTING_INPUT_NEUTRAL_MAX = 0x26
TIC_SETTING_INPUT_MAX = 0x28
TIC_SETTING_OUTPUT_MIN = 0x2A
TIC_SETTING_INPUT_AVERAGING_ENABLED = 0x2E
TIC_SETTING_INPUT_HYSTERESIS = 0x2F
TIC_SETTING_CURRENT_LIMIT_DURING_ERROR = 0x31
TIC_SETTING_OUTPUT_MAX = 0x32
TIC_SETTING_SWITCH_POLARITY_MAP = 0x36
TIC_SETTING_ENCODER_POSTSCALER = 0x37
TIC_SETTING_SCL_CONFIG = 0x3B
TIC_SETTING_SDA_CONFIG = 0x3C
TIC_SETTING_TX_CONFIG = 0x3D
TIC_SETTING_RX_CONFIG = 0x3E
TIC_SETTING_RC_CONFIG = 0x3F
TIC_SETTING_CURRENT_LIMIT = 0x40
TIC_SETTING_STEP_MODE = 0x41
TIC_SETTING_DECAY_MODE = 0x42
TIC_SETTING_STARTING_SPEED = 0x43
TIC_SETTING_MAX_SPEED = 0x47
TIC_SETTING_MAX_DECEL = 0x4B
TIC_SETTING_MAX_ACCEL = 0x4F
TIC_SETTING_SOFT_ERROR_RESPONSE = 0x53
TIC_SETTING_SOFT_ERROR_POSITION = 0x54
TIC_SETTING_ENCODER_PRESCALER = 0x58
TIC_SETTING_ENCODER_UNLIMITED = 0x5C
TIC_SETTING_KILL_SWITCH_MAP = 0x5D
TIC_SETTING_SERIAL_RESPONSE_DELAY = 0x5E
TIC_SETTING_LIMIT_SWITCH_FORWARD_MAP = 0x5F
TIC_SETTING_LIMIT_SWITCH_REVERSE_MAP = 0x60
TIC_SETTING_HOMING_SPEED_TOWARDS = 0x61
TIC_SETTING_HOMING_SPEED_AWAY = 0x65
TIC_SETTING_SERIAL_DEVICE_NUMBER_HIGH = 0x69
TIC_SETTING_SERIAL_ALT_DEVICE_NUMBER = 0x6A
TIC_SETTING_AGC_MODE = 0x6C
TIC_SETTING_AGC_BOTTOM_CURRENT_LIMIT = 0x6D
TIC_SETTING_AGC_CURRENT_BOOST_STEPS = 0x6E
TIC_SETTING_AGC_FREQUENCY_LIMIT = 0x6F
TIC_SETTINGS_SIZE = 0x70

#TIC_SETTINGS_SIZE = 0x5F

TIC_BAUD_RATE_GENERATOR_FACTOR = 12000000
TIC_MAX_USB_RESPONSE_SIZE = 128
TIC_INPUT_NULL = 0xFFFF
TIC_CONTROL_PIN_COUNT = 5

# addtional for pytic
# tic use 0x40 for commands - host to device, standard, to device
TIC_REQUESTTYPE_CMD = usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE
# 0x80
TIC_REQUEST_FIRMWARE_VERSION =  usb.util.CTRL_IN | usb.util.CTRL_TYPE_STANDARD | usb.util.CTRL_RECIPIENT_DEVICE
#
TIC_REQUEST_VARIABLES = usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE

ERROR_NAMES = {}
ERROR_NAMES[TIC_ERROR_INTENTIONALLY_DEENERGIZED] = "Intentionally de-energized"
ERROR_NAMES[TIC_ERROR_MOTOR_DRIVER_ERROR] = "Motor driver error"
ERROR_NAMES[TIC_ERROR_LOW_VIN] = "Low VIN"
ERROR_NAMES[TIC_ERROR_KILL_SWITCH] = "Kill switch active"
ERROR_NAMES[TIC_ERROR_REQUIRED_INPUT_INVALID] = "Required input invalid"
ERROR_NAMES[TIC_ERROR_SERIAL_ERROR] = "Serial error"
ERROR_NAMES[TIC_ERROR_COMMAND_TIMEOUT] = "Command timeout"
ERROR_NAMES[TIC_ERROR_SAFE_START_VIOLATION] = "Safe start violation"
ERROR_NAMES[TIC_ERROR_ERR_LINE_HIGH] = "ERR line high"
ERROR_NAMES[TIC_ERROR_SERIAL_FRAMING] = "Serial framing"
ERROR_NAMES[TIC_ERROR_SERIAL_RX_OVERRUN] = "Serial RX overrun"
ERROR_NAMES[TIC_ERROR_SERIAL_FORMAT] = "Serial format"
ERROR_NAMES[TIC_ERROR_SERIAL_CRC] = "Serial CRC"
ERROR_NAMES[TIC_ERROR_ENCODER_SKIP] = "Encoder skip"

TIC03A_CURRENT_TABLE = \
    [
      0,
      1,
      174,
      343,
      495,
      634,
      762,
      880,
      990,
      1092,
      1189,
      1281,
      1368,
      1452,
      1532,
      1611,
      1687,
      1762,
      1835,
      1909,
      1982,
      2056,
      2131,
      2207,
      2285,
      2366,
      2451,
      2540,
      2634,
      2734,
      2843,
      2962,
      3093
    ]

TIC03A_RECOMMENDED_CODES = \
    [
    0,   1,   2,   3,   4,   5,   6,   7,
    8,   9,   10,  11,  12,  13,  14,  15,
    16,  17,  18,  19,  20,  21,  22,  23,
    24,  25,  26,  27,  28,  29,  30,  31,
    32,
    ]

TIC01A_RECOMMENDED_CODES = \
    [
    0,   1,   2,   3,   4,   5,   6,   7,
    8,   9,   10,  11,  12,  13,  14,  15,
    16,  17,  18,  19,  20,  21,  22,  23,
    24,  25,  26,  27,  28,  29,  30,  31,
    32,  34,  36,  38,  40,  42,  44,  46,
    48,  50,  52,  54,  56,  58,  60,  62,
    64,  68,  72,  76,  80,  84,  88,  92,
    96,  100, 104, 108, 112, 116, 120, 124,
    ]


class TicError(Exception):
    pass


class TicDevice:
    # Encapsulates the logic to control a tic stepper driver
    def __init__(self):
        self.timeout = None
        self.version = None
        self.serial = None
        self.product = None
        self.current_table = None
        self.current_table_max = None
        self.dev = None
        self.cfg = None
        self.intf = None
        self.poll_period = .01
        self.variables={}
        self.init_defaults()

    def close(self):
        self.dev = None
        self.init_defaults()

    def init_defaults(self):
        self.timeout = 1000
        self.version = None
        self.serial = None
        self.product = None
        self.dev = None
        self.cfg = None
        self.intf = None

    def open(self, product_id=None, serial=None, vendor=0xffb):
        self.init_defaults()
        devices = usb.core.find(find_all=True, idVendor=vendor) #, idProduct=product_id)
        for device in devices:
            if serial is None or device.serial_number == serial:
                self.dev = device
                exit  # we take the first unit that matches if no serial number supplied

        if self.dev is None:
            raise TicError('tic device not found.')
        else:
            self.serial = self.dev.serial_number
            self.version =  str((self.dev.bcdDevice >> 12) & 0xf) + \
                            str((self.dev.bcdDevice >> 8) & 0xf) + \
                            '.' + \
                            str((self.dev.bcdDevice >> 4) & 0xf) + \
                            str(self.dev.bcdDevice & 0xf)
            # log.debug("tic open complete. Serial:" + self.serial + " Version:" + self.version)
            self.dev.set_configuration()
            self.cfg = self.dev[0]
            self.intf = self.cfg[(0, 0)]
            self.product_id = product_id
            self.current_defaults_for_product()

    def transfer(self, request_type=TIC_REQUESTTYPE_CMD, request=0, value=0, index=0, data_or_length=0, timeout=None, msg=""):
        if self.dev is None:
            raise TicError("Device not connected")
        # log.debug("tic" + self.serial + " - " + msg + " Req:" + hex(request) + " Val:" + str(value) + " Ind:" + str(index))
        if timeout is None:
            timeout = self.timeout
        try:
            result = self.dev.ctrl_transfer(bmRequestType=request_type,
                                   bRequest=request,
                                   wValue=value,
                                   wIndex=index,
                                   data_or_wLength=data_or_length,
                                   timeout=timeout)
        except:
            log.error(msg)
            #if the request type or request is invalid ussually fails with
            #usb.core.USBError: [Errno 32] Pipe error
            raise TicError()
        return result

    def transfer_32bit(self, request, data, msg=""):
        # 32-bit write command
        value = data & 0xFFFF
        index = data >> 16 & 0xFFFF
        self.transfer(request=request, value=value, index=index, msg=msg)

    def transfer_block(self, cmd, data, msg=""):
        transfer(bmRequestType=40, bRequest=cmd, wValue=value, wIndex=index, data_or_wLength=None, timeout=self.timeout)
        # reads a block of data from the Tic; the block starts from the specified offset and can have a variable length

    # thin wrappers around the USB access code
    def set_setting_byte(self, address, byte):
        self.transfer(request=TIC_CMD_SET_SETTING, value=address, index=byte, msg="applying settings")

    # usb tic commands - anything issued via a tic command is volatile
    def halt_and_hold(self):
        self.transfer(request=TIC_CMD_HALT_AND_HOLD, msg="halting.")

    def reset_command_timeout(self):
        self.transfer(request= TIC_CMD_RESET_COMMAND_TIMEOUT, msg="resetting the command timeout.")

    def deenergize(self):
        self.transfer(request=TIC_CMD_DEENERGIZE, msg="deenergizing.")

    def energize(self):
        self.transfer(request=TIC_CMD_ENERGIZE, msg="energizing.")

    def exit_safe_start(self):
        self.transfer(request=TIC_CMD_EXIT_SAFE_START, msg="exiting safe start.")

    def enter_safe_start(self):
        self.transfer(request=TIC_CMD_ENTER_SAFE_START, msg="entering safe start.")

    def reset(self):
        self.transfer(request=TIC_CMD_RESET, msg="sending the Reset command.")

    def clear_driver_error(self):
        self.transfer(request=TIC_CMD_CLEAR_DRIVER_ERROR, msg="clearing the driver error.")

    def reinitialize(self):
        self.transfer(request=TIC_CMD_REINITIALIZE, msg="reinitializing the device.")

    def start_bootloader(self):
        self.transfer(request=TIC_CMD_START_BOOTLOADER, msg="starting the bootloader.")

    def set_target_position(self, position):
        self.transfer_32bit(request=TIC_CMD_SET_TARGET_POSITION,
                            data=position,
                            msg="setting the target position.")

    def set_target_velocity(self, velocity):
        self.transfer_32bit(request=TIC_CMD_SET_TARGET_VELOCITY,
                            data=velocity,
                            msg="setting the target velocity.")

    def halt_and_set_position(self, position):
        self.transfer_32bit(request=TIC_CMD_HALT_AND_SET_POSITION,
                            data=position,
                            msg="halting and setting the position.")

    def set_max_speed(self, max_speed):
        self.transfer_32bit(request=TIC_CMD_SET_MAX_SPEED,
                            data=max_speed,
                            msg="setting the maximum speed.")

    def set_starting_speed(self, starting_speed):
        self.transfer_32bit(request=TIC_CMD_SET_STARTING_SPEED,
                            data=starting_speed,
                            msg="setting the starting speed.")

    def set_max_accel(self, max_accel):
        self.transfer_32bit(request=TIC_CMD_SET_MAX_ACCEL,
                            data=max_accel,
                            msg="setting the maximum acceleration.")

    def set_max_decel(self, max_decel):
        self.transfer_32bit(request=TIC_CMD_SET_MAX_DECEL,
                            data=max_decel,
                            msg="setting the maximum deceleration.")

    def set_step_mode(self, step_mode):
        self.transfer(request = TIC_CMD_SET_STEP_MODE,
                      value = step_mode,
                      msg = "setting the step mode.")

    def set_decay_mode(self, decay_mode):
        self.transfer(request = TIC_CMD_SET_DECAY_MODE,
                      value = decay_mode,
                      msg="setting the decay mode.")

    def set_current_limit_code(self, value):
        #directly send value - check code for correct values
        self.transfer(request=TIC_CMD_SET_CURRENT_LIMIT,
                      value = value,
                      msg="setting the current limit.")

    def get_firmware_mod_array(self):

        buffer = self.transfer(request_type= usb.util.CTRL_IN | usb.util.CTRL_TYPE_STANDARD | usb.util.CTRL_RECIPIENT_DEVICE,
                      request= USB_REQUEST_GET_DESCRIPTOR,
                      value = (USB_DESCRIPTOR_TYPE_STRING << 8) | TIC_FIRMWARE_MODIFICATION_STRING_INDEX,
                      data_or_length = 256,
                      msg="getting modified firmware version.")
        #Ignore the modification string if it is just a dash.
        if len (buffer) == 4 and buffer[2]== 45:
            buffer = None
        return buffer

    def wait_for_device_ready(self):
        self.get_variables()
        while self.variables ['operation_state'] != 10:
            self.get_variables()
            es = self.get_error_status(self.variables['error_status'])
            # log.debug ("op state:" + str(self.variables ['operation_state']) + " err:" + \
                       # str(self.variables ['error_status']) + " " + es )
            time.sleep(self.poll_period)
            ticdev.reset_command_timeout()
#         log.debug (str(self.variables ['operation_state']) + " err:" + \
#                        str(self.variables ['error_status'])
#                       )

    def wait_for_move_complete(self):
        self.get_variables()
        while (self.variables ['operation_state'] == 10 and \
            self.variables ['current_position'] != self.variables ['target_position'] ):
            if self.variables ['input_state'] == 2:
                break
            if self.variables ['input_state'] == 1:
                break

            self.get_variables()
         # log.debug ("operation state:" + \
         #               str(self.variables ['operation_state']) + " input state:" + \
         #               str(self.variables ['input_state']) + " err:" + \
         #               str(self.variables ['error_status']) + " curr:" + \
         #               str(self.variables ['current_position']) + " tar:" + \
         #               str(self.variables ['target_position']) + " - " + \
         #               str(self.variables ['current_velocity'])         )

            if self.variables ['operation_state'] != 10:
                raise
            time.sleep(self.poll_period)
            #ticdev.reset_command_timeout()

    def get_status_variables (self, clear_errors = False):
        assert(TIC_VARIABLES_SIZE <= TIC_MAX_USB_RESPONSE_SIZE)
        if clear_errors:
            cmd = TIC_CMD_GET_VARIABLE_AND_CLEAR_ERRORS_OCCURRE
        else:
            cmd = TIC_CMD_GET_VARIABLE
        # log.debug (hex(TIC_REQUEST_VARIABLES))
        buffer = self.transfer(request_type= TIC_REQUEST_VARIABLES,
                               request= cmd,
                               data_or_length =  TIC_VARIABLES_SIZE,
                               msg="getting variables.")
        self.parse_status_variables (buffer)

    def get_error_status(self, val):
        s = ""
        for k, v in sorted(ERROR_NAMES.items()):
            if ( 1 << k  & val):
                s = s + str(v) + "(" + str(k) + ") "
        return s


    def parse_status_variables (self, buffer):
        self.variables['operation_state'] = int.from_bytes (buffer [TIC_VAR_OPERATION_STATE:TIC_VAR_OPERATION_STATE+1],byteorder='little')
        self.variables['energized_position_uncertain'] = int.from_bytes (buffer [0x1:0x2],byteorder='little')
        self.variables['error_status'] = int.from_bytes (buffer [0x2:0x4],byteorder='little')

    def get_variables(self, clear_errors = False):
        assert(TIC_VARIABLES_SIZE <= TIC_MAX_USB_RESPONSE_SIZE)
        if clear_errors:
            cmd = TIC_CMD_GET_VARIABLE_AND_CLEAR_ERRORS_OCCURRE
        else:
            cmd = TIC_CMD_GET_VARIABLE
        buffer = self.transfer(request_type= TIC_REQUEST_VARIABLES,
                               request= cmd,
                               data_or_length =  TIC_VARIABLES_SIZE,
                               msg="getting variables.")

        self.parse_status_variables (buffer)
        self.variables['planning_mode'] = int.from_bytes (buffer [TIC_VAR_PLANNING_MODE:TIC_VAR_PLANNING_MODE+1],byteorder='little')
        self.variables['target_position'] = int.from_bytes ( buffer [TIC_VAR_TARGET_POSITION:TIC_VAR_TARGET_POSITION+4],byteorder='little', signed=True)
        self.variables['target_velocity'] = int.from_bytes ( buffer [TIC_VAR_TARGET_VELOCITY:TIC_VAR_TARGET_VELOCITY+4],byteorder='little', signed=True)
        self.variables['starting_speed'] = int.from_bytes ( buffer [TIC_VAR_STARTING_SPEED:TIC_VAR_STARTING_SPEED+4],byteorder='little')
        self.variables['max_speed'] = int.from_bytes ( buffer [TIC_VAR_MAX_SPEED:TIC_VAR_MAX_SPEED+4],byteorder='little')
        self.variables['max_decel'] = int.from_bytes ( buffer [TIC_VAR_MAX_DECEL:TIC_VAR_MAX_DECEL+4],byteorder='little')
        self.variables['max_accel'] = int.from_bytes ( buffer [TIC_VAR_MAX_ACCEL:TIC_VAR_MAX_ACCEL+4],byteorder='little')
        self.variables['current_position'] = int.from_bytes ( buffer [TIC_VAR_CURRENT_POSITION:TIC_VAR_CURRENT_POSITION +4],byteorder='little', signed=True)
        self.variables['current_velocity'] = int.from_bytes ( buffer [TIC_VAR_CURRENT_VELOCITY:TIC_VAR_CURRENT_VELOCITY+4],byteorder='little', signed=True)
        self.variables['acting_target_position'] = int.from_bytes ( buffer [TIC_VAR_ACTING_TARGET_POSITION:TIC_VAR_ACTING_TARGET_POSITION +4],byteorder='little', signed=True)
        self.variables['time_since_last_step'] = int.from_bytes ( buffer [TIC_VAR_TIME_SINCE_LAST_STEP :TIC_VAR_TIME_SINCE_LAST_STEP +4],byteorder='little')
        self.variables['device_reset'] = int.from_bytes (buffer [TIC_VAR_DEVICE_RESET:TIC_VAR_DEVICE_RESET+1],byteorder='little')
        self.variables['vin_voltage'] = int.from_bytes (buffer [TIC_VAR_VIN_VOLTAGE:TIC_VAR_VIN_VOLTAGE +2],byteorder='little') / 1000
        self.variables['up_time'] = int.from_bytes ( buffer [TIC_VAR_UP_TIME:TIC_VAR_UP_TIME+4],byteorder='little')
        self.variables['encoder_position'] = int.from_bytes ( buffer [TIC_VAR_ENCODER_POSITION:TIC_VAR_ENCODER_POSITION+4], byteorder='little', signed=True)
        self.variables['rc_pulse_width'] = int.from_bytes (buffer [TIC_VAR_RC_PULSE_WIDTH:TIC_VAR_RC_PULSE_WIDTH+2],byteorder='little')
        self.variables['step_mode'] = int.from_bytes ( buffer [TIC_VAR_STEP_MODE:TIC_VAR_STEP_MODE +1], byteorder="little")
        self.variables['current_limit'] = int.from_bytes (buffer [TIC_VAR_CURRENT_LIMIT:TIC_VAR_CURRENT_LIMIT+1],byteorder='little')
        self.variables['decay_mode'] = int.from_bytes ( buffer [TIC_VAR_DECAY_MODE:TIC_VAR_DECAY_MODE+1],byteorder='little')
        self.variables['input_state'] = int.from_bytes ( buffer [TIC_VAR_INPUT_STATE:TIC_VAR_INPUT_STATE+1],byteorder='little')
        self.variables['input_after_averaging'] = int.from_bytes (buffer [TIC_VAR_INPUT_AFTER_AVERAGING:TIC_VAR_INPUT_AFTER_AVERAGING+2],byteorder='little')
        self.variables['input_after_hysteresis'] = int.from_bytes (buffer [TIC_VAR_INPUT_AFTER_HYSTERESIS:TIC_VAR_INPUT_AFTER_HYSTERESIS+2],byteorder='little')
        self.variables['input_after_scaling'] = int.from_bytes ( buffer [TIC_VAR_INPUT_AFTER_SCALING:TIC_VAR_INPUT_AFTER_SCALING+2],byteorder='little', signed=True)


        #log.debug (self.variables['step_mode'])
        #for k, v in sorted(self.variables.items()):
                #    log.debug ( k + " - " + str(v))
        '''
        TIC_VAR_MISC_FLAGS1 = 0x01
        TIC_VAR_ERROR_STATUS = 0x02
        TIC_VAR_ERRORS_OCCURRED = 0x04
        
        TIC_VAR_ANALOG_READING_SCL = 0x3F
        TIC_VAR_ANALOG_READING_SDA = 0x41
        TIC_VAR_ANALOG_READING_TX = 0x43
        TIC_VAR_ANALOG_READING_RX = 0x45
        TIC_VAR_DIGITAL_READINGS = 0x47
        TIC_VAR_PIN_STATES = 0x48
        '''

    def current_defaults_for_product( self):
        if self.product_id ==  TIC_PRODUCT_ID_T500:
            self.product = TIC_PRODUCT_T500
            self.current_max = TIC_MAX_ALLOWED_CURRENT_T500
            self.current_table = TIC03A_RECOMMENDED_CODES
            self.current_table_count = len(TIC03A_CURRENT_TABLE)
        elif self.product_id ==  TIC_PRODUCT_ID_T834:
            # Some of the codes at the end of the table are too high; they violate
            # TIC_MAX_ALLOWED_CURRENT_T834.  So just return a count lower than the
            # actual number of items in the table.
            self.product = TIC_PRODUCT_T834
            self.current_max = TIC_MAX_ALLOWED_CURRENT_T834
            self.current_table = TIC01A_RECOMMENDED_CODES
            self.current_table_count = 60;
        elif self.product_id == TIC_PRODUCT_ID_T825:
            self.product = TIC_PRODUCT_T825
            self.current_max = TIC_MAX_ALLOWED_CURRENT_T825
            self.current_table = TIC01A_RECOMMENDED_CODES
            self.current_table_count = len(TIC01A_RECOMMENDED_CODES)
        else:
            self.product = None
            self.current_max = None
            self.current_table = None
            self.current_table_count = None

    def current_limit_code_to_ma(self, code):
        if self.product == TIC_PRODUCT_T500:
            if code > TIC_MAX_ALLOWED_CURRENT_CODE_T500:
                code = TIC_MAX_ALLOWED_CURRENT_CODE_T500
            return TIC03A_CURRENT_TABLE[code]
        else:
            max = self.current_max / TIC_CURRENT_LIMIT_UNITS_MA
            if code > max:
                code = max
            elif code > 64:
                code = code * 4
            elif code > 32:
                code = code * 2
            return code * TIC_CURRENT_LIMIT_UNITS_MA

    def current_limit_ma_to_code(self, ma):
        #   Assumption: The table is an ascending order, so we want to return the last
        #   one that is less than or equal to the desired current.
        #   Assumption: 0 is a valid code and a good default to use.
        code = 0;
        for i in range (0 , self.current_table_count - 1):
            #recomended_current_code = self.current_table_recomended_count
            table_ma = self.current_limit_code_to_ma(i)
            if  table_ma <= ma:
                code = i
            else:
                break
        return code;

    def code_test(self):
        self.product_id = TIC_PRODUCT_ID_T500
        self.current_defaults_for_product ()
        code = self.current_limit_ma_to_code(1000)
        # log.debug ( str(TIC_PRODUCT_ID_T500) + " - " + str(code) + " - " + str(1000) )

    def compute_ilim(self, dac_level):
        v_iset = 0.9
        v_dac_top = 4.096
        r_top = 107000.0
        r_bot = 33000.0

        r_dac_top = (32 - dac_level) * 5000
        r_dac_bot = dac_level * 5000

        v_dacout = v_dac_top * r_dac_bot / (r_dac_bot + r_dac_top)
        if dac_level == 0:
            r_dacout = 0
        else:
            r_dacout = 1 / (1 / r_dac_top + 1 / r_dac_bot)

        iset_current_sourced = (v_iset - v_dacout) / (r_top + r_dacout) + v_iset / r_bot

        if iset_current_sourced < 0:
            iset_current_sourced = 0

        iset_current_sourced = iset_current_sourced * 86666 * 1000
        iset_current_sourced = int (round(iset_current_sourced))
        return iset_current_sourced

    def log_ilim (self):
        for dac_level in range (31,-1, -1):
            log.debug (str (dac_level) +"  --  " + str (self.compute_ilim(dac_level)))

if __name__ == '__main__':

    step_factor = 8
    ticdev = TicDevice()
    ticdev.log_ilim()
    ticdev.code_test()
    #ticdev.open(vendor=0x1ffb, product_id=TIC_PRODUCT_ID_T500, serial="00218293")
    ticdev.open(vendor=TIC_VENDOR_ID)
    # quick test
    ticdev.reset()
    ticdev.reset_command_timeout()
    ticdev.clear_driver_error()
    ticdev.exit_safe_start()
    ticdev.halt_and_set_position(0)
    ticdev.set_current_limit_code(21)
    ticdev.wait_for_device_ready()
    ticdev.exit_safe_start()
    #ticdev.get_variables()
    ticdev.set_max_speed(12000000 * step_factor)
    ticdev.set_max_accel(100000 * step_factor)
    ticdev.set_max_decel(100000 * step_factor)
    ticdev.exit_safe_start()
    ticdev.set_starting_speed(0)
    ticdev.wait_for_device_ready()
    ticdev.energize()
    ticdev.wait_for_device_ready()
    ticdev.set_target_position (-1650 * step_factor)
    ticdev.wait_for_move_complete()
    #this will trigger command time out....
    time.sleep(1.5)
    ticdev.set_target_position(-1550 * step_factor )
    ticdev.wait_for_move_complete()
    ticdev.halt_and_set_position(0)
    #does not clear target postion
    ticdev.wait_for_move_complete()
    while True:
        ticdev.set_target_position(400 * step_factor)
        ticdev.wait_for_move_complete()
        ticdev.set_target_position(0)
        ticdev.wait_for_move_complete()


