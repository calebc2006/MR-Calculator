import pandas as pd
import sys

# Fetches ptable data 
def get_ptable(isIB :bool):
    columns_needed = ['Symbol', 'AtomicMass']
    df = pd.read_csv('data.csv')[columns_needed]
    df['AtomicMass'] = df['AtomicMass'].astype(float)

    ptable = {}
    for index, row in df.iterrows():
        ptable[row['Symbol']] = row['AtomicMass']
        if isIB:
            ptable[row['Symbol']] = round(ptable[row['Symbol']], 2)
        else:
            ptable[row['Symbol']] = round(ptable[row['Symbol']], 4)

    return ptable

# Returns type of character
def get_type(c :str):
    assert len(c) == 1
    
    if not c.isalnum():
        return 'BRACKET'
    if not c.isalpha():
        return 'NUMBER'
    if c.islower():
        return 'LOWER'
    return 'UPPER'

# Parses input string into array of items to process, ends with '.'
def parse_str(formula_str :str, data :dict):
    formula = []
    buffer = '(' # Stores relevant previous chars
    prev_type = '' # Stores type of previous char
    
    formula_str = formula_str.replace('[', '(').replace(']', ')')
    
    for cur in formula_str:
        cur_type = get_type(cur)
        
        if cur_type == 'UPPER':
            # Start of new element, push and reset buffer 
            formula.append(buffer)
            buffer = cur
            prev_type = 'UPPER'
            continue
        
        if cur_type == 'LOWER':
            buffer += cur
            prev_type = 'LOWER'
            continue
        
        if cur_type == 'NUMBER':
            if prev_type == 'NUMBER':
                buffer += cur
                continue
            
            # Start of new element, push and reset buffer 
            formula.append(buffer)
            buffer = cur
            prev_type = 'NUMBER'
            continue
        
        if cur_type == 'BRACKET':
            # Start of new element, push and reset buffer 
            formula.append(buffer)
            buffer = cur
            prev_type = 'BRACKET'
            continue
    
    formula.append(buffer)
    formula.append(')')
    
    for i in range(len(formula)):
        if formula[i].isnumeric():
            formula[i] = int(formula[i])
            continue
        if formula[i] not in '()':
            assert formula[i] in data.keys()
    
    formula.append('.')
    return formula

# Recursively calculates total mass, returns (mass, next_index)
def get_mass(formula :list, data, start_index):
    mass = 0
    idx = start_index
    
    while True:
        cur = formula[idx]
        if cur == '.': # At the end of the formula
            return (mass, idx)
        
        if cur == ')': # We're done with this component
            coeff = 1
            if type(formula[idx+1]) == int: # Next is the relevant coefficient
                coeff = formula[idx+1]
                idx += 1
            
            return (mass*coeff, idx+1)
        
        if cur in data.keys(): # Its an element
            coeff = 1
            if type(formula[idx+1]) == int: # Next is the relevant coefficient
                coeff = formula[idx+1]
                idx += 1
                
            mass += data[cur] * coeff
            idx += 1
        
        if cur == '(': # Start new recursion
            (m, end) = get_mass(formula, data, idx+1)
            mass += m
            idx = end

def main(ib :bool, data, uinput=None):
    mass_data = data
    
    if uinput is not None:
        formula_str = uinput
    else:
        formula_str = str(input("Formula: ")).strip()
        
    try:
        formula = parse_str(formula_str, mass_data)
    except:
        print("Bad Formula")
        return
    
    try:
        mass = get_mass(formula, mass_data, 0)
        print(round(mass[0], 3) if ib else round(mass[0], 2))
    except:
        print("Error: Bad Formula?")
        return
   

help_msg = """
I am a friendly mr calculator! 

Enter as many formulas as you like in the command (separated by space) and I will give you their molecular masses! 
If none are provided I will just stick around forever waiting for formulas to crunch :D (quit with CTRL+C)

Arguments:
    --ib : uses values from the IB data booklet (2 dp)
"""
        
if __name__ == "__main__":
    ib = False
    args = sys.argv
    args = args[1:]
    
    # Handles Args
    if '-h' in sys.argv or '--help' in args:
        print(help_msg)
        quit()
    
    if '--ib' in args:
        ib = True
    
    # Handles inline calls
    isInline = False
    data = get_ptable(ib)
    
    for i in args:
        if i not in ['--ib', '-h', '--help', 'mr.py']:
            main(ib, data, uinput=i.strip())
            isInline = True
    
    if not isInline:
        while True:
            main(ib, data, uinput=None)