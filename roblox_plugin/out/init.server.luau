--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.include.RuntimeLib)
local Server = TS.import(script, script, "server").default
local MeshAsset = TS.import(script, script, "MeshAsset").MeshAsset
local ImageAsset = TS.import(script, script, "ImageAsset").ImageAsset
local Workspace = TS.import(script, script, "include", "node_modules", "@rbxts", "services").Workspace
-- const toolbar = plugin.CreateToolbar("test");
-- const button = toolbar.CreateButton("testbutton", "", "");
-- button.Click.Connect(() => {});
-- const increment: number = (plugin.GetSetting("increment") as number | null) ?? 0;
-- plugin.SetSetting("increment", increment + 1);
-- print("plugin ran", increment, plugin.GetSetting("Rojo_confirmationBehavior"));
local meshes, images
local Object = {}
do
	local _container = Object
	local function create(objectData)
		local _binding = objectData
		local name = _binding[1]
		local cframe = _binding[2]
		local size = _binding[3]
		local meshImages = _binding[4]
		local consumers = {}
		for _, meshImage in meshImages do
			local _binding_1 = meshImage
			local hasImage = _binding_1[1]
			local useImageTransparency = _binding_1[2]
			local meshHash = _binding_1[3]
			local alpha = _binding_1[4]
			local imageHash = _binding_1[5]
			local meshAsset = meshes[meshHash]
			local consumer = {
				meshParts = {},
				size = size,
				useImageTransparency = useImageTransparency,
			}
			MeshAsset.addConsumer(meshAsset, consumer)
			if hasImage then
				ImageAsset.addConsumer(images[imageHash], consumer)
			end
			for _1, meshPart in consumer.meshParts do
				meshPart.Material = Enum.Material.Fabric
				meshPart.CastShadow = false
				meshPart.CFrame = cframe
				if not useImageTransparency then
					meshPart.Transparency = 1 - alpha / 255
				end
			end
			table.insert(consumers, consumer)
		end
		local instance
		if #consumers > 1 then
			instance = Instance.new("Model")
			for _, consumer in consumers do
				consumer.instance.Parent = instance
			end
		else
			instance = consumers[1].instance
		end
		instance.Name = name
		instance.Parent = Workspace
		return {
			name = name,
			instance = instance,
			consumers = consumers,
		}
	end
	_container.create = create
end
meshes = {}
images = {}
local objects = {}
Server.Hook("sendObjects", function(sendMeshes, sendImages, sendObjects)
	for meshHash, meshBuffer in sendMeshes do
		local _arg1 = MeshAsset.create(meshBuffer)
		meshes[meshHash] = _arg1
	end
	for imageHash, imageBuffer in sendImages do
		local _arg1 = ImageAsset.create(imageBuffer)
		images[imageHash] = _arg1
	end
	for objectHash, objectData in sendObjects do
		local _arg1 = Object.create(objectData)
		objects[objectHash] = _arg1
	end
end)
plugin.Unloading:Connect(function()
	Server.Unloading()
end)
