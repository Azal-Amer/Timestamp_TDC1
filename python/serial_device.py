from __future__ import print_function  # Needed for compatibility with Py2
"""
Author: Alessandro Cere
Modified by: Chin Chean Lim, 03/06/2019
Created: 2017.10.16

Description:
General serial device
"""
import serial
import time

from serial import SerialException


class SerialDevice(serial.Serial):
    """
    The usb device is seen as an object through this class,
    inherited from the generic serial one.
    """

    def __init__(self, device_path=None, timeout=0.2):
        """
        Initializes the USB device.
        It requires the full path to the serial device as arguments
        """
        try:
            serial.Serial.__init__(self, device_path, timeout)
            self.timeout = timeout
            self.baudrate = 57600
            self.stopbits = serial.STOPBITS_ONE
            self.bytesize = serial.EIGHTBITS
            self.parity = serial.PARITY_NONE
            self._reset_buffers()
        except SerialException:
            print('Connection failed')

    def _reset_buffers(self):
        self.reset_input_buffer()
        self.reset_output_buffer()

    def _getresponse(self, cmd):
        """
        function to send commands and read the response of the device.
        it contains a workaroud for the 'Unknown command' problem.
        Make sure that the command implies a reply, otherwise...

        :param command: string containing the command.
        :return: the reply of the device,
        only the first line and stripped of decorations
        """
        self._reset_buffers()
        self.write((cmd + '\n').encode())
        return self.readlines()

    def _getresponseTime(self, cmd, t_sleep):
        """
        function to send commands and read the response of the device.
        it contains a workaroud for the 'Unknown command' problem.
        Make sure that the command implies a reply, otherwise...

        :param command: string containing the command.
        :return: the reply of the device,
        only the first line and stripped of decorations
        """
        self._reset_buffers()
        self.write((cmd + '\n').encode())
        #self._reset_buffers()

        # time.sleep(0.0015)
        # Buffer_length = self.in_waiting
        # memory1 = self.read(Buffer_length)
        # Rlength1 = len(memory1)
        # time.sleep(0.001)
        # Buffer_length = self.in_waiting
        # memory2 = self.read(Buffer_length)
        # time.sleep(0.001)
        # Buffer_length = self.in_waiting
        # memory3 = self.read(Buffer_length)
        # memory = memory1+memory2+memory3
        # Rlength3 = len(memory3)
        # Rlength2 = len(memory2)
        #Buffer_length = 2000000
        memory = b''
        time0 = time.time()
        while (time.time() - time0 < 2):  # Read data for 5 seconds
            Buffer_length = self.in_waiting
            memory = memory + self.read(Buffer_length)
            #print(memory)
            #time.sleep(0.0001)
        Rlength = len(memory)
        print(str(Rlength) + " Bytes Recorded")
        #print(memory)
        #print(str(Rlength2) + " Bytes Recorded")
        #print(str(Rlength3) + " Bytes Recorded")
        return memory

    def help(self):
        """
        Prints device help to the screen
        """
        ([print(x.decode().strip()) for x in self._getresponse('help')])
