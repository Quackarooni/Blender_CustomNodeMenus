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

node_categories = []
category_draw_funcs = []
classname_dict = {}

def append_menu(menu_name, parent_menu=None, icon="NONE"):
    global node_categories
    global category_draw_funcs
    global classname_dict
    
    if parent_menu is None:
        parent_menu = bpy.types.NODE_MT_add
        menu_classname = f'NODE_MT_CUSTOM_MENUS_{menu_name.replace(" ", "_")}'
    else:
        menu_classname = f'{parent_menu.bl_idname}_{menu_name.replace(" ", "_")}'


    if hasattr(bpy.types, menu_classname):
        print(f"WARNING:'{menu_name}' already exists within {parent_menu}. Ignoring duplicate entry.")
        return

    def draw(self, context):
        pass

    menu = type(menu_classname,(bpy.types.Menu,),
        {
            "bl_idname": menu_classname,
            "bl_space_type": "NODE_EDITOR",
            "bl_label": menu_name,
            "draw": draw,
        },
    )
    
    bpy.utils.register_class(menu)

    name, label = menu.bl_idname, menu.bl_label
    def draw_menu(self, context):
        self.layout.menu(name, text=label, icon=icon)
    if parent_menu == bpy.types.NODE_MT_add:
        category_draw_funcs.append(draw_menu)
    
    parent_menu.append(draw_menu)
    node_categories.append(menu)

    return menu

def build_tree(tree, parent=None):
    for item in tree:
        if type(item) == list:
            menu_parent = append_menu(item.pop(0), parent)
            for subitem in item:
                if type(subitem) == list:
                    print("sublist", subitem, menu_parent)
                    build_tree(subitem, menu_parent)
                else:
                    print("subitem", subitem, menu_parent)
                    append_menu(subitem, menu_parent)
        else:
            print("item", item, parent)
            append_menu(item, parent)

def append_operator(operator_idname, parent_menu=None, label="Operator", icon='NONE'):
    if parent_menu is None:
        parent_menu = bpy.types.NODE_MT_add
    
    def draw(self, context):
        self.layout.operator(operator_idname, text=label, icon=icon)
    parent_menu.append(draw)

    if parent_menu == bpy.types.NODE_MT_add:
        category_draw_funcs.append(draw)



def register():
    global node_categories
    global category_draw_funcs
    global classname_dict
    
    node_categories.clear()
    category_draw_funcs.clear()
    classname_dict.clear()

    tree = [["Menu 1", [["Hey", "Heyyyy", "Hi-ho"], "GRuh"], "Ahoy"], ["Menu 2", "menu 1", "menu 2"], "Menu 3"]
    #build_tree(tree)

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
    

    for cls in node_categories:
        print(cls)
    for func in category_draw_funcs:
        print(func)

def unregister():
    global node_categories

    for draw_func in category_draw_funcs:
        bpy.types.NODE_MT_add.remove(draw_func)

    for item in node_categories:
        bpy.utils.unregister_class(item)



