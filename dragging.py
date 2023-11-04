import re
import time
import math
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from Gates import ANDGate, ORGate, NANDGate, NORGate, XORGate, XNORGate
from LeftPanelButton import LeftPanelButton
from Input import Input
from Output import Output
from circuit_analyzer import analyze_circuit

drag_start_time = 0
start_position_x = 0
start_position_y = 0
upper_panel_height = 100
left_panel_width = 175
line_width = 5
input_count = 1

left_panel_button_size = 40
left_panel_button_distance_from_left = 15
left_panel_button_distance_from_top = 90
left_panel_button_distance_between_buttons_top = 50
left_panel_button_label_distance_from_left = 70

upper_panel_button_width = 150
upper_panel_button_height = 75
upper_panel_button_distance_from_left = 200
upper_panel_button_distance_from_top = 10
upper_panel_button_distance_between_buttons_left = 200

analyze_circuit_button_distance_from_left = 75
analyze_circuit_button_distance_from_top = 10
analyze_circuit_button_width = 150
analyze_circuit_button_height = 75

entry_distance_from_left = 10
entry_distance_from_bottom = 125
entry_width = 145
entry_height = 30

title_font_size = 20

pins_title_distance_from_left = 50
pins_title_distance_from_top = 100

gates_title_distance_from_left = 50
gates_title_distance_from_top = 240

pin_size = 30
gate_size = 90

dragging = False
is_line_creating = False

entry = None

current_pin = None

output = None

current_gate = None
last_gate = None
all_gates = [] # It is used to help to save the circuit

buttons = [LeftPanelButton('Input', 'pin'), LeftPanelButton('Output', 'pin'), LeftPanelButton('AND gate', 'gate'), LeftPanelButton('OR gate', 'gate'), LeftPanelButton('NAND gate', 'gate'), LeftPanelButton('NOR gate', 'gate'), LeftPanelButton('XOR gate', 'gate'), LeftPanelButton('XNOR gate', 'gate')]
button_classes = { 'Input': Input, 'Output': Output, 'AND gate': ANDGate, 'OR gate': ORGate, 'NAND gate': NANDGate, 'NOR gate': NORGate, 'XOR gate': XORGate, 'XNOR gate': XNORGate} # hardcoded

all_inputs = []
line_IDs = []

global_root = None

def clear_circuit():
    global output, input_count, current_gate, last_gate, all_gates, all_inputs, line_IDs, dragging, is_line_creating, entry, current_pin
    for gate in all_gates:
        gate.destroy()
        del gate
    all_gates.clear()
    for input in all_inputs:
        input.destroy()
        del input
    all_inputs.clear()
    for line_ID in line_IDs:
        canvas.delete(line_ID)
    line_IDs.clear()
    if output is not None:
        output.destroy()
        del output
        output = None
    input_count = 1 # it's resetted because the inputs will have to start from 1 again
    current_gate = None
    last_gate = None
    dragging = False
    is_line_creating = False
    current_pin = None
    output = None

def create_buttons(root): # this function creates the initial UI elements
    global canvas, entry, entry_text, left_panel_button_distance_from_top, last_gate, global_root
    global_root = root
    background = tk.Canvas(root, bg='white', width=root.winfo_screenwidth(), height=root.winfo_screenheight())
    background.place(x=0, y=0)

    canvas = tk.Canvas(background)
    canvas.place(x=left_panel_width, y=upper_panel_height, relwidth=1, relheight=1, width=-left_panel_width, height=-upper_panel_height)

    left_panel = tk.Frame(root, width=left_panel_width, bg='steelblue')
    left_panel.pack(side='left', fill='y')

    entry_text = tk.StringVar()
    entry = tk.Entry(root, textvariable=entry_text, bd=0)
    entry.place(x=entry_distance_from_left, y=root.winfo_screenheight()-entry_distance_from_bottom, width=entry_width, height=entry_height)
    entry.bind('<Return>', lambda event: set_label_from_entry())

    upper_panel = tk.Frame(root, height=upper_panel_height, bg='#2B547A')
    upper_panel.pack(side='top', fill='x')

    create_upper_panel_buttons(upper_panel, root)

    pins_title = tk.Label(root, text="Pins")
    pins_title.place(x=pins_title_distance_from_left, y=pins_title_distance_from_top)
    pins_title.config(font=("Arial", title_font_size), fg="black", bg="steelblue")

    gates_title = tk.Label(root, text="Gates")
    gates_title.place(x=gates_title_distance_from_left, y=gates_title_distance_from_top)
    gates_title.config(font=("Arial", title_font_size), fg="black", bg="steelblue")

    for i, button in enumerate(buttons):
        image = button.image
        image = image.resize((left_panel_button_size, left_panel_button_size), Image.ANTIALIAS) 
        photo = ImageTk.PhotoImage(image)
        if i == 2:
            left_panel_button_distance_from_top += left_panel_button_size

        left_panel_button = tk.Button(root, image=photo) # the buttons on the left panel, this includes the buttons of the gates and the pins, this buttons are used to create new pins and gates with drag and drop
        left_panel_button.image = photo
        left_panel_button.place(x=left_panel_button_distance_from_left, y=left_panel_button_distance_from_top + (i + 1) * left_panel_button_distance_between_buttons_top)

        left_panel_button.bind("<Button-1>", lambda event: start_drag(event, root))
        left_panel_button.bind("<ButtonRelease-1>", lambda event, btn=button: stop_drag(event, root, btn))
        left_panel_button.name = "original_button"

        left_panel_button_label = tk.Label(root, text=button.name)
        left_panel_button_label.place(x=left_panel_button_label_distance_from_left, y=left_panel_button_distance_from_top + (i + 1) * left_panel_button_distance_between_buttons_top + left_panel_button_size/4)
        left_panel_button_label.config(font=("Arial", 12), fg="black", bg="steelblue")

