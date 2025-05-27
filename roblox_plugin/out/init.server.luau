--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.include.RuntimeLib)
local Server = TS.import(script, script, "server").default
-- const toolbar = plugin.CreateToolbar("test");
-- const button = toolbar.CreateButton("testbutton", "", "");
-- button.Click.Connect(() => {});
-- const increment: number = (plugin.GetSetting("increment") as number | null) ?? 0;
-- plugin.SetSetting("increment", increment + 1);
-- print("plugin ran", increment, plugin.GetSetting("Rojo_confirmationBehavior"));
local meshes = {}
local images = {}
local objects = {}
-- Server.Hook("sendObjects", (sendMeshes, sendImages, sendObjects) => {
-- 	for (const [meshHash, meshBuffer] of sendMeshes as Map<string, buffer>) {
-- 		meshes.set(meshHash, MeshAsset.create(meshBuffer));
-- 	}
-- 	for (const [imageHash, imageBuffer] of sendImages as Map<string, buffer>) {
-- 		images.set(imageHash, ImageAsset.create(imageBuffer));
-- 	}
-- 	for (const [objectHash, objectData] of sendObjects as Map<string, ObjectData>) {
-- 		objects.set(objectHash, Object.create(objectData));
-- 	}
-- });
plugin.Unloading:Connect(function()
	Server.Unloading()
end)
