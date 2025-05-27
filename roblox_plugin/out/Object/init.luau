--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.include.RuntimeLib)
local Workspace = TS.import(script, script.Parent, "include", "node_modules", "@rbxts", "services").Workspace
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
			-- const meshAsset = meshes.get(meshHash)!;
			-- const consumer: Consumer = {
			-- 	meshParts: [],
			-- 	size: size,
			-- 	useImageTransparency: useImageTransparency,
			-- };
			-- MeshAsset.addConsumer(meshAsset, consumer);
			-- if (hasImage) {
			-- 	ImageAsset.addConsumer(images.get(imageHash!), consumer);
			-- }
			-- for (const meshPart of consumer.meshParts) {
			-- 	meshPart.Material = Enum.Material.Fabric;
			-- 	meshPart.CastShadow = false;
			-- 	meshPart.CFrame = cframe;
			-- 	if (!useImageTransparency) {
			-- 		meshPart.Transparency = 1 - alpha / 255;
			-- 	}
			-- }
			-- consumers.push(consumer);
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
local default = Object
return {
	Object = Object,
	default = default,
}
