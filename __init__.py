# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
    "name": "Quadriflow remesher",
    "author": "David Gayerie",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Properties > Quadriflow",
    "description": "Automatic remesher based in quadriflow",
    "category": "Mesh"}

import bpy
import tempfile
import os
import sys
import subprocess
import importlib
from bpy.props import (
        BoolProperty,
        IntProperty,
        )


class QuadriflowRemesher(bpy.types.Operator):
  """Remesh using Quadriflow"""
  bl_idname = "mesh.quadriflow"
  bl_label = "Quadriflow"
  bl_options = {'PRESET', 'UNDO'}

  sharp = BoolProperty(
            name="Sharp",
            description="Try to follow sharp edges",
            default=False,
            )

  adaptive = BoolProperty(
            name="Adaptive",
            description="Adaptive mode",
            default=False,
            )

  minimum_cost_flow = BoolProperty(
            name="Min cost flow",
            description="Minimum cost flow",
            default=False,
            )

  faces = IntProperty(
            name="Faces",
            description="Number of faces",
            default=500,
            soft_max=2000,
            )

  cuda = BoolProperty(
            name="Use CUDA",
            description="Use CUDA",
            default=True,
            )

  def find_quadriflow(self):
    if sys.platform == 'linux':
      quadriflow_exe = "quadriflow"
    elif sys.platform == 'darwin':
      quadriflow_exe = "quadriflow_osx"
    else:
      quadriflow_exe = "quadriflow.exe"

    if self.cuda:
      quadriflow_exe = "cuda_%s" % quadriflow_exe

    base_path = importlib.find_loader(__name__).path
    base_path = os.path.dirname(base_path)
    return os.path.join(base_path, "bin", quadriflow_exe)

  def execute(self, context):

    # export mesh as obj
    fh, input_filepath = tempfile.mkstemp(suffix=".obj", prefix="blender_quadriflow")
    output_filepath = "%s.output" % input_filepath
    os.close(fh)

    try:
      print("Quadriflow Remesher > Exporting obj file...")
      bpy.ops.export_scene.obj(filepath=input_filepath, use_selection=True, use_materials=False)

      arguments = [self.find_quadriflow(), "-i", input_filepath, "-o", output_filepath, "-f", str(self.faces)]

      if self.sharp:
        arguments.insert(-1, "-sharp")

      if self.adaptive:
        arguments.insert(-1, "-adaptive")

      if self.minimum_cost_flow:
        arguments.insert(-1, "-mcf")

      print("Quadriflow Remesher > Launching: %s" % arguments)
      subprocess.run(arguments)

      print("Quadriflow Remesher > Importing remeshed obj file...")
      bpy.ops.import_scene.obj(filepath=output_filepath)

    finally:
      if os.path.isfile(input_filepath):
        os.remove(input_filepath)
      if os.path.isfile(output_filepath):
        os.remove(output_filepath)

    return {'FINISHED'}


def register():
  bpy.utils.register_class(QuadriflowRemesher)

def unregister():
  bpy.utils.unregister_class(QuadriflowRemesher)

if __name__ == "__main__":
    register()
