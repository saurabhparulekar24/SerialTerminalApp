import serial
import serial.tools.list_ports
import threading
from threading import Event
from tkinter import END


class SerialManager:
    """
    Class for managing serial communication.
    """

    def __init__(self, print_gui: callable, print_device: callable) -> None:
        """
        Initialize the SerialManager.

        :param print_gui: A function to print GUI messages.
        :param print_device: A function to print device-related messages.
        """
        self.print_gui = print_gui
        self.print_device = print_device
        self.send_event = Event()
        self.ser = None

    def read_serial(self) -> None:
        """
        Read serial data and print it.
        """
        try:
            if self.ser:
                while True:
                    if self.ser.in_waiting > 0:
                        data = self.ser.readline().decode().strip()
                        self.print_device(data)
        except KeyboardInterrupt:
            self.print_gui("Serial reading stopped by user.")
        except serial.SerialException as e:
            self.print_gui(f"Error reading serial data: {e}")

    def initialize_serial(self, port: str, baudrate: int = 115200, bytesize: int = 8, parity: str = 'N', stopbits: int = 1, timeout: int = None) -> serial.Serial:
        """
        Initialize serial communication.

        :param port: The port to initialize communication with.
        :param baudrate: The baudrate for communication.
        :param bytesize: The number of data bits.
        :param parity: The parity setting.
        :param stopbits: The number of stop bits.
        :param timeout: The timeout value for reading operations.
        :return: The serial object if successful, None otherwise.
        """
        try:
            self.ser = serial.Serial(port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
            self.print_gui(f"Serial communication initialized with {port}")
            check_thread = threading.Thread(target=self.read_serial)
            check_thread.start()
            return self.ser
        except serial.SerialException as e:
            self.print_gui(f"Error: {e}")
            return None

    def send_data(self, data: str) -> None:
        """
        Send data over serial.

        :param data: The data to send.
        """
        try:
            if self.ser:
                self.send_event.set()
                self.ser.write(data.encode())
                self.print_gui(f"Data sent: {data}")
                self.send_event.clear()
        except serial.SerialException as e:
            self.print_gui(f"Error sending data: {e}")

    def find_edbg_port(self) -> None:
        """
        Search for EDBG devices.
        """
        self.print_gui(f"Searching EDBG Devices. Please wait...")
        com_ports = serial.tools.list_ports.comports()
        for port in com_ports:
            if "EDBG" in port.description:
                if port.device:
                    self.print_gui(f"EDBG port found: {port.device}")
                    self.initialize_serial(port=port.device)
                else:
                    self.print_gui(f"No EDBG port found.")
                    return None

    def deinitialize_serial(self) -> None:
        """
        Close the serial connection.
        """
        self.ser.close()
