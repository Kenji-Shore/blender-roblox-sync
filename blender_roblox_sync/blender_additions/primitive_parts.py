import bpy, bmesh

def register(utils, package):
    def load_post():
        resources_path = utils.get_resources_path(package)
        
    return {
        # "classes": (VIEW3D_PT_sculpt_dyntopo, VIEW3D_PT_sculpt_voxel_remesh,),
        "listeners": (
            # utils.listen_mode(("VERTEX_PAINT", "SCULPT"), enter=enter_vertex_paint, exit=exit_vertex_paint), 
            # utils.listen_depsgraph_update(add_vertex_colors),
            utils.listen_handler("load_post", load_post),
        ),
    }