def create_upper_panel_buttons(upper_panel, root):
        analyze_circuit_button = tk.Button(upper_panel, text="Analyze circuit", font=('Helvetica 15 bold'), bd=0, bg='steelblue', fg='black', activebackground='steelblue', activeforeground='black')
        analyze_circuit_button.place(x=50, y=upper_panel_button_distance_from_top, width=upper_panel_button_width, height=upper_panel_button_height)
        analyze_circuit_button.bind('<Button-1>', lambda event: analyze_circuit(last_gate, all_inputs))

        clear_circuit_button = tk.Button(upper_panel, text="Clear circuit", font=('Helvetica 15 bold'), bd=0, bg='steelblue', fg='black', activebackground='steelblue', activeforeground='black')
        clear_circuit_button.place(x=250, y=upper_panel_button_distance_from_top, width=upper_panel_button_width, height=upper_panel_button_height)
        clear_circuit_button.bind('<Button-1>', lambda event: clear_circuit())

        save_circuit_button = tk.Button(upper_panel, text="Save circuit", font=('Helvetica 15 bold'), bd=0, bg='steelblue', fg='black', activebackground='steelblue', activeforeground='black')
        save_circuit_button.place(x=450, y=upper_panel_button_distance_from_top, width=upper_panel_button_width, height=upper_panel_button_height)
        save_circuit_button.bind('<Button-1>', lambda event: save_circuit(root))

        load_circuit_button = tk.Button(upper_panel, text="Load circuit", font=('Helvetica 15 bold'), bd=0, bg='steelblue', fg='black', activebackground='steelblue', activeforeground='black')
        load_circuit_button.place(x=650, y=upper_panel_button_distance_from_top, width=upper_panel_button_width, height=upper_panel_button_height)
        load_circuit_button.bind('<Button-1>', lambda event: load_circuit())

def create_rotated_rectangle_between_two_points(x1, y1, x2, y2, width): # this function creates a long rectangle between two points, this rectangle is basically the line between the gates or between a pin and a gate
    canvas_x = canvas.winfo_rootx()
    canvas_y = canvas.winfo_rooty()

    x1 -= canvas_x
    y1 -= canvas_y
    x2 -= canvas_x
    y2 -= canvas_y

    dx = x2 - x1
    dy = y2 - y1
    height = math.sqrt(dx**2 + dy**2)
    angle = math.atan2(dy, dx)

    rectangle = [(0, -width/2), (height, -width/2), (height, width/2), (0, width/2)]

    rectangle = [(x1 + math.cos(angle) * rx - math.sin(angle) * ry, y1 + math.sin(angle) * rx + math.cos(angle) * ry) for rx, ry in rectangle]
    
    line = canvas.create_polygon(rectangle)
    line_IDs.append(line)

def connect_buttons(event, button):
    if button.__class__.__base__.__name__ == 'Pin':
        start_line_creation(event, button)
    else:
        if current_pin and not current_gate:
            finish_line_creation_between_pin_and_gate(event, button)
        elif current_gate and not current_pin:
            finish_line_creation_between_gate_and_gate(event, button)
        else:
            start_line_creation(event, button)

def start_line_creation(event, button):
    global drag_start_time, start_position_x, start_position_y, current_pin, current_gate
    if time.time() - drag_start_time < 0.25:
        start_position_x = event.x_root
        start_position_y = event.y_root
        if button.__class__.__base__.__name__ == 'Pin':
            current_pin = button
        else:
            current_gate = button

def finish_line_creation_between_pin_and_gate(event, gate):
    global drag_start_time, start_position_x, start_position_y, current_pin
    if time.time() - drag_start_time < 0.25 and current_pin:
        x = event.x_root
        y = event.y_root  
        
        connect_pin_with_gate(gate, start_position_x, start_position_y, x, y)
            

