# Copyright (C) 2021-2024
# lightningpirate@gmail.com.com

# Created by LightningPirate

# This file is part of SWE1R Import/Export.

#     SWE1R Import/Export is free software; you can redistribute it and/or
#     modify it under the terms of the GNU General Public License
#     as published by the Free Software Foundation; either version 3
#     of the License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program; if not, see <https://www.gnu.org
# /licenses>.

bl_info = {
    "name": "SWE1R Import/Export",
    "blender": (2, 80, 0),
    "category": "Object",
}

import os
import json

if "bpy" in locals(): #means Blender already started once
    print('already loaded in blender')
    import importlib
    importlib.reload(swr_import)
    importlib.reload(swr_export)
    importlib.reload(block)
    importlib.reload(modelblock)
    importlib.reload(textureblock)
    importlib.reload(splineblock)
    importlib.reload(general)
    importlib.reload(popup)
else: #start up
    print('starting up for the first time')
    from .swr_import import *
    from .swr_export import *
    from .popup import *
    from .model_list import *
    from .modelblock import *
    from .block import *
    from .textureblock import *
    from .splineblock import *
    from .general import *

import bpy

version = bpy.app.version_string
version = version.split(".")
if version[0] is not "4" and version[1] is not "0":
    print("blender-swe1r: Unsupported Blender version")
SETTINGS_FILE = os.path.join(bpy.utils.user_resource('CONFIG'), "blender_swe1r_settings.json")

def save_settings(self, context):
    keys = ['import_folder', 'import_type', 'import_model', 'export_folder', 'export_model', 'export_texture', 'export_spline']
    settings = load_settings()
    for key in [key for key in keys if context.scene.get(key) is not None]:
        settings[key] = context.scene.get(key)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def load_settings():
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    return settings

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)

def get_setting(key, default=None):
    settings = load_settings()
    val = settings.get(key, default)
    return val if val is not None else default

model_types = [('0', 'All', 'View all models'),
                            ('1', 'MAlt', 'High LOD pods'),
                            ('2', 'Modl', 'Misc animated elements'),
                            ('3', 'Part', 'Misc props'),
                            ('4', 'Podd', 'Pod models'),
                            ('5', 'Pupp', 'Animated racers'),
                            ('6', 'Scen', 'Animated scenes'),
                            ('7', 'Trak', 'Tracks'),
                            ]
models = [(str(i), f"{model['extension']} {model['name']}", f"Import model {model['name']}") for i, model in enumerate(model_list)]
classes = []

def update_model_dropdown(self, context):
    model_type = model_types[int(context.scene.import_type)][1]
    
    if model_type == 'All':
        items_for_selected_category = [(str(i), f"{model['extension']} {model['name']}", f"Import model {model['name']}") for i, model in enumerate(model_list)]
    else:
        items_for_selected_category = [(str(i), f"{model['name']}", f"Import model {model['name']}") for i, model in enumerate(model_list) if model['extension'] == model_type]
        items_for_selected_category.insert(0, ('-1', 'All', 'Import all models'))
        
    bpy.types.Scene.import_model = bpy.props.EnumProperty(
        items=items_for_selected_category,
        name="Model Selection",
        description="Select models to import",
    )
    save_settings(self, context)
    
    
bpy.types.Object.target = bpy.props.PointerProperty(type=bpy.types.Object)

class ImportPanel(bpy.types.Panel):
    bl_label = "Import"
    bl_idname = "PT_ImportPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SWE1R Import/Export'
    
    def draw(self, context):
        layout = self.layout
            
        # Import
        layout.prop(context.scene, "import_folder", text = '', full_event=False)
        layout.prop(context.scene, "import_type", text="Type")
        layout.prop(context.scene, "import_model", text="Model")
        row = layout.row()
        row.scale_y = 1.5
        row.operator("import.import_operator", text="Import", icon = 'IMPORT')
        
