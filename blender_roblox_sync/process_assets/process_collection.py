import bpy

def register(utils, package):
    
    global process
    def process(assets, collection):
        objects = []
        for object in collection.objects:
            objects.append(assets.process(object))
        children = []
        for child in collection.children:
            children.append(assets.process(child))
        return (collection.instance_offset, objects, children,)
        