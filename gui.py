import tkinter as tk
import RPi.GPIO as gpio
import time

class Radiobutton():
    
    _next_value = 1
    
    @classmethod
    def next_value(cls):
        Radiobutton._next_value = Radiobutton._next_value + 1
        return Radiobutton._next_value - 1
    
    def __init__(self, label, convar, command):
        self.widget = tk.Radiobutton(
            text = label,
            command = command,
            variable = convar,
            value = Radiobutton.next_value(),
            width = 30,
            height = 5
        )
        self.widget.pack()
        self.state = False

class RadiobuttonGroup():
    
    def generate_callback(self, command, index):
        def callback():
            if self.selected is None:
                self.selected = self.buttons[index]
                self.selected.state = True
            else:
                if self.selected == self.buttons[index]:
                    return
                else:
                    self.selected = self.buttons[index]
                    for button in self.buttons:
                        button.state = False
                    self.selected.state = True
            command()
        return callback
    
    def __init__(self, buttons):
        self.convar = tk.IntVar()
        self.buttons = [None]*len(buttons)
        for index, button in enumerate(buttons):
            self.buttons[index] = Radiobutton(
                button[0],
                self.convar,
                self.generate_callback(button[1], index)
            )
        self.selected = None

window = tk.Tk()

def loop(func, period):
    def wrapped():
        func()
        window.after(period, wrapped)
    wrapped()
    
#####################

gpio.setmode(gpio.BOARD)

patterns = [
    ("No LEDs", ()),
    ("Left LED", 13),
    ("Center LED", 15),
    ("Right LED", 11),
    ("All LEDs", (11, 15, 13))
]

leds = set()
for pattern in patterns:
    if isinstance(pattern[1], int):
        leds.add(pattern[1])
    else:
        leds.update(pattern[1])

for led in leds:
    gpio.setup(led, gpio.OUT)
    
class Blink():
    pin = None
    
    cycle = 0
    period = 100 # milliseconds
    
    high_time = 200
    low_time = 300
    
    @staticmethod
    def set_pin(pin):
        for led in leds:
            gpio.output(led, gpio.LOW)
        Blink.pin = pin
        
    @staticmethod
    def do_cycle():
        inner_cycle = Blink.cycle
        inner_cycle %= (Blink.high_time + Blink.low_time) // Blink.period
        
        if inner_cycle == 0:
            gpio.output(Blink.pin, gpio.HIGH)
        elif inner_cycle == Blink.high_time // Blink.period:
            gpio.output(Blink.pin, gpio.LOW)
        
        Blink.cycle += 1
    
Blink.set_pin(())

###################
    
radiobutton_group = RadiobuttonGroup(
    list(map(
        lambda index, pattern : (
            pattern[0],
            lambda : Blink.set_pin(pattern[1])
        ),
        range(len(patterns)), patterns
    ))
)

exit_button = tk.Button(
    text = "Exit",
    command = lambda : window.destroy()
)
exit_button.pack()

###########W

window.eval(f'tk::PlaceWindow {window.winfo_pathname(window.winfo_id())} center')

loop(Blink.do_cycle, Blink.period)
window.mainloop()

gpio.cleanup()