class ExportPanel(bpy.types.Panel):
    bl_label = "Export"
    bl_idname = "PT_ExportPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SWE1R Import/Export'
    
    def draw(self, context):
        layout = self.layout
            
        # Export
        layout.prop(context.scene, "export_folder", text="",  full_event=False)
        row = layout.row(align=True)
        row.prop(context.scene, "export_model", text="Model", icon='MESH_CUBE', toggle=True, icon_only=True)
        row.prop(context.scene, "export_texture", text="Texture", icon='MATERIAL', toggle=True, icon_only=True)
        row.prop(context.scene, "export_spline", text="Spline", icon='CURVE_BEZCURVE', toggle=True, icon_only=True)
        row = layout.row()
        row.scale_y = 1.5
        row.operator("import.export_operator", text="Export", icon = 'EXPORT')
        
class ToolPanel(bpy.types.Panel):
    bl_label = "Tools"
    bl_idname = "PT_ToolPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SWE1R Import/Export'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row(align=True)
        row.label(text = "Visuals")
        row.operator("import.select_visible", text = "Select", icon = 'SELECT_SET')
        row.prop(context.scene, "visuals_visible", toggle=True, text = "", icon = 'HIDE_OFF' if context.scene.visuals_visible else 'HIDE_ON')
        row.prop(context.scene, "visuals_selectable", toggle =True, text = "", icon = 'RESTRICT_SELECT_OFF' if context.scene.visuals_selectable else 'RESTRICT_SELECT_ON') 
        
        row = layout.row(align=True)
        row.label(text = "Collision")
        row.operator("import.select_collidable", text = "Select", icon = 'SELECT_SET')
        row.prop(context.scene, "collision_visible", toggle=True, text = "", icon = 'HIDE_OFF' if context.scene.collision_visible else 'HIDE_ON')
        row.prop(context.scene, "collision_selectable", toggle =True, text = "", icon = 'RESTRICT_SELECT_OFF' if context.scene.collision_selectable else 'RESTRICT_SELECT_ON') 
        
        
class SelectedPanel(bpy.types.Panel):
    bl_label = "Selected"
    bl_idname = "PT_SelectedPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SWE1R Import/Export'
 
    def draw(self, context):
        layout = self.layout
        
        if not context.selected_objects:
            layout.label(text = "Select an object to edit its properties")
            return

        mesh = False
        collidable = True
        collidable_data = True
        visible = True
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                if 'collidable'  not in obj or not obj['collidable']:
                    collidable = False
                if 'visible'  not in obj or not obj['visible']:
                    visible = False
                mesh = True
                
        if mesh:
            
            if not visible:
                row = layout.row(align=True)
                row.label(text = 'Visuals')
                row.operator("import.set_visible", text= "Add")
            else:
                box = layout.box()
                row = layout.row()
                row.label(text = 'Visuals')
                row.operator("import.set_visible", text = "", icon = "X", emboss = False)
                box.operator("import.v_color", text="Set Up Vertex Colors")
                
            
            box = layout.box()
            row = box.row(align=True)
            row.label(text = 'Collision')
            if not collidable:
                row.operator("import.set_collidable", text= "", icon = "ADD", emboss = False)
            else:
                row.operator("import.set_collidable", text = "", icon = "X", emboss = False)
            
            
        

class ImportOperator(bpy.types.Operator):
    bl_label = "SWE1R Import/Export"
    bl_idname = "import.import_operator"
    

    def execute(self, context):
        folder_path = context.scene.import_folder
        if folder_path == "":
            show_custom_popup(bpy.context, "No set import folder", "Select your folder containing the .bin files")
            return {'CANCELLED'}
        if folder_path[:2] == '//':
            folder_path = os.path.join(os.path.dirname(bpy.data.filepath), folder_path[2:])
        if not os.path.exists(folder_path  + 'out_modelblock.bin'):
            show_custom_popup(bpy.context, "Missing required files", "No out_modelblock.bin found in the selected folder.")
            return {'CANCELLED'}

        import_model(folder_path, [int(context.scene.import_model)])
        return {'FINISHED'}