def connect_pin_with_gate(gate, start_position_x, start_position_y, x, y):
    global last_gate, current_gate, current_pin

    can_connection_be_created_between_gate_and_pin = False
    print(type(current_pin).__name__)
    if type(current_pin).__name__ == 'Input' and current_pin not in gate.inputs:
        gate.inputs.append(current_pin)
        all_inputs.append(current_pin)
        can_connection_be_created_between_gate_and_pin = True
    elif type(current_pin).__name__ == 'Output' and current_pin != gate.output:
        gate.output = current_pin
        can_connection_be_created_between_gate_and_pin = True

    if can_connection_be_created_between_gate_and_pin:
        create_rotated_rectangle_between_two_points(start_position_x, start_position_y, x, y, line_width) 
        current_pin = None
        current_gate = None
        if not last_gate: # only set the last gate, if this is the first connection
            last_gate = gate


def finish_line_creation_between_gate_and_gate(event, gate):
    global drag_start_time, start_position_x, start_position_y, current_gate
    if time.time() - drag_start_time < 0.25 and current_gate:
        x = event.x_root
        y = event.y_root  
        connect_gates(gate, start_position_x, start_position_y, x, y)


def connect_gates(gate, start_position_x, start_position_y, x, y):
    global current_gate, last_gate
    current_gate.next_gate = gate
    
    create_rotated_rectangle_between_two_points(start_position_x, start_position_y, x, y, line_width) 
    last_gate = gate
    if current_gate:
        current_gate.next_gate = gate
        last_gate.previous_gate = current_gate
        current_gate = None


def start_drag(event, root):
    global dragging, drag_start_time
    widget = event.widget
    widget.startX = event.x
    widget.startY = event.y
    widget.startPosX = root.winfo_pointerx()
    widget.startPosY = root.winfo_pointery()
    drag_start_time = time.time()
    dragging = True

def stop_drag(event, root, left_panel_button):
    global dragging
    widget = event.widget
    if dragging and hasattr(widget, 'name') and widget.name == "original_button":
        endPosX = root.winfo_pointerx()
        endPosY = root.winfo_pointery()
        if abs(endPosX - widget.startPosX) > 5 or abs(endPosY - widget.startPosY) > 5:
            x = root.winfo_pointerx() - root.winfo_rootx() - widget.startX
            y = root.winfo_pointery() - root.winfo_rooty() - widget.startY
            create_draggable_button(root, left_panel_button, x, y)
            
    dragging = False

def create_draggable_button(root, left_panel_button, x, y): # Used to create gates and pins
    global input_count, entry, last_gate, all_gates, output

    if left_panel_button.category == 'pin':
        button_size = pin_size
    else:
        button_size = gate_size
    image = Image.open('Images/' + left_panel_button.name + '.png').resize((button_size, button_size), Image.ANTIALIAS)
    new_photo = ImageTk.PhotoImage(image)

    ButtonClass = button_classes.get(left_panel_button.name)
    button_text = ''
    if left_panel_button.name == 'Input':
        button_text = 'x' + str(input_count)
        input_count += 1    
    elif left_panel_button.name == 'Output':
        button_text = 'y'

    if left_panel_button.category in ['pin', 'gate'] and ButtonClass is not None:
        new_button = ButtonClass(root, image=new_photo, text=button_text, bd=0, font=('Helvetica 15 bold'), compound=tk.LEFT)
        if left_panel_button.category == 'gate': # Adds the gate to the list of all gates, to save it later
            all_gates.append(new_button)
    
    if left_panel_button.name == 'Output':
        output = new_button # saves the output so that it can be deleted later, if the user calls the clear_circuit() function again

    new_button.label = button_text
    new_button.place(x=x, y=y)
            
    def on_button_press(event):
        start_drag(event, root)
        global drag_start_time
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y
        widget.startPosX = root.winfo_pointerx()
        widget.startPosY = root.winfo_pointery()
        drag_start_time = time.time()

    def on_button_release(event, root, left_panel_button):
        widget = event.widget
        endPosX = root.winfo_pointerx()
        endPosY = root.winfo_pointery()
        if abs(endPosX - widget.startPosX) > 5 or abs(endPosY - widget.startPosY) > 5: # This was a drag operation
            stop_drag(event, root, left_panel_button)
        else:   # This was a click operation
            entry_text.set(button_text)
            connect_buttons(event, new_button)

    new_button.bind("<Button-1>", on_button_press)
    new_button.bind("<ButtonRelease-1>", lambda event: on_button_release(event, root, left_panel_button))
    new_button.bind("<B1-Motion>", lambda event: do_drag(event, root))

    return new_button

