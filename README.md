© Ihor Mirzov, 2023  
Distributed under GNU General Public License v3.0

<br/><br/>



---

[How to use](#how-to-use) |
[Screenshots](#screenshots) |
[Your help](#your-help) |
[TODO](#todo)

---

<br/><br/>



# CalculiX to Salome converter (inp to unv)

Converts [CalculiX](http://dhondt.de/) .inp file to [Salome](https://www.salome-platform.org/) .unv format.

<br/><br/>



# How to use

Python3 is needed.

Result UNV-file name is the same as INP-file name. So only one argument should be passed to the converter:

    python unv2ccx.py file.inp

<br/><br/>



# Screenshots

1D and 2D elements in CalculiX GraphiX:  
![INP 2D](./Compound_Mesh_2D_inp.png "INP 2D")
Converted 1D and 2D UNV elements in Salome:  
![UNV 2D](./Compound_Mesh_2D_unv.png "UNV 2D")

3D elements in CalculiX GraphiX:  
![INP 3D](./Compound_Mesh_3D_inp.png "INP 3D")
Converted 3D UNV elements in Salome:  
![UNV 3D](./Compound_Mesh_3D_unv.png "UNV 3D")

<br/><br/>



# Your help

Please, you may:

- Star this project.
- Simply use this software and ask questions.
- Share your models and screenshots.
- Report problems by [posting issues](https://github.com/calculix/inp2unv/issues).
- Or even [become a sponsor to me](https://github.com/sponsors/imirzov).

<br/><br/>



# TODO

- Support keyword *HEADING
- Support keyword *SURFACE