class ExportOperator(bpy.types.Operator):
    bl_label = "SWE1R Import/Export"
    bl_idname = "import.export_operator"

    def execute(self, context):
        selected_objects = context.selected_objects
        selected_collection = context.view_layer.active_layer_collection.collection
        if selected_objects:
            selected_collection = selected_objects[0].users_collection[0]
            
        if selected_collection is None:
            show_custom_popup(bpy.context, "No collection", "Exported items must be part of a collection")
            return {'CANCELLED'}
                
        folder_path = context.scene.export_folder if context.scene.export_folder else context.scene.import_folder
        
        if 'ind' not in selected_collection:
            show_custom_popup(bpy.context, "Invalid collection selected", "Please select a model collection to export")
            return {'CANCELLED'}
        if folder_path == "":
            show_custom_popup(bpy.context, "No set export folder", "Select your folder containing the .bin files")
            return {'CANCELLED'}
        if not os.path.exists(folder_path  + 'out_modelblock.bin'):
            show_custom_popup(bpy.context, "Missing required files", "No out_modelblock.bin found in the selected folder.")
            return {'CANCELLED'}
        
        export_model(selected_collection, folder_path, [context.scene.export_model, context.scene.export_texture, context.scene.export_spline])
        return {'FINISHED'}
    
class VertexColorOperator(bpy.types.Operator):
    bl_label = "SWE1R Import/Export"
    bl_idname = "import.v_color"
    
    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.geometry.color_attribute_add(name = "color", domain = "CORNER", data_type="BYTE_COLOR", color = [1.0, 1.0, 1.0, 1.0])
        return {'FINISHED'}
  
class VisibleOperator(bpy.types.Operator):
    bl_label = "SWE1R Import/Export"
    bl_idname = "import.set_visible"
    
    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            obj['visible'] = True
        return {'FINISHED'}
    
class CollidableOperator(bpy.types.Operator):
    bl_label = "SWE1R Import/Export"
    bl_idname = "import.set_collidable"
    
    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            obj['collidable'] = True
        return {'FINISHED'}
    
class VisibleSelect(bpy.types.Operator):
    bl_label = "SWE1R Import/Export"
    bl_idname = "import.select_visible"
    
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        
        #make selectable
        if not context.scene.visuals_selectable:
            context.scene.visuals_selectable = True
        SelVis(self, context)
        
        for obj in bpy.data.objects:
            if 'visible' in obj and obj['visible']:
                obj.select_set(True)
        return {'FINISHED'}
    
class CollidableSelect(bpy.types.Operator):
    bl_label = "SWE1R Import/Export"
    bl_idname = "import.select_collidable"
    
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        
        #make selectable
        if not context.scene.collision_selectable:
            context.scene.collision_selectable = True
        SelCol(self, context)
        
        for obj in bpy.data.objects:
            if 'collidable' in obj and obj['collidable']:
                obj.select_set(True)
        return {'FINISHED'}
    
def SplineVis(self, context = None):
    for obj in bpy.context.scene.objects:
        if obj.type == "CURVE":
            obj.hide_viewport = not context.scene.spline_visible

def ColVis(self, context = None):
    for obj in bpy.context.scene.objects:
        if 'collidable' in obj and obj['collidable']:
            obj.hide_viewport = not context.scene.collision_visible
            
def ShoVis(self, context = None):
    for obj in bpy.context.scene.objects:
        if 'visible' in obj and obj['visible']:
            obj.hide_viewport = not context.scene.visuals_visible
                
def SelVis(self, context = None):
    for obj in bpy.context.scene.objects:
        if 'visible' in obj and obj['visible']:
            obj.hide_select = not context.scene.visuals_selectable

def SelCol(self, context = None):
    for obj in bpy.context.scene.objects:
        if 'collidable' in obj and obj['collidable']:
            obj.hide_select = not context.scene.collision_selectable
                
