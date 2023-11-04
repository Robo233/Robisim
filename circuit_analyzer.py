import itertools
import tkinter as tk

from Gates import XORGate

font_size = 12
paddingX = 10
paddingY = 10
equation_font_size = 25
equation_paddingX = 100
equation_column = 0
font_color = "black"
font_background = "steelblue"


"""
Handles the creation of the analysis window, creates the value table and the equation
"""

def on_configure(event): # It is called when the user scrolls the scrollbar, it updates the canvas size
    canvas.configure(scrollregion=canvas.bbox('all'))

def analyze_circuit(last_gate, all_inputs): # It is called when the user clicks on the "Analyze circuit" button, it creates the analysis window and calculates the truth table
    global equation_column
    equation_column = all_inputs.__len__() + 1 # It is saved, to place the equation to the right place
    
    root = tk.Tk()
    root.title("Analysis")
    root.geometry("1000x500")

    global canvas, scrollable_frame
    canvas = tk.Canvas(root)
    canvas.pack(side='left', fill='both', expand=True)

    # makes the canvas that was created above scrollable
    scrollbar = tk.Scrollbar(root, command=canvas.yview)
    scrollbar.pack(side='left', fill='y')
    canvas.configure(yscrollcommand = scrollbar.set)
    canvas.bind('<Configure>', on_configure)
    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0,0), window=scrollable_frame, anchor='nw')

    create_equation(last_gate, scrollable_frame)

    binary_variations = [list(variation) for variation in list(itertools.product([0, 1], repeat=all_inputs.__len__()))] # an array of numbers, that contains the binary values, like 001

    for input_count, input_ in enumerate(all_inputs):
        input_label = tk.Label(scrollable_frame, text=input_.label)
        input_label.grid(row=0, column=input_count, padx=paddingX, pady = paddingY)
        input_label.config(font=("Arial", font_size), fg=font_color, bg=font_background)

    output_label = tk.Label(scrollable_frame, text=last_gate.output.label)
    output_label.grid(row=0, column=input_count+1, padx = paddingX, pady=paddingY)
    output_label.config(font=("Arial", font_size), fg=font_color, bg=font_background)

    for binary_variation_count, binary_variation in enumerate(binary_variations):
        for binary_variation_value_count, binary_variation_value in enumerate(binary_variation):
            binary_value__input_label = tk.Label(scrollable_frame, text=binary_variation_value)  
            binary_value__input_label.grid(row=1+binary_variation_count, column=binary_variation_value_count, pady = paddingY)
            binary_value__input_label.config(font=("Arial", font_size), fg=font_color)  

        binary_value__output_label = tk.Label(scrollable_frame, text=last_gate.analyze_circuit_values(binary_variation)) 
        binary_value__output_label.grid(row=1+binary_variation_count, column=binary_variation_value_count+1, pady = paddingY)
        binary_value__output_label.config(font=("Arial", font_size), fg=font_color) 

    root.mainloop()

"""
Creation of the equation
"""

def create_equation(last_gate, scrollable_frame):
    first_gate = get_first_gate(last_gate)
    equation = ''
    can_equation_be_created = True
    while first_gate.__class__.__name__ != 'NoneType':
        input_labels = [equation]
        input_labels.extend(first_gate.get_current_input_labels())
        if (  (input_labels.__len__() > 2 and equation!='') or (input_labels.__len__()>3 and equation=='')  ) and isinstance(first_gate, XORGate): # The equation can only be created if there is no XOR or XNOR gate that contains more than 2 inputs
            can_equation_be_created = False
            break

        equation = ''
        equation += small_equation(input_labels, first_gate.operator, input_labels[0]!='' ) # Only add operator before the first value if an equation was already written

        equation = equation + "'" if first_gate.isNegation else equation

        first_gate = first_gate.next_gate

    if can_equation_be_created:
        if equation[-1] == ')':
            equation = equation[1:-1] # Remove the first and last parantheses if the last character is not a negation
        equation_label = tk.Label(scrollable_frame, text=equation)
    else:
        equation_label = tk.Label(scrollable_frame, text="Equation cannot be created")

    equation_label.grid(row=0, column=equation_column, padx=equation_paddingX, pady=paddingY)
    equation_label.config(font=("Arial", equation_font_size), fg=font_color)


def small_equation(input_labels, operator, should_operator_before_the_first_velue_be_added): # creates one parantheses of the big equation
    equation = '('
    for input_label in input_labels:
        equation += input_label
        if (input_labels.index(input_label)==0 and should_operator_before_the_first_velue_be_added) or (input_labels.index(input_label)>0 and input_labels.index(input_label)<input_labels.__len__()-1 ):
            equation += operator
    return equation + ')'


def get_first_gate(gate):
    while gate.previous_gate is not None:
        gate = gate.previous_gate
    return gate