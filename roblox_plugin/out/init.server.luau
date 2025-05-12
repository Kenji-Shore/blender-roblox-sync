--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.include.RuntimeLib)
local Server = TS.import(script, script, "server").default
local Mesh = TS.import(script, script, "Mesh").Mesh
local _services = TS.import(script, script, "include", "node_modules", "@rbxts", "services")
local AssetService = _services.AssetService
local Workspace = _services.Workspace
local function makeHello(name)
	return `Hello from {name}!`
end
local toolbar = plugin:CreateToolbar("test")
local button = toolbar:CreateButton("testbutton", "", "")
button.Click:Connect(function() end)
-- const increment: number = (plugin.GetSetting("increment") as number | null) ?? 0;
-- plugin.SetSetting("increment", increment + 1);
-- print("plugin ran", increment, plugin.GetSetting("Rojo_confirmationBehavior"));
local Image
do
	Image = setmetatable({}, {
		__tostring = function()
			return "Image"
		end,
	})
	Image.__index = Image
	function Image.new(...)
		local self = setmetatable({}, Image)
		return self:constructor(...) or self
	end
	function Image:constructor(imageBuffer)
		-- if (this.isAlpha) {
		-- 	const [result, assetId] = AssetService.CreateAssetAsync(this.content.Object!, Enum.AssetType.Image, {
		-- 		Name: "test",
		-- 	}) as LuaTuple<[Enum.CreateAssetResult, number]>;
		-- 	if (result === Enum.CreateAssetResult.Success) {
		-- 		this.assetId = `rbxassetid://${assetId}`;
		-- 	}
		-- }
		local width = buffer.readu16(imageBuffer, 0)
		local height = buffer.readu16(imageBuffer, 2)
		local size = Vector2.new(width, height)
		local image = AssetService:CreateEditableImage({
			Size = size,
		})
		local totalBytes = width * height * 4
		local pixelsBuffer = buffer.create(totalBytes)
		buffer.copy(pixelsBuffer, 0, imageBuffer, 4)
		image:WritePixelsBuffer(Vector2.zero, size, pixelsBuffer)
		self.content = Content.fromObject(image)
		-- if (this.isAlpha) {
		-- 	const [result, assetId] = AssetService.CreateAssetAsync(this.content.Object!, Enum.AssetType.Image, {
		-- 		Name: "test",
		-- 	}) as LuaTuple<[Enum.CreateAssetResult, number]>;
		-- 	if (result === Enum.CreateAssetResult.Success) {
		-- 		this.assetId = `rbxassetid://${assetId}`;
		-- 	}
		-- }
	end
	function Image:apply(meshPart, useImageTransparency)
		if useImageTransparency then
			-- && this.assetId) {
			meshPart.TextureContent = self.content
			meshPart.Transparency = 0.02
			-- let surfaceAppearance = new Instance("SurfaceAppearance");
			-- surfaceAppearance.AlphaMode = Enum.AlphaMode.Transparency;
			-- surfaceAppearance.ColorMap = this.assetId;
			-- surfaceAppearance.Parent = meshPart;
		else
			meshPart.TextureContent = self.content
		end
	end
end
local meshes = {}
local images = {}
local objects = {}
local MeshObject
do
	MeshObject = setmetatable({}, {
		__tostring = function()
			return "MeshObject"
		end,
	})
	MeshObject.__index = MeshObject
	function MeshObject.new(...)
		local self = setmetatable({}, MeshObject)
		return self:constructor(...) or self
	end
	function MeshObject:constructor(objectData)
		local _binding = objectData
		local name = _binding[1]
		local cframe = _binding[2]
		local size = _binding[3]
		local meshImages = _binding[4]
		local separatedMeshes = {}
		for _, meshImage in meshImages do
			local _binding_1 = meshImage
			local hasImage = _binding_1[1]
			local useImageTransparency = _binding_1[2]
			local meshHash = _binding_1[3]
			local alpha = _binding_1[4]
			local imageHash = _binding_1[5]
			local sourceMesh = meshes[meshHash]
			local meshSize = sourceMesh.meshSize
			local _exp = (meshSize * size):Max(meshSize) // 2048
			local _one = Vector3.one
			local chunks = _exp + _one
			local mesh = Mesh.new(sourceMesh, chunks)
			mesh:renderContent()
			for _1, content in mesh.contents do
				local meshPart = AssetService:CreateMeshPartAsync(content, {
					CollisionFidelity = Enum.CollisionFidelity.Box,
					RenderFidelity = Enum.RenderFidelity.Precise,
					FluidFidelity = Enum.FluidFidelity.UseCollisionGeometry,
				})
				if hasImage then
					images[imageHash]:apply(meshPart, useImageTransparency)
				end
				meshPart.Material = Enum.Material.Fabric
				meshPart.CastShadow = false
				meshPart.CFrame = cframe
				meshPart.Size = meshPart.Size * size
				if not useImageTransparency then
					meshPart.Transparency = 1 - alpha / 255
				end
				table.insert(separatedMeshes, meshPart)
			end
		end
		local object
		if #separatedMeshes > 1 then
			object = Instance.new("Model")
			for _, meshPart in separatedMeshes do
				meshPart.Parent = object
			end
		else
			object = separatedMeshes[1]
		end
		object.Name = name
		object.Parent = Workspace
		self.name = name
		self.object = object
	end
end
Server.Hook("sendObjects", function(sendMeshes, sendImages, sendObjects)
	for meshHash, meshBuffer in sendMeshes do
		local sourceMesh = Mesh.new(meshBuffer)
		meshes[meshHash] = sourceMesh
	end
	for imageHash, imageBuffer in sendImages do
		local _image = Image.new(imageBuffer)
		images[imageHash] = _image
	end
	for objectHash, objectData in sendObjects do
		local _meshObject = MeshObject.new(objectData)
		objects[objectHash] = _meshObject
	end
end)
plugin.Unloading:Connect(function()
	Server.Unloading()
end)
return {
	makeHello = makeHello,
}
