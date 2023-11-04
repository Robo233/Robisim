import math
from tkinter import Button as TkButton

class Gate(TkButton):
    def __init__(self, master=None, image=None,  **kw):
        self.image = image
        self.inputs = []
        self.output = None
        self.next_gate = None
        self.previous_gate = None 
        super().__init__(master, image=self.image, **kw)

    operator = None
    isNegation = False
    can_have_more_than_two_inputs = True # Only False for the XOR and XNOR
    
    def get_first_gate_and_add_values_to_inputs(self, values):
    # Start from the last gate
        gate = self
        while gate.previous_gate is not None:
            gate = gate.previous_gate

    # Reverse the values list to assign values starting from the last gate
        values = values[::-1]
    
    # Iterate over each gate starting from the last gate
        current_gate = gate
        while current_gate is not None:
            if current_gate.inputs:
                for input_ in reversed(current_gate.inputs): # Iterate over each input in reverse order
                    if values:
                        input_.current_value = values.pop()
                    else:
                        break

            current_gate = current_gate.next_gate

        return gate
    
    def analyze_circuit_values(self, values):
        first_gate = self.get_first_gate_and_add_values_to_inputs(values)
        final_value = 0
        current_values = []
    
        while first_gate.__class__.__name__ != 'NoneType':
            current_values = current_values + first_gate.get_current_input_values()
            final_value = first_gate.return_output(current_values)
            current_values.clear()
            current_values.append(final_value)
            first_gate = first_gate.next_gate
            
        return final_value
    

    def get_current_input_values(self):
        values = []
        for input in self.inputs:
            values.append(input.current_value)
        return values
    
    def get_current_input_labels(self):
        labels = []
        for input in self.inputs:
            labels.append(input.label)
        return labels

# Each gate has a separate subclass
# Each negation gate is a subclass of the gate it negates

class ANDGate(Gate):
    def return_output(self, values):
        return and_function(values)
    operator = '*'
    
class NANDGate(ANDGate):
    def return_output(self, values):
        return not and_function(values)
    isNegation = True

class ORGate(Gate):
    def return_output(self, values):
        return or_function(values)
    operator = '+'
        
class NORGate(ORGate):
    def return_output(self, values):
        return not or_function(values)
    isNegation = True
    
class XORGate(Gate):
    def return_output(self, values):
        return xor_function(values)
    operator = '⊕'

class XNORGate(XORGate):
    def return_output(self, values):
        return not xor_function(values)
    isNegation = True

def and_function(values):
    return math.prod(values) # If there are all 1's return true

def or_function(values):
    return int(1 in values) # If there is at least one 1

def xor_function(values):
    if sum(values) == values.__len__(): # If there are only 1's returns false
        return False 
    return int(sum(values) % 2) # If there are an even number of 1's returns true