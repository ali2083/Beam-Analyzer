##Statically indeterminate beam analysis
import numpy as np

def perform_analysis_determinate(length, elasticity, inertia, num_elements, supports, point_loads, distributed_loads, moments):
    """ this function will perform the analysis of the beam
    and return the shear force and bending moment diagrams
    as well as the deflection of the beam.
    variables:  length = length of the beam (m)
                elasticity = elasticity of the beam (Pa)
                inertia = inertia of the beam (m^4)
                supports = list of supports (type, position)
                point_loads = list of point loads (force, position)
                distributed_loads = list of distributed loads (function, start, end)
                moments = list of moments (moment, position)

    Returns:
        Array of shear forces along the beam.
    """

    node_coords = np.linspace(0, length, num_elements + 1)
    element_length = length / num_elements

    # Stiffness matrix for a single beam element
    k_element = (elasticity * inertia / element_length**3) * np.array([
        [12, 6 * element_length, -12, 6 * element_length],
        [6 * element_length, 4 * element_length**2, -6 * element_length, 2 * element_length**2],
        [-12, -6 * element_length, 12, -6 * element_length],
        [6 * element_length, 2 * element_length**2, -6 * element_length, 4 * element_length**2]
    ])

    # Global stiffness matrix assembly
    global_k = np.zeros((2 * (num_elements + 1), 2 * (num_elements + 1)))
    for i in range(num_elements):
        global_k[2 * i:2 * i + 4, 2 * i:2 * i + 4] += k_element

    # Force vector assembly
    global_f = np.zeros(2 * (num_elements + 1))

    # Apply point loads
    for force, position  in point_loads:
        node_index = np.argmin(np.abs(node_coords - position))
        global_f[2 * node_index] -= force

    # Apply distributed loads
    for load_expr, start, end in distributed_loads:
        start_index = np.argmin(np.abs(node_coords - start))
        end_index = np.argmin(np.abs(node_coords - end))
        for i in range(start_index, end_index):
            load_mid = eval(load_expr, {'x': i, 'np': np})
            global_f[2 * i] -= load_mid * element_length
            global_f[2 * (i + 1)] -= load_mid * element_length
            global_f[2 * i + 1] -= load_mid * element_length**2 / 12
            global_f[2 * (i + 1) + 1] += load_mid * element_length**2 / 12

    # Apply moments
    for moment, position in moments:
        node_index = np.argmin(np.abs(node_coords - position))
        global_f[2 * node_index + 1] -= moment

    # Apply support conditions
    support_indices = []
    for support_type, position  in supports:
        node_index = np.argmin(np.abs(node_coords - position))
        if support_type == 3:
            support_indices.extend([2 * node_index, 2 * node_index + 1])
        elif support_type == 1:
            support_indices.append(2 * node_index)
        elif support_type == 2:
            support_indices.append(2 * node_index)

    # Apply support conditions to stiffness matrix and force vector
    for index in support_indices:
        global_k[index, :] = 0
        global_k[:, index] = 0
        global_k[index, index] = 1
        global_f[index] = 0

    # Solve for displacements
    u = np.linalg.solve(global_k, global_f)

    # Calculate element forces
    element_forces = np.zeros(2 * (num_elements + 1))
    for i in range(num_elements):
        element_forces[2 * i:2 * i + 4] = k_element @ u[2 * i:2 * i + 4]

    # Calculate shear forces
    shear_forces = np.zeros(num_elements + 1)
    for i in range(num_elements + 1):
        shear_forces[i] = element_forces[2 * i]

    # Calculate bending moments
    bending_moments = np.zeros(num_elements + 1)
    for i in range(num_elements + 1):
        bending_moments[i] = element_forces[2 * i + 1]

    # Calculate deflections
    deflections = u[::2]

    # Calculate support reactions
    support_reactions = []
    for i in range(len(supports)):
        support_type = supports[i][0]
        position = supports[i][1]
        node_index = np.argmin(np.abs(node_coords - position))
        if support_type == 3:
            support_reactions.append({'type': 3, 'position': position, 'force': element_forces[2 * node_index], 'moment': element_forces[2 * node_index + 1]})
        elif support_type == 2:
            support_reactions.append({'type': 2, 'position': position, 'force': element_forces[2 * node_index]})
        elif support_type == 1:
            support_reactions.append({'type': 1, 'position': position, 'force': element_forces[2 * node_index]})

    plots_data = {
        'node_coords': node_coords,
        'shear_forces': shear_forces,
        'bending_moments': bending_moments,
        'deflections': deflections,
        'support_reactions': support_reactions
    }
    return plots_data
    

    