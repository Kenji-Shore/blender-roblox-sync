import bpy

def register(utils, package):
    roblox_opencloud = utils.import_module("roblox_opencloud")

    global upload
    def upload():
        def response_callback(success, **kwargs):
            if success:
                print(kwargs["response_dict"])
            else:
                print(kwargs["reason"])
        roblox_opencloud.request("get",
            f"https://apis.roblox.com/assets/v1/assets/{5580068799}",
            scopes=("asset:read", "asset:write"),
            callback=response_callback,
        )
        
    class VIEW3D_OT_UPLOAD_ASSETS(bpy.types.Operator):
        bl_idname = "view3d.upload_assets"
        bl_label = "Upload Assets"
        bl_options = {"REGISTER", "UNDO"}

        def execute(self, context):
            upload()
            return {"FINISHED"}

    def draw(layout, context):
        layout.operator("view3d.upload_assets", text="Upload Assets")
    return {
        "classes": (VIEW3D_OT_UPLOAD_ASSETS,),
        "draw": (draw, 2),
    }