def EmptyVis(self, context):
    for obj in bpy.context.scene.objects:
        if obj.type == "EMPTY" or obj.type == "LIGHT":
            obj.hide_viewport = not context.scene.emptyvis


def menu_func(self, context):
    self.layout.operator(ImportOperator.bl_idname)
    self.layout.operator(ExportOperator.bl_idname)

def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.import_folder = bpy.props.StringProperty(subtype='DIR_PATH', update=save_settings, default =get_setting('import_folder', ""), description="Select the lev01 folder (or any folder containing the .bin files)")
    bpy.types.Scene.import_type = bpy.props.EnumProperty(
        items=model_types,
        name="Model Type",
        description="Select model type",
        default=get_setting('import_type', 0), 
        update=update_model_dropdown
    )
    bpy.types.Scene.import_model = bpy.props.EnumProperty(
        items=models,
        name="Model",
        description="Select model",
        default=get_setting('import_model', 0), 
        update=save_settings
    )
    bpy.types.Scene.export_folder = bpy.props.StringProperty(subtype='DIR_PATH', update=save_settings, default=get_setting('export_folder', ""), description="Select the lev01 folder (or any folder you wish to export to)")
    bpy.types.Scene.export_model = bpy.props.BoolProperty(name="Model", update=save_settings, default=get_setting('export_model', True))
    bpy.types.Scene.export_texture = bpy.props.BoolProperty(name="Texture", update=save_settings, default=get_setting('export_texture', True))
    bpy.types.Scene.export_spline = bpy.props.BoolProperty(name="Spline", update=save_settings, default=get_setting('export_spline', True))
    bpy.types.Scene.collision_visible = bpy.props.BoolProperty(name = 'collision_visible', update =ColVis, default=True)
    bpy.types.Scene.collision_selectable = bpy.props.BoolProperty(name = 'collision_selectable', update =SelCol, default=True)
    bpy.types.Scene.visuals_visible = bpy.props.BoolProperty(name = 'visuals_visible', update =ShoVis, default=True)
    bpy.types.Scene.visuals_selectable = bpy.props.BoolProperty(name = 'visuals_selectable', update =SelVis, default=True)
    bpy.types.Scene.visible = bpy.props.BoolProperty(name = 'visible', default=False)
    bpy.types.Scene.collidable = bpy.props.BoolProperty(name = 'collidable', default=False)

    bpy.utils.register_class(ImportPanel)
    bpy.utils.register_class(ExportPanel)
    bpy.utils.register_class(ToolPanel)
    
    bpy.utils.register_class(SelectedPanel)
    bpy.utils.register_class(ImportOperator)
    bpy.utils.register_class(ExportOperator)
    bpy.utils.register_class(VertexColorOperator)
    bpy.utils.register_class(CollidableOperator)
    bpy.utils.register_class(VisibleSelect)
    bpy.utils.register_class(CollidableSelect)
    bpy.utils.register_class(VisibleOperator)
    bpy.types.TOPBAR_MT_file.append(menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(ImportPanel)
    bpy.utils.unregister_class(ExportPanel)
    bpy.utils.unregister_class(ToolPanel)
        
    bpy.utils.unregister_class(SelectedPanel)
    bpy.utils.unregister_class(ImportOperator)
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(VertexColorOperator)
    bpy.utils.unregister_class(CollidableSelect)
    bpy.utils.unregister_class(VisibleSelect)
    bpy.utils.unregister_class(VisibleOperator)
    
    bpy.types.TOPBAR_MT_file.remove(menu_func)
    del bpy.types.Scene.import_folder
    del bpy.types.Scene.import_type
    del bpy.types.Scene.import_model
    del bpy.types.Scene.export_folder
    del bpy.types.Scene.export_model
    del bpy.types.Scene.export_texture
    del bpy.types.Scene.export_spline
