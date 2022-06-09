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

menu_classes = []
category_draw_funcs = []
root_menu = bpy.types.NODE_MT_add

class NODE_MT_CUSTOM_MENU_BASECLASS(bpy.types.Menu):
    bl_label = "Menu"
    bl_idname = "NODE_MT_CUSTOM_MENU_BASECLASS"
    bl_space_type = "NODE_EDITOR"
    
    tree_types = ("ShaderNodeTree", 'GeometryNodeTree', 'CompositorNodeTree', 'TextureNodeTree')

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type in cls.tree_types

    def draw(self, context):
        pass

def append_to_parent(parent_menu, draw):
    parent_menu.append(draw)
    if parent_menu == root_menu:
        category_draw_funcs.append(draw)

def name_hash(menu_name):
    hashed_name = str(hash(menu_name))
    if hashed_name.startswith("-"):
        hashed_name = hashed_name.replace("-","1")
    hashed_name = hex(int(hashed_name))
    return hashed_name

def append_menu(menu_name, parent_menu=None, icon="NONE", tree_types=None):
    if parent_menu is None:
        parent_menu = root_menu
        menu_classname = f'NODE_MT_CUSTOM_MENUS_{menu_name.replace(" ", "_")}'
    else:
        parent_hash = str(name_hash(parent_menu.bl_idname))
        menu_classname = f'NODE_MT_CUSTOM_MENUS_{menu_name.replace(" ", "_")}_{parent_hash}'

    if hasattr(bpy.types, menu_classname):
        print(f"WARNING:'{menu_name}' already exists within {parent_menu}. Ignoring duplicate entry.")
        return

    tree_defaults = ("ShaderNodeTree", 'GeometryNodeTree', 'CompositorNodeTree', 'TextureNodeTree')
    if tree_types is None:
        tree_types = tree_defaults
    else:
        for item in tree_types:
            if item not in tree_defaults:
                print(f'WARNING: Invalid poll function - "{item}" is not a valid nodetree type. Ignoring entry for {menu_classname}')
        tree_types = tuple(item for item in tree_types if item in tree_defaults)


    menu = type(menu_classname,(NODE_MT_CUSTOM_MENU_BASECLASS,),
        {
            "bl_idname": menu_classname,
            "bl_label": menu_name,
            "tree_types": tree_types,
        },
    )
    
    bpy.utils.register_class(menu)
    menu_classes.append(menu)

    def draw(self, context):
        self.layout.menu(menu.bl_idname, text=menu.bl_label, icon=icon)
    append_to_parent(parent_menu, draw)
    return menu

def append_separator(parent_menu=root_menu, factor=1):
    def draw(self, context):
        self.layout.separator(factor=factor)
    append_to_parent(parent_menu, draw)

def append_operator(operator_idname, parent_menu=root_menu, label="Operator", icon='NONE'):
    def draw(self, context):
        self.layout.operator(operator_idname, text=label, icon=icon)
    append_to_parent(parent_menu, draw)

def main():
    if not hasattr(bpy.types, "NODE_MT_CUSTOM_MENU_BASECLASS"):
        bpy.utils.register_class(NODE_MT_CUSTOM_MENU_BASECLASS)
    
    menu_classes.clear()
    category_draw_funcs.clear()

    menu = append_menu("Menu")
    for _ in range(50):
        append_separator(parent_menu=menu, factor=0.5)
        append_operator("node.duplicate_move", parent_menu=menu, icon="SORT_DESC")
        append_menu("Submenus 1", parent_menu=menu, tree_types=("ShaderNodeTree", "GeometryNodeTree"))
        append_separator(parent_menu=menu, factor=0.5)
        menu = append_menu("Submenu 2", parent_menu=menu)
    
    #FOR DEBUG ONLY - IF I LEFT THIS IN I'M BEING A DUMDUM
    for cls in menu_classes:
        print(cls)
    for func in category_draw_funcs:
        print(func)

def register():
    try:
        main()
    except Exception:
        print(f'\nWARNING: {traceback.format_exc()}\n')
        unregister()
        menu_classes.clear()
        category_draw_funcs.clear()

def unregister():
    if hasattr(bpy.types, "NODE_MT_CUSTOM_MENU_BASECLASS"):
        bpy.utils.unregister_class(NODE_MT_CUSTOM_MENU_BASECLASS)

    for draw_func in category_draw_funcs:
        root_menu.remove(draw_func)
    for cls in menu_classes:
        bpy.utils.unregister_class(cls)
    



