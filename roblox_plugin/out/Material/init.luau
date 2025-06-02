--!native
-- Compiled with roblox-ts v3.0.0
local Material = {}
do
	local _container = Material
	local function create(materialData)
		local _binding = materialData
		local name = _binding[1]
		local hasImage = _binding[2]
		local useImageTransparency = _binding[3]
		local imageHash = _binding[4]
		local alpha = _binding[5]
		-- const consumers: Consumer[] = [];
		-- for (const meshImage of meshImages) {
		-- 	const [hasImage, useImageTransparency, meshHash, alpha, imageHash] = meshImage;
		-- 	const meshAsset = meshes.get(meshHash)!;
		-- 	const consumer: Consumer = {
		-- 		meshParts: [],
		-- 		size: size,
		-- 		useImageTransparency: useImageTransparency,
		-- 	};
		-- 	MeshAsset.addConsumer(meshAsset, consumer);
		-- 	if (hasImage) {
		-- 		ImageAsset.addConsumer(images.get(imageHash), consumer);
		-- 	}
		-- 	for (const meshPart of consumer.meshParts) {
		-- 		meshPart.Material = Enum.Material.Fabric;
		-- 		meshPart.CastShadow = false;
		-- 		meshPart.CFrame = cframe;
		-- 		if (!useImageTransparency) {
		-- 			meshPart.Transparency = 1 - alpha / 255;
		-- 		}
		-- 	}
		-- 	consumers.push(consumer);
		-- }
		local instance
		-- if (consumers.size() > 1) {
		-- 	instance = new Instance("Model");
		-- 	for (const consumer of consumers) {
		-- 		consumer.instance!.Parent = instance;
		-- 	}
		-- } else {
		-- 	instance = consumers[0].instance!;
		-- }
		-- instance.Name = name;
		-- instance.Parent = Workspace;
		-- return {
		-- 	name: name,
		-- 	instance: instance,
		-- 	consumers: consumers,
		-- };
	end
	_container.create = create
	-- export function addConsumer() {}
end
local default = Material
return {
	Material = Material,
	default = default,
}