def set_label_from_entry(): # It is called when the user presses the enter, after writing something in the entry
        global entry
        current_pin.label = entry.get()
        current_pin.config(text=current_pin.label)


def do_drag(event, root): # It is called when the user drags a gate or a pin
    global dragging
    widget = event.widget
    if dragging and not hasattr(widget, 'name'):
        x = root.winfo_pointerx() - root.winfo_rootx() - widget.startX
        y = root.winfo_pointery() - root.winfo_rooty() - widget.startY
        widget.place(x=x, y=y)

def save_circuit(root): # It is called when the user presses the Save circuit button
    filename = filedialog.asksaveasfilename(defaultextension=".rob", filetypes=[("Text Files", "*.rob"), ("All Files", "*.*")])
    if filename:
        with open(filename, 'w') as file:
            for gate_count in range(len(all_gates)):
                if gate_count != 0: # If it's not the first gate, writes the gate on a new line
                    file.write('\n')
                file.write('Gate: ' + type(all_gates[gate_count]).__name__ + "(x=" + str(all_gates[gate_count].winfo_rootx() - root.winfo_rootx()) + " y=" + str(all_gates[gate_count].winfo_rooty() - root.winfo_rooty()) + ")")
                file.write('\n' + 'Inputs:')
                for input in all_gates[gate_count].inputs:
                    file.write(" Input(x=" + str(input.winfo_rootx() - root.winfo_rootx()) + " y=" + str(input.winfo_rooty() - root.winfo_rooty()) + ")")
                if all_gates[gate_count].output is not None:
                    file.write('\n' + 'Output: ' + 'Output(x=' + str(all_gates[gate_count].output.winfo_rootx() - root.winfo_rootx()) + " y=" + str(all_gates[gate_count].output.winfo_rooty() - root.winfo_rooty()) + ')')


def load_circuit(): # It is called when the user presses the Load circuit button
    global global_root, current_gate, current_pin
    filename = filedialog.askopenfilename(defaultextension=".rob", filetypes=[("Text Files", "*.rob"), ("All Files", "*.*")])
    if filename:
        clear_circuit()
        with open(filename, 'r') as file:
            previous_gate = None
            for line in file:
                line = line.strip()  # strip() is used to remove the newline character at the end
                if(line.startswith('Gate')):
                    match = re.match(r"Gate: (\w+)\(x=(\d+) y=(\d+)\)", line)
                    if match:
                        gate_name = match.group(1)
                        gate_position_x = int(match.group(2))
                        gate_position_y = int(match.group(3))
                        if gate_name.endswith("Gate"): # If the gate name ends with gate, a space is added, because in the buttons list, the names of the gates contain a space before 'gate'
                            gate_name = gate_name[:-4] + ' gate'

                        left_panel_button = get_left_panel_button_by_name(gate_name)
                        newly_created_gate = create_draggable_button(global_root, left_panel_button, gate_position_x, gate_position_y)
                        
                        current_gate = previous_gate
                        if previous_gate is not None:
                            connect_gates(newly_created_gate, previous_gate_position_x + gate_size/2, previous_gate_position_y + gate_size/2, gate_position_x + gate_size/2, gate_position_y + gate_size/2)
                        previous_gate = newly_created_gate
                        previous_gate_position_x = gate_position_x
                        previous_gate_position_y = gate_position_y
                elif(line.startswith('Inputs')):
                    matches = re.findall(r"(\w+)\(x=(\d+)\s+y=(\d+)\)", line)
                    for match in matches:
                        input_name = match[0]
                        input_position_x = int(match[1])
                        input_position_y = int(match[2])
                        left_panel_button = get_left_panel_button_by_name(input_name)
                        newly_created_input = create_draggable_button(global_root, left_panel_button, input_position_x, input_position_y)
                        current_pin = newly_created_input
                        connect_pin_with_gate(previous_gate, input_position_x + pin_size, input_position_y + pin_size, previous_gate_position_x + gate_size/2, previous_gate_position_y + gate_size/2)
                else:
                    left_panel_button = get_left_panel_button_by_name("Output")
                    match = re.search(r"Output\(x=(\d+)\s+y=(\d+)\)", line)
                    output_position_x = int(match.group(1))
                    output_position_y = int(match.group(2))
                    newly_created_output = create_draggable_button(global_root, left_panel_button, output_position_x, output_position_y)
                    current_pin = newly_created_output
                    connect_pin_with_gate(previous_gate, output_position_x + pin_size, output_position_y + pin_size, previous_gate_position_x + gate_size/2, previous_gate_position_y + gate_size/2)

def get_left_panel_button_by_name(name):
    global buttons
    for button in buttons:
        if button.name == name:
            return button

def get_gate_from_line(line): # Used when reading a circuit from a file
    return line.split('(')[0]