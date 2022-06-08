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

bl_info = {
    "name": "Custom Node Menu",
    "author": "Quackers",
    "description": "Test Add-on for Generating Custom Node Add Menus",
    "blender": (2, 83, 0),
    "version": (0, 4, 0),
    "location": "Shader Editor > Add > SDF",
    "category": "Node",
}

import bpy
import traceback
from random import random

menu_classes = []
category_draw_funcs = []

class NODE_MT_CUSTOM_MENU_BASECLASS(bpy.types.Menu):
    bl_label = "Menu"
    bl_idname = "NODE_MT_CUSTOM_MENU_BASECLASS"

    tree_types = ("ShaderNodeTree", 'GeometryNodeTree', 'CompositorNodeTree', 'TextureNodeTree')

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type in cls.tree_types

    def draw(self, context):
        pass

def name_hash(menu_name):
    hashed_name = str(hash(menu_name))
    if hashed_name.startswith("-"):
        hashed_name = hashed_name.replace("-","1")
    hashed_name = hex(int(hashed_name))
    return hashed_name

def append_menu(menu_name, parent_menu=None, icon="NONE", tree_types=None):
    global menu_classes
    global category_draw_funcs
    
    if parent_menu is None:
        parent_menu = bpy.types.NODE_MT_add
        menu_classname = f'NODE_MT_CUSTOM_MENUS_{menu_name.replace(" ", "_")}'
    else:
        parent_hash = str(name_hash(parent_menu.bl_idname))
        menu_classname = f'NODE_MT_CUSTOM_MENUS_{menu_name.replace(" ", "_")}_{parent_hash}'
        #menu_classname = f'NODE_MT_CUSTOM_MENUS_{parent_menu.bl_label}_{menu_name.replace(" ", "_")}'

    tree_defaults = ("ShaderNodeTree", 'GeometryNodeTree', 'CompositorNodeTree', 'TextureNodeTree')
    if tree_types is None:
        tree_types = tree_defaults
    else:
        for item in tree_types:
            if item not in tree_defaults:
                print(f'WARNING: Invalid poll function - "{item}" is not a valid nodetree type. Ignoring entry for {menu_classname}')
        tree_types = tuple(item for item in tree_types if item in tree_defaults)
                


    if hasattr(bpy.types, menu_classname):
        print(f"WARNING:'{menu_name}' already exists within {parent_menu}. Ignoring duplicate entry.")
        return

    def draw(self, context):
        pass

    menu = type(menu_classname,(NODE_MT_CUSTOM_MENU_BASECLASS,),
        {
            "bl_idname": menu_classname,
            "bl_space_type": "NODE_EDITOR",
            "bl_label": menu_name,
            "draw": draw,
            "tree_types": tree_types,
        },
    )
    
    bpy.utils.register_class(menu)

    name, label = menu.bl_idname, menu.bl_label
    def draw_menu(self, context):
        self.layout.menu(name, text=label, icon=icon)
    if parent_menu == bpy.types.NODE_MT_add:
        category_draw_funcs.append(draw_menu)

    parent_menu.append(draw_menu)
    menu_classes.append(menu)

    return menu


def append_operator(operator_idname, parent_menu=None, label="Operator", icon='NONE'):
    if parent_menu is None:
        parent_menu = bpy.types.NODE_MT_add
    
    def draw(self, context):
        self.layout.operator(operator_idname, text=label, icon=icon)
    parent_menu.append(draw)

    if parent_menu == bpy.types.NODE_MT_add:
        category_draw_funcs.append(draw)

def main():
    global menu_classes
    global category_draw_funcs
    if not hasattr(bpy.types, "NODE_MT_CUSTOM_MENU_BASECLASS"):
        bpy.utils.register_class(NODE_MT_CUSTOM_MENU_BASECLASS)
    
    menu_classes.clear()
    category_draw_funcs.clear()

    menu = append_menu("Menu")
    for _ in range(50):
        append_menu("Submenusssssssssssss 1", parent_menu=menu, tree_types=("ShaderNodeTree", "GeometryNodeTree"))
        menu = append_menu("Submenu 2", parent_menu=menu)
    
    '''
    menu1 = append_menu("Menu 1", icon="CON_TRANSFORM")
    append_menu("Submenu 1", parent_menu=menu1, icon="SORT_DESC")
    append_menu("Submenu 2", parent_menu=menu1,icon="RADIOBUT_OFF")

    submenu1 = append_menu("Submenu 3", parent_menu=menu1,icon="RADIOBUT_ON")
    append_operator("node.duplicate_move", parent_menu=submenu1, icon="SNAP_VERTEX")
    append_operator("node.duplicate_move", parent_menu=submenu1, icon="SORT_DESC")
    append_operator("nd_align.right", parent_menu=submenu1, icon="SORT_DESC")
    subsubmenu1 = append_menu("Submenu 1", parent_menu=submenu1,icon="RADIOBUT_OFF")
    append_operator("node.duplicate_move", label="Duplicate", parent_menu=subsubmenu1, icon="RADIOBUT_ON")
    append_operator("node.duplicate_move", label="Duplicate", parent_menu=submenu1, icon="RADIOBUT_OFF")

    menu2 = append_menu("Menu 2")
    append_menu("Submenu 1", parent_menu=menu2)
    append_operator("node.duplicate_move", label="Hey Hey", icon="RADIOBUT_OFF")
    append_operator("node.duplicate_move", icon="SORT_DESC")
    submenu1 = append_menu("Submenu 2", parent_menu=menu2)
    append_menu("Submenu 1", parent_menu=submenu1)
    append_menu("Submenu 2", parent_menu=submenu1)
    append_menu("Submenu 3", parent_menu=menu2, icon="RADIOBUT_ON")
    '''
    #FOR DEBUG ONLY - IF I LEFT THIS IN I'M BEING A DUMDUM
    for cls in menu_classes:
        print(cls)
    for func in category_draw_funcs:
        print(func)

def register():
    global menu_classes
    global category_draw_funcs
    
    try:
        main()
    except Exception as error_message:
        print(f'\nWARNING: {traceback.format_exc()}\n')
        unregister()
        menu_classes.clear()
        category_draw_funcs.clear()

def unregister():
    global menu_classes
    if hasattr(bpy.types, "NODE_MT_CUSTOM_MENU_BASECLASS"):
        bpy.utils.unregister_class(NODE_MT_CUSTOM_MENU_BASECLASS)

    for draw_func in category_draw_funcs:
        bpy.types.NODE_MT_add.remove(draw_func)

    for cls in menu_classes:
        bpy.utils.unregister_class(cls)
    



