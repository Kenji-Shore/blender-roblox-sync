import bpy

def register(utils):

    global process
    def process(assets, scene):
        scene_collection = scene.collection
        objects = []
        for object in scene_collection.objects:
            objects.append(assets.process(object))
        children = []
        for child in scene_collection.children:
            children.append(assets.process(child))
        return (objects, children,)
        