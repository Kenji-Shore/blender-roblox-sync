import bpy, hashlib, time

def register(utils):
    
    ROOT_FILE_NAME = None
    class Assets:
        data = {}
        def __init__(self):
            modules = {
                "collection": utils.import_module("process_collection"),
                "instance": utils.import_module("process_instance"),
                "object": utils.import_module("process_object"),
                "mesh": utils.import_module("process_mesh"),
                "material": utils.import_module("process_material"),
            }
            for asset_type, module in modules.items():
                self.data[asset_type] = {
                    "process": module.process,
                    "validated": [],
                    "send": {}
                }

        sync_needed = False
        def invalidate(self, asset_type, asset):
            asset_data = self.data[asset_type]
            if asset in asset_data["validated"]:
                asset_data["validated"].remove(asset)
                self.sync_needed = True
        def process(self, asset_type, asset):
            asset_data = self.data[asset_type]
            if not (asset in asset_data["validated"]):
                send = asset_data["process"](self, asset)
                if send:
                    asset_data["validated"].append(asset)
                    asset_data["send"][asset.name] = send
        
        depsgraph = None
        hashes = {}
        def hash_bytes(self, bytes):
            hashed_bytes = hashlib.sha256(bytes).digest()
            if not hashed_bytes in self.hashes:
                self.hashes[hashed_bytes] = bytes
            return hashed_bytes
        
        def get_data_file(self, data):
            nonlocal ROOT_FILE_NAME
            if not ROOT_FILE_NAME:
                ROOT_FILE_NAME = bpy.path.basename(bpy.context.blend_data.filepath)
            return bpy.path.basename(data.library.filepath) if data.library else ROOT_FILE_NAME
        
    assets = Assets()

    global process
    def process():
        process_collection(bpy.context.scene.collection)

    def depsgraph_update_post(scene, depsgraph):
        assets.depsgraph = depsgraph
        for depsgraph_update in depsgraph.updates:
            asset = depsgraph_update.id
            match type(asset):
                case bpy.types.Material:
                    assets.invalidate("material", asset)
                case bpy.types.Mesh:
                    if depsgraph_update.is_updated_geometry:
                        assets.invalidate("mesh", asset)
                case bpy.types.Object:
                    if depsgraph_update.is_updated_transform and not depsgraph_update.is_updated_geometry:
                        assets.invalidate("object", asset)
                case bpy.types.Collection:
                    assets.invalidate("collection", asset)

    return {
        "listeners": (utils.listen_handler("depsgraph_update_post", depsgraph_update_post),) 
    }