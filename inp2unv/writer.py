#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""© Ihor Mirzov, 2023
Distributed under GNU General Public License v3.0

Writes FEM nodes, elements and groups
(node and element sets) into INP file.

UNV format documentation:
https://docs.plm.automation.siemens.com/tdoc/nx/10/nx_help/#uid:index_advanced:xid602249:id625716:id625821
"""

import logging
import re

PADDING = ' '*3 # four spaces
HEADER = """
    -1
   164
         1  SI: Meter (newton)         2
    1.0000000000000000E+0    1.0000000000000000E+0    1.0000000000000000E+0
    2.7314999999999998E+2
    -1
    -1
  2420
         1
SMESH_Mesh
         1         0         0
Global Cartesian Coordinate System
    1.0000000000000000E+0    0.0000000000000000E+0    0.0000000000000000E+0
    0.0000000000000000E+0    1.0000000000000000E+0    0.0000000000000000E+0
    0.0000000000000000E+0    0.0000000000000000E+0    1.0000000000000000E+0
    0.0000000000000000E+0    0.0000000000000000E+0    0.0000000000000000E+0
    -1
    -1
"""


# Main function
def write(FEM, file_name):
    with open(file_name, 'w') as f:
        for line in HEADER[1:]:
            f.write(line)

        # Nodes
        f.write('  2411\n')
        for node in FEM.nodes:
            line1 = '{:>10d}'.format(node.num) + '{:>10d}'.format(1) * 2 + '{:>10d}'.format(11)
            f.write(line1 + '\n')
            line2 = '{:>25.16E}'*3 + '\n'
            f.write(line2.format(*node.coords))
        f.write('    -1\n')
        f.write('    -1\n')

        # Elements
        f.write('  2412\n')
        for e in FEM.elements:
            # Select the appropriate map between the nodes
            themap = element_connectivity(e.type)
            unv_element_type = convert_element(e.type) # can return None

            line1 = '{:>10d}' * 6 + '\n'
            f.write(line1.format(e.num, unv_element_type, 2, 1, 7, len(e.nodes)))

            # 1D elements have an additionnal line in definition
            if unv_element_type < 33:
                line = '{:>10d}' * 3
                f.write(line.format(0, 1, 1) + '\n')

            for i,n in enumerate(themap):
                f.write('{:>10d}'.format(e.nodes[n - 1].num))
                i += 1
                if i == len(e.nodes):
                    break
                if i % 8 == 0:
                    f.write('\n')
            f.write('\n')
        f.write('    -1\n')
        f.write('    -1\n')

        # Write sets
        f.write('  2467\n')
        for i, group in enumerate(FEM.nsets + FEM.esets):
            line = '{:>10d}' * 8
            f.write(line.format(i+1, 0, 0, 0, 0, 0, 0, len(group.items)) + '\n')
            f.write(group.name + '\n')
            for j, item in enumerate(group.items):
                line = '{:>10d}' * 4
                f.write(line.format(group.type, item.num, 0, 0))
                new_line = False
                if j % 2:
                    new_line = True
                    f.write('\n')
            if not new_line:
                f.write('\n')
        f.write('    -1\n')


# Convert UNV element type to CalculiX
def convert_element(inp_element_type):

    # unv_element_type : inp_element_type
    dic = {
        11:'B31',       # Rod
        21:'B31',       # Linear beam
        22:'B32',       # Tapered beam
        23:'B32',       # Curved beam
        24:'B32',       # Parabolic beam
        31:'B31',       # Straight pipe
        32:'B32',       # Curved pipe
        41:'CPS3',      # Plane Stress Linear Triangle
        42:'CPS6',      # Plane Stress Parabolic Triangle
        43: None,       # Plane Stress Cubic Triangle
        44:'CPS4',      # Plane Stress Linear Quadrilateral
        45:'CPS8',      # Plane Stress Parabolic Quadrilateral
        46: None,       # Plane Strain Cubic Quadrilateral
        51:'CPE3',      # Plane Strain Linear Triangle
        52:'CPE6',      # Plane Strain Parabolic Triangle
        53: None,       # Plane Strain Cubic Triangle
        54:'CPE4',      # Plane Strain Linear Quadrilateral
        55:'CPE8',      # Plane Strain Parabolic Quadrilateral
        56: None,       # Plane Strain Cubic Quadrilateral
        61:'M3D3',      # Plate Linear Triangle
        62:'M3D6',      # Plate Parabolic Triangle
        63: None,       # Plate Cubic Triangle
        64:'M3D4',      # Plate Linear Quadrilateral
        65:'M3D8',      # Plate Parabolic Quadrilateral
        66: None,       # Plate Cubic Quadrilateral
        71:'M3D4',      # Membrane Linear Quadrilateral
        72:'M3D6',      # Membrane Parabolic Triangle
        73: None,       # Membrane Cubic Triangle
        74:'M3D3',      # Membrane Linear Triangle
        75:'M3D8',      # Membrane Parabolic Quadrilateral
        76: None,       # Membrane Cubic Quadrilateral
        81:'CAX3',      # Axisymetric Solid Linear Triangle
        82:'CAX6',      # Axisymetric Solid Parabolic Triangle
        84:'CAX4',      # Axisymetric Solid Linear Quadrilateral
        85:'CAX8',      # Axisymetric Solid Parabolic Quadrilateral
        91:'S3',        # Thin Shell Linear Triangle
        92:'S6',        # Thin Shell Parabolic Triangle
        93: None,       # Thin Shell Cubic Triangle
        94:'S4',        # Thin Shell Linear Quadrilateral
        95:'S8',        # Thin Shell Parabolic Quadrilateral
        96: None,       # Thin Shell Cubic Quadrilateral
        # 101:'C3D6',     # Thick Shell Linear Wedge
        # 102:'C3D15',    # Thick Shell Parabolic Wedge
        # 103: None,      # Thick Shell Cubic Wedge
        # 104:'C3D8',     # Thick Shell Linear Brick
        # 105:'C3D20',    # Thick Shell Parabolic Brick
        106: None,      # Thick Shell Cubic Brick
        111:'C3D4',     # Solid Linear Tetrahedron
        112:'C3D6',     # Solid Linear Wedge
        113:'C3D15',    # Solid Parabolic Wedge
        114: None,      # Solid Cubic Wedge
        115:'C3D8',     # Solid Linear Brick
        116:'C3D20',    # Solid Parabolic Brick
        117: None,      # Solid Cubic Brick
        118:'C3D10',    # Solid Parabolic Tetrahedron
        121: None,      # Rigid Bar
        122: None,      # Rigid Element
        136:'SPRINGA',  # Node To Node Translational Spring
        137:'SPRINGA',  # Node To Node Rotational Spring
        138:'SPRINGA',  # Node To Ground Translational Spring
        139:'SPRINGA',  # Node To Ground Rotational Spring
        141:'DASHPOTA', # Node To Node Damper
        142:'DASHPOTA', # Node To Gound Damper
        151:'GAPUNI',   # Node To Node Gap
        152:'GAPUNI',   # Node To Ground Gap
        161:'MASS',     # Lumped Mass
        171: None,      # Axisymetric Linear Shell
        172: None,      # Axisymetric Parabolic Shell
        181: None,      # Constraint
        191: None,      # Plastic Cold Runner
        192: None,      # Plastic Hot Runner
        193: None,      # Plastic Water Line
        194: None,      # Plastic Fountain
        195: None,      # Plastic Baffle
        196: None,      # Plastic Rod Heater
        201: None,      # Linear node-to-node interface
        202: None,      # Linear edge-to-edge interface
        203: None,      # Parabolic edge-to-edge interface
        204: None,      # Linear face-to-face interface
        208: None,      # Parabolic face-to-face interface
        212: None,      # Linear axisymmetric interface
        213: None,      # Parabolic axisymmetric interface
        221: None,      # Linear rigid surface
        222: None,      # Parabolic rigin surface
        231: None,      # Axisymetric linear rigid surface
        232: None,      # Axisymentric parabolic rigid surface
        }
    if inp_element_type in dic.values():
        for unv_element_type, v in dic.items():
            if inp_element_type == v:
                return unv_element_type


# Map of the nodes between Universal and Calculix elements
def element_connectivity(inp_element_type):

    # Some elements have the same connectivity
    etype = re.sub('CPS|CPE|M3D|CAX', 'S', inp_element_type)
    # if inp_element_type != etype:
    #     logging.debug('Using {} connectivity for {}.'.format(etype, inp_element_type))
    # else:
    #     print(etype)

    dic = {
        # index   1  2  3  4  5  6
        # INP     1, 2, 3, 4, 5, 6 - from this we have...
        # UNV     1, 4, 2, 5, 3, 6 - ...to receive this
        'S6':    [1, 4, 2, 5, 3, 6],

        # index   1  2  3  4  5  6  7  8
        # INP     1, 2, 3, 4, 5, 6, 7, 8 - from this we have...
        # UNV     1, 5, 2, 6, 3, 7, 4, 8 - ...to receive this
        'S8':    [1, 5, 2, 6, 3, 7, 4, 8],

        # index   1  2  3  4  5  6  7   8   9 10
        # INP     1, 3, 2, 4, 7, 6, 5,  8, 10, 9 - from this we have...
        # UNV     1, 7, 3, 6, 2, 5, 8, 10,  9, 4 - ...to receive this
        'C3D10': [1, 5, 2, 6, 3, 7, 8,  9, 10, 4],

        # index   1  2  3  4  5  6   7   8   9  10  11  12  13  14  15
        # INP     1, 3, 2, 4, 6, 5,  9,  8,  7, 12, 11, 10, 13, 15, 14 - from this we have...
        # UNV     1, 9, 3, 8, 2, 7, 13, 15, 14,  4, 12,  6, 11,  5, 10 - ...to receive this
        'C3D15': [1, 7, 2, 8, 3, 9, 13, 14, 15,  4, 10,  5, 11,  6, 12],

        # index   1  2   3   4  5   6  7   8   9  10  11  12  13  14  15  16  17  18  19  20
        # INP     1, 4,  3,  2, 5,  8, 7,  6, 12, 11, 10,  9, 16, 15, 14, 13, 17, 20, 19, 18 - from this we have...
        # UNV     1, 12, 4, 11, 3, 10, 2,  9, 17, 20, 19, 18,  5, 16,  8, 15,  7, 14,  6, 13 - ...to receive this
        'C3D20': [1, 9,  2, 10, 3, 11, 4, 12, 17, 18, 19, 20,  5, 13,  6, 14,  7, 15,  8, 16],
        }

    if etype in dic:
        return dic[etype]

    # If no map is available translate as it is
    else:
        # print('WARNING: no element map available.')
        return list(range(1,21))
