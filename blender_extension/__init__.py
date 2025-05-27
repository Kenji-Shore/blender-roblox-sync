# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import utils
utils.assign_root_path(__file__)

dependency_tree_stack = []
registered_modules = []
def register_module(modules, module_name):
    if module_name in modules:
        module_dict = modules[module_name]
        if (not module_name in dependency_tree_stack) and (not module_dict in registered_modules):
            dependency_tree_stack.append(module_name)
            if "dependencies" in module_dict:
                for module_name in module_dict["dependencies"]:
                    register_module(modules, module_name)
            dependency_tree_stack.remove(module_name)

            if "classes" in module_dict:
                for cls in module_dict["classes"]:
                    bpy.utils.register_class(cls)
            if "register" in module_dict:
                module_dict["register"](__package__)
            registered_modules.append(module_dict)

def register():
    modules = utils.glob_from_parent(__file__, "**/*.py")
    registered_modules.clear()
    dependency_tree_stack.clear()

    register_module(modules, "utils")
    for module_name in modules.keys():
        register_module(modules, module_name)

def unregister():
    registered_modules.reverse()
    for module_dict in registered_modules:
        if "classes" in module_dict:
            for cls in reversed(module_dict["classes"]):
                bpy.utils.unregister_class(cls)
        if "listeners" in module_dict:
            for listener in module_dict["listeners"]:
                utils.unlisten(listener)
            module_dict["listeners"].clear()
        if "unregister" in module_dict:
            module_dict["unregister"](__package__)