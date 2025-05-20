--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.include.RuntimeLib)
local AssetService = TS.import(script, script.Parent, "include", "node_modules", "@rbxts", "services").AssetService
local ImageAsset = {}
do
	local _container = ImageAsset
	local function create(imageBuffer)
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
		local content = Content.fromObject(image)
		-- if (this.isAlpha) {
		-- 	const [result, assetId] = AssetService.CreateAssetAsync(this.content.Object!, Enum.AssetType.Image, {
		-- 		Name: "test",
		-- 	}) as LuaTuple<[Enum.CreateAssetResult, number]>;
		-- 	if (result === Enum.CreateAssetResult.Success) {
		-- 		this.assetId = `rbxassetid://${assetId}`;
		-- 	}
		-- }
		return {
			content = content,
			consumers = {},
		}
	end
	_container.create = create
	local function addConsumer(imageAsset, consumer)
		local imageConsumer = {
			consumer = consumer,
		}
		local _exp = imageAsset.consumers
		table.insert(_exp, imageConsumer)
		if consumer.useImageTransparency then
			for _, meshPart in consumer.meshParts do
				meshPart.TextureContent = imageAsset.content
				meshPart.Transparency = 0.02
				-- let surfaceAppearance = new Instance("SurfaceAppearance");
				-- surfaceAppearance.AlphaMode = Enum.AlphaMode.Transparency;
				-- surfaceAppearance.ColorMap = this.assetId;
				-- surfaceAppearance.Parent = meshPart;
			end
		else
			for _, meshPart in consumer.meshParts do
				meshPart.TextureContent = imageAsset.content
			end
		end
	end
	_container.addConsumer = addConsumer
end
local default = ImageAsset
return {
	ImageAsset = ImageAsset,
	default = default,
}
