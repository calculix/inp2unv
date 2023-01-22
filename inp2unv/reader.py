#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""© Ihor Mirzov, 2023
Distributed under GNU General Public License v3.0

"""

import mesh
import FEM
FLAG = '    -1'


# INP file reader
class INP:

    def __init__(self, filename):
        self.filename = filename
        self.fem = FEM.FEM()
    
    def read(self):
        self.mesh = mesh.Mesh(ifile=self.filename)
    
    def convert_to_fem(self):
        for mesh_node in self.mesh.nodes.values():
            fem_node = FEM.Node(mesh_node.num, mesh_node.coords)
            self.fem.nodes.append(fem_node)
        for mesh_element in self.mesh.elements.values():
            fem_element = FEM.Element(mesh_element.num, mesh_element.type, mesh_element.nodes)
            self.fem.elements.append(fem_element)
        for mesh_nset in self.mesh.nsets.values():
            items = mesh_nset.items
            fem_nset = FEM.Group(mesh_nset.name, 7, items)
            self.fem.nsets.append(fem_nset)
        for mesh_elset in self.mesh.elsets.values():
            items = mesh_elset.items
            fem_elset = FEM.Group(mesh_elset.name, 8, items)
            self.fem.esets.append(fem_elset)
        # self.mesh.surfaces
        return self.fem
