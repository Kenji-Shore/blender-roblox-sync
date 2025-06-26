import bpy, hashlib

def register(utils, package):
    ASSET_TYPES = {
        "scene": bpy.types.Scene,
        "collection": bpy.types.Collection,
        "object": bpy.types.Object,
        "mesh": bpy.types.Mesh,
        "material": bpy.types.Material,
    }
    ROOT_FILE_NAME = None
    class Assets:
        data = {}
        def __init__(self):
            for asset_type_str, asset_type in ASSET_TYPES.items():
                module = utils.import_module(f"process_{asset_type_str}")
                self.data[asset_type] = {
                    "process": module.process,
                    "validated": [],
                    "send": []
                }

        sync_needed = False
        def invalidate(self, asset):
            asset_type = type(asset)
            if asset_type in self.data:
                asset_data = self.data[asset_type]
                if asset in asset_data["validated"]:
                    asset_data["validated"].remove(asset)
                    self.sync_needed = True
        def process(self, asset):
            asset_type = type(asset)
            if asset_type in self.data:
                asset_name = self.get_asset_name(asset)
                asset_data = self.data[asset_type]
                if not (asset in asset_data["validated"]):
                    send = asset_data["process"](self, asset)
                    if send:
                        asset_data["validated"].append(asset)
                        asset_data["send"] = asset_name + send
                        return asset_name
                else:
                    return asset_name
        
        depsgraph = None
        hashes = {}
        def hash_bytes(self, bytes):
            hashed_bytes = hashlib.sha256(bytes).digest()
            if not hashed_bytes in self.hashes:
                self.hashes[hashed_bytes] = bytes
            return hashed_bytes
        
        def get_asset_name(self, asset):
            nonlocal ROOT_FILE_NAME
            if not ROOT_FILE_NAME:
                ROOT_FILE_NAME = bpy.path.basename(bpy.context.blend_data.filepath)
            file_name = bpy.path.basename(asset.library.filepath) if asset.library else ROOT_FILE_NAME
            return (asset.name, file_name,)
        
    assets = Assets()

    def depsgraph_update_post(scene, depsgraph):
        assets.depsgraph = depsgraph
        for depsgraph_update in depsgraph.updates:
            asset = depsgraph_update.id
            match type(asset):
                case bpy.types.Material:
                    assets.invalidate(asset)
                case bpy.types.Mesh:
                    if depsgraph_update.is_updated_geometry:
                        assets.invalidate(asset)
                case bpy.types.Object:
                    if depsgraph_update.is_updated_transform and not depsgraph_update.is_updated_geometry:
                        assets.invalidate(asset)
                case bpy.types.Collection:
                    assets.invalidate(asset)

    return {
        "listeners": (utils.listen_handler("depsgraph_update_post", depsgraph_update_post),) 
    }