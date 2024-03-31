import time
import tkinter as tk
from tkinter import scrolledtext
import threading
from enum import Enum
from serial_manager import SerialManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from threading import Event


class GUIManager:
    """
    Class for managing the GUI of the CLI application.
    """
    class FixedStrings(Enum):
        """
        Enum class for fixed strings.
        """
        WELCOME_MESSAGE = "Welcome to HelMate Python Terminal\nCreated by Saurabh Parulekar\n"
        GUI_PREFIX = "GUI>>"
        DEVICE_PREFIX = "DEV>>"


    class CLICommands(Enum):
        """
        Enum class for Command strings.
        """
        RESET = "reset\n"
        VERSION = "version\n"
        TICKS = "ticks\n"
        IMU = "imu\n"

    def __init__(self) -> None:
        """
        Initialize the GUIManager.
        """
        self.graph_event = Event()
        self.accelerometer_values = {'x':[],'y':[],'z':[]}
        print("Gui Initialized")

    def init_serial_manager(self) -> None:
        """
        Initialize the SerialManager and start threads for finding EDBG port and updating light indicator.
        """
        self.serial_manager = SerialManager(self.print_gui, self.print_device)
        self.__start_thread(self.serial_manager.find_edbg_port)
        self.__start_thread(function=self.update_light_indicator)
        self.__start_thread(function=self.graph_accelerometer_values)

    def print_gui(self, string: str) -> None:
        """
        Print a message in the GUI.

        :param string: The message to print.
        """
        print(string)
        self.text_box.insert(tk.END, f"{self.FixedStrings.GUI_PREFIX.value}{string}\n")
        self.scroll_to_bottom()

    def print_device(self, string: str) -> None:
        """
        Print a device-related message in the GUI.

        :param string: The device-related message to print.
        """
        print(string)
        self.text_box.insert(tk.END, f"{self.FixedStrings.DEVICE_PREFIX.value}{string}\n")
        self.scroll_to_bottom()

    @staticmethod
    def __start_thread(function: callable, **kwargs: dict) -> None:
        """
        Start a new thread for the given function with optional arguments.

        :param function: The function to run in a new thread.
        :param kwargs: Optional keyword arguments for the function.
        """
        new_thread = threading.Thread(target=function, kwargs=kwargs)
        new_thread.start()

    def reset_text(self) -> None:
        """
        Reset the text in the GUI text box.
        """
        self.text_box.delete('1.0', tk.END)

    def scroll_to_bottom(self, *args) -> None:
        """
        Scroll the text box to the bottom.
        """
        self.text_box.yview_moveto(1.0)

    def close_window(self) -> None:
        """
        Close the GUI window.
        """
        self.root.destroy()

    def update_light_indicator(self) -> None:
        """
        Continuously update the light indicator based on serial connection status.
        """
        while True:
            if self.serial_manager.ser is not None:
                if self.serial_manager.ser.is_open:
                    self.canvas.itemconfig(self.light_indicator, fill="green")
                else:
                    self.canvas.itemconfig(self.light_indicator, fill="red")
            time.sleep(0.5)

    def graph_accelerometer_values(self) -> None:
        """
        Continuously update the graph with accelerometer values.
        """
        while True:
            if self.graph_event.is_set():
                self.serial_manager.send_data(self.CLICommands.IMU.value)
                while("Ax" not in self.serial_manager.data and self.serial_manager.data is not None): pass
                print(self.serial_manager.data)
                accelerometer_data = self.parse_accelerometer_data()
                if accelerometer_data:
                    self.accelerometer_values['x'].append(accelerometer_data['x'])
                    self.accelerometer_values['y'].append(accelerometer_data['y'])
                    self.accelerometer_values['z'].append(accelerometer_data['z'])
                    self.update_graph()
                time.sleep(0.1)

    def parse_accelerometer_data(self)->dict:
        """
        For me data looks like "Ax: -4, Ay: -4, Az: 1017", write a a different code to parse your data
        """
        accelerometer_data_dict = {"x":0,"y":0,"z":0}
        if "Ax" in self.serial_manager.data:
            print("what")
            acc_data = self.serial_manager.data
            split_str = acc_data.split(",")
            print(acc_data)
            print(split_str)
            if acc_data:
                for index, axis in enumerate(accelerometer_data_dict.keys()):
                    accelerometer_data_dict[axis] = int(split_str[index].split(":")[1])
            return accelerometer_data_dict
        return None

    def update_graph(self):
        """
        Update the graph with accelerometer values.
        """
        print("Plotting Graph")
        self.ax.clear()
        self.ax.plot(self.accelerometer_values['x'], label='X-axis')
        self.ax.plot(self.accelerometer_values['y'], label='Y-axis')
        self.ax.plot(self.accelerometer_values['z'], label='Z-axis')
        self.ax.legend()
        self.ax.set_title('Accelerometer Values')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Acceleration')
        self.figure_canvas.draw()

    def run_gui(self) -> None:
        """
        Run the GUI application.
        """
        self.root = tk.Tk()
        self.root.title("Python GUI for CLI")

        # Create Matplotlib figure and embed it into Tkinter window
        self.figure, self.ax = plt.subplots()
        self.figure_canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.figure_canvas.get_tk_widget().pack(side=tk.LEFT, padx=5, pady=5)

        # Create scrollable text box
        self.text_box = scrolledtext.ScrolledText(self.root, width=60, height=20, wrap=tk.WORD)
        self.text_box.pack(pady=10)



        # Add initial text to the text box
        self.text_box.insert(tk.END, self.FixedStrings.WELCOME_MESSAGE.value)

        # Auto-scroll when more text is added
        self.text_box.bind("<<Modified>>", self.scroll_to_bottom)
        self.text_box.bind("<Configure>", self.scroll_to_bottom)

        

        # Create buttons
        reset_button_cli = tk.Button(self.root, text="Reset CLI", command=self.reset_text)
        reset_button_cli.pack(side=tk.LEFT, padx=5, pady=5)

        search_device = tk.Button(self.root, text="Search Device and Connect", command=self.init_serial_manager)
        search_device.pack(side=tk.LEFT, padx=5, pady=5)

        disconnect_button = tk.Button(self.root, text="Disconnect Device", command=lambda: self.serial_manager.deinitialize_serial())
        disconnect_button.pack(side=tk.LEFT, padx=5, pady=5)

        version_button = tk.Button(self.root, text="Get Firmware Version", command=lambda: self.serial_manager.send_data(self.CLICommands.VERSION.value))
        version_button.pack(side=tk.LEFT, padx=5, pady=5)

        tick_button = tk.Button(self.root, text="Get Current Ticks", command=lambda: self.serial_manager.send_data(self.CLICommands.TICKS.value))
        tick_button.pack(side=tk.LEFT, padx=5, pady=5)

        reset_button = tk.Button(self.root, text="Reset Device", command=lambda: self.serial_manager.send_data(self.CLICommands.RESET.value))
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        graph_start_button = tk.Button(self.root, text="Start Graph", command=lambda: self.graph_event.set())
        graph_start_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        graph_stop_button = tk.Button(self.root, text="Stop Graph", command=lambda: self.graph_event.clear())
        graph_stop_button.pack(side=tk.BOTTOM, padx=5, pady=5)

        close_button = tk.Button(self.root, text="Close CLI", command=self.close_window)
        close_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Create canvas for light indicator
        self.canvas = tk.Canvas(self.root, width=30, height=30)
        self.canvas.pack(side=tk.LEFT, padx=5, pady=5)
        self.light_indicator = self.canvas.create_oval(5, 5, 25, 25, fill="red")

        

        self.root.mainloop()

if __name__ == "__main__":
    gui_manager = GUIManager()
    gui_manager.run_gui()
