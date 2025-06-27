import bpy

def register(utils, package):
    manage_roblox_plugin = utils.import_module("manage_roblox_plugin")
    server = utils.import_module("server")
    process_assets = utils.import_module("process_assets")

    syncing = False
    class VIEW3D_OT_toggle_roblox_sync(bpy.types.Operator):
        bl_idname = "view3d.toggle_roblox_sync"
        bl_label = "Toggle Roblox Sync"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            nonlocal syncing
            syncing = not syncing
            return {"FINISHED"}
    
    class SyncingAsset(bpy.types.PropertyGroup):
        is_scene: bpy.props.BoolProperty()
        id: bpy.props.PointerProperty(type=bpy.types.ID)
    bpy.utils.register_class(SyncingAsset)
    bpy.types.Scene.currently_syncing = bpy.props.CollectionProperty(type=SyncingAsset)
    bpy.types.Scene.currently_syncing_index = bpy.props.IntProperty(default=0)

    class SyncingAssetPrefs(bpy.types.PropertyGroup):
        name: bpy.props.StringProperty()
        file: bpy.props.StringProperty()
        asset_type_str: bpy.props.StringProperty()
        is_paused: bpy.props.BoolProperty()
        
    class VIEW3D_OT_toggle_sync(bpy.types.Operator):
        bl_idname = "view3d.toggle_sync"
        bl_label = "Toggle Syncing Object"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            context.scene.currently_syncing.remove(context.scene.currently_syncing_index)
            return {"FINISHED"}
    
    class VIEW3D_UL_sync_list(bpy.types.UIList):
        def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
            # print(icon, active_property, getattr(active_data, active_property), index)
            # "OUTLINER_COLLECTION" collection
            # "OUTLINER_OB_GROUP_INSTANCE" instance
            
            set_text = ""
            set_icon = ""
            if item.is_scene:
                set_text = "Scene"
                set_icon = "SCENE_DATA"
            elif item.id:
                id = item.id
                set_text = id.name
                id_type = type(id)
                if id_type is bpy.types.Object:
                    if id.is_instancer:
                        set_icon = "OUTLINER_OB_GROUP_INSTANCE"
                    else:
                        set_icon = "OUTLINER_OB_MESH"
                elif id_type is bpy.types.Collection:
                    set_icon = "OUTLINER_COLLECTION"
            layout.label(text=set_text, icon=set_icon)
            if index == getattr(active_data, active_property):
                layout.operator("view3d.toggle_sync", text="", icon="PAUSE", emboss=False)
        def draw_filter(self, context, layout):
            return
    bpy.utils.register_class(VIEW3D_UL_sync_list)

    class VIEW3D_OT_sync_scene(bpy.types.Operator):
        bl_idname = "view3d.sync_scene"
        bl_label = "Sync Scene"
        bl_options = {"REGISTER", "UNDO"}

        @classmethod
        def poll(cls, context):
            for sync_id in context.scene.currently_syncing:
                if sync_id.is_scene:
                    return False
            return True
        
        def execute(self, context):
            syncing_id = bpy.context.scene.currently_syncing.add()
            syncing_id.is_scene = True
            return {"FINISHED"}
        
    class VIEW3D_OT_sync_selected(bpy.types.Operator):
        bl_idname = "view3d.sync_selected"
        bl_label = "Sync Selected"
        bl_options = {"REGISTER", "UNDO"}

        @classmethod
        def poll(cls, context):
            areas = [area for area in context.window.screen.areas if area.type == 'OUTLINER']
            if len(areas) > 0:
                return True
            return False
        
        def execute(self, context):
            areas = [area for area in context.window.screen.areas if area.type == 'OUTLINER']
            if len(areas) > 0:
                area = areas[0]
                with context.temp_override(
                    window=context.window,
                    area=area,
                    region=next(region for region in area.regions if region.type == 'WINDOW'),
                    screen=context.window.screen
                ):
                    for id in bpy.context.selected_ids:
                        syncing_id = bpy.context.scene.currently_syncing.add()
                        syncing_id.id = id
            return {"FINISHED"}

    class VIEW3D_OT_OTHER_OPERATOR(bpy.types.Operator):
        bl_idname = "view3d.hgf_other_operator"
        bl_label = "HGF Other Operator"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            process_assets.process()
            return {"FINISHED"}

    class VIEW3D_PT_roblox_sync(bpy.types.Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "Roblox"
        bl_label = "Roblox Sync"
        
        def draw(self, context):
            server.is_connected_area = context.area
            layout = self.layout

            box = layout.box()
            box.enabled = not syncing
            col = box.column(align=True)
            col.label(text="Currently Syncing:")
            col.template_list("VIEW3D_UL_sync_list", "", context.scene, "currently_syncing", context.scene, "currently_syncing_index", type="DEFAULT", rows=2, maxrows=4, sort_lock=True)

            split = col.split(factor=0.5, align=True)
            split.operator("view3d.sync_selected", text="+ Selected ")
            split.operator("view3d.sync_scene", text="+ Scene ")

            can_sync = False
            sync_text = ""
            if not manage_roblox_plugin.is_valid_dir:
                sync_text = "Invalid Plugin Directory"
            elif not server.is_connected:
                sync_text = "Roblox Studio Not Open"
            else:
                sync_text = "Stop Sync" if syncing else "Start Sync"
                can_sync = True
            
            col2 = layout.column()
            row = col2.row()
            row.operator("view3d.toggle_roblox_sync", text=sync_text)
            row.enabled = can_sync

            row2 = col2.row()
            row2.progress(factor=0.5)
            row2.scale_y = 0.4

            box = layout.box()
            active_object = bpy.context.object
            if active_object:
                row = box.row()
                row.prop(active_object, "is_invisible", text="Is Invisible")
                if active_object.is_invisible:
                    row = box.row()
                    row.prop(active_object, "invisible_color", text="Color")
            # layout.operator("view3d.hgf_other_operator", text="test button")
    
    def unregister():
        bpy.utils.unregister_class(SyncingAsset)
        bpy.utils.unregister_class(VIEW3D_UL_sync_list)
    return {
        "classes": (
            VIEW3D_OT_toggle_roblox_sync, 
            VIEW3D_PT_roblox_sync, 
            VIEW3D_OT_OTHER_OPERATOR, 
            VIEW3D_OT_sync_selected,
            VIEW3D_OT_sync_scene,
            VIEW3D_OT_toggle_sync,
            SyncingAssetPrefs,
        ),
        "prefs": {
            "syncing_list": bpy.props.CollectionProperty(type=SyncingAssetPrefs),
            "syncing_index": bpy.props.IntProperty(default=0)
        },
        "unregister": unregister
    }