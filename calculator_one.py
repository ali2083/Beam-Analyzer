##Statically determinate beam analysis

import numpy as np
import sympy as sp

def perform_analysis_determinate(length, elasticity, inertia, supports, point_loads, distributed_loads, moments):
    """ this function will perform the analysis of the beam
    ### and return the shear force and bending moment diagrams
    ### as well as the deflection of the beam.
    ### variables: length = length of the beam (m)
    ###            elasticity = elasticity of the beam (Pa)
    ###            inertia = inertia of the beam (m^4)
    ###            supports = list of supports (type, position)
    ###            point_loads = list of point loads (force, position)
    ###            distributed_loads = list of distributed loads (function, start, end)
    ###            moments = list of moments (moment, position)"""


    #Beam defintion
    beam = np.zeros((0,4)) ## beam = [start position, end position, force, moment]

    for point_load in point_loads:
        beam = np.vstack((beam, [point_load[1], point_load[1], point_load[0], 0]))
    
    for distributed_load in distributed_loads:
        x = sp.Symbol('x')
        load_function = sp.sympify(distributed_load[0])
        beam = np.vstack((beam, [distributed_load[1], distributed_load[2], load_function, 0]))

    for moment in moments:
        beam = np.vstack((beam, [moment[1], moment[1], 0, moment[0]]))
                         
    for i in range(len(supports)):
        support = supports[i]
        if support[0] == 1:
            force_symbol = sp.Symbol(f'R_{i}')
            beam = np.vstack((beam, [support[1], support[1], force_symbol, 0]))
        elif support[0] == 2:
            force_symbol = sp.Symbol(f'R_{i}')
            beam = np.vstack((beam, [support[1], support[1], force_symbol, 0]))
        elif support[0] == 3:
            force_symbol = sp.Symbol(f'R_{i}')
            moment_symbol = sp.Symbol(f'M_{i}')
            beam = np.vstack((beam, [support[1], support[1], force_symbol, moment_symbol]))
        else:
            raise ValueError("Invalid support type")
    
    support_reactions = calculation_support_forces(beam.copy())

    for i in range(len(supports)):
        support = supports[i]
        if support[0] == 1 or support[0] == 2:
            force_symbol = sp.Symbol(f'R_{i}')
            beam[np.where(beam[:, 2] == force_symbol), 2] = support_reactions[force_symbol]
        elif support[0] == 3:
            force_symbol = sp.Symbol(f'R_{i}')
            beam[np.where(beam[:, 2] == force_symbol), 2] = support_reactions[force_symbol]
            beam[np.where(beam[:, 3] == moment_symbol), 3] = support_reactions[moment_symbol]
    
    return beam

    
def equal_force_distributed_loads(distributed_load) -> (tuple): ##(function, start position, end position)
    load_function = distributed_load[0]
    x = sp.Symbol('x')
    equal_force = sp.integrate(load_function, (x, distributed_load[1], distributed_load[2]))

    position = sp.integrate(x * load_function, (x, distributed_load[1], distributed_load[2])) / equal_force

    return (equal_force, position)


def calculation_support_forces(ideal_beam):
    #===================== Idealization of the beam =====================#
    for row in ideal_beam:
        #point load force
        if isinstance(row[2], (float, int)):
            force = row[2]
        #distributed load force
        elif (isinstance(row[2], sp.core.symbol.Symbol) and row[2].free_symbols == {sp.Symbol('x')}) or isinstance(row[2], sp.core.Number) or isinstance(row[2], sp.core.Add) or isinstance(row[2], sp.core.Mul):
            load = equal_force_distributed_loads((row[2], row[0], row[1]))
            force = float(load[0])
            row[0] = float(load[1])
            row[1] = float(load[1])
        #support force
        elif isinstance(row[2], sp.core.Symbol):
            force = row[2]   
        #error handling
        else:
            raise ValueError("Invalid force type")
        row[2] = force

    #===================== Calculation of support forces =====================#
    equations = []
    sigma_F = 0
    syms = []

    for row in ideal_beam:
        #summing forces
        sigma_F += row[2]
        #supports moment
        #checking the element is support
        if isinstance(row[2], sp.core.symbol.Symbol):
            #========= getting syms out ===========#
            syms.append(row[2])
            if isinstance(row[3], sp.core.symbol.Symbol):
                syms.append(row[3])
            #=================================#
            moment_equation = sp.S(0)
            for i in range(len(ideal_beam) - 1):
                row2 = ideal_beam[i]
                distance = row2[0] - row[0]
                ## counter clockwise moment is positive
                if distance != 0:
                    if row2[0] < row[0]:
                        moment_equation -= row2[2] * distance
                    elif row2[0] > row[0]:
                        moment_equation += row2[2] * distance
                    moment_equation += row2[3]
            moment_equation += row[3]
            equations.append(moment_equation)
    
    #===================== Solving the equations =====================#
    equations.append(sigma_F)
    solution = sp.linsolve(equations, syms)
    total_solution = {}
    for i in range(len(syms)):
        total_solution[syms[i]] = solution.args[0][i]
    return total_solution


