--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.include.RuntimeLib)
local AssetService = TS.import(script, script.Parent, "include", "node_modules", "@rbxts", "services").AssetService
local loadFromBuffer = TS.import(script, script, "loadFromBuffer").loadFromBuffer
local loadFromMesh = TS.import(script, script, "loadFromMesh").loadFromMesh
local renderContent = TS.import(script, script, "renderContent").renderContent
local splitMesh = TS.import(script, script, "splitMesh").splitMesh
local MeshAsset = {}
do
	local _container = MeshAsset
	local function create(meshBuffer)
		local sourceMesh, minBounds, maxBounds = loadFromBuffer(Vector3.one, meshBuffer)
		return {
			minBounds = minBounds,
			maxBounds = maxBounds,
			meshSize = maxBounds - minBounds,
			sourceSplit = {
				divisions = Vector3.zero,
				divisionCount = 0,
				mesh = sourceMesh,
				consumers = {},
				contents = {},
			},
			splits = {},
		}
	end
	_container.create = create
	local function createMeshPart(content, size)
		local meshPart = AssetService:CreateMeshPartAsync(content, {
			CollisionFidelity = Enum.CollisionFidelity.Box,
			RenderFidelity = Enum.RenderFidelity.Precise,
			FluidFidelity = Enum.FluidFidelity.UseCollisionGeometry,
		})
		meshPart.Anchored = true
		meshPart.CanCollide = false
		meshPart.CanTouch = false
		meshPart.CanQuery = false
		local _size = meshPart.Size
		local _size_1 = size
		meshPart.Size = _size * _size_1
		return meshPart
	end
	local function addConsumer(meshAsset, consumer)
		local consumerSize = consumer.size
		local meshSize = meshAsset.meshSize
		local requiredSize = (meshSize * consumerSize):Max(meshSize)
		local _exp = requiredSize // 2048
		local _one = Vector3.one
		local requiredChunks = _exp + _one
		local divisions = Vector3.new(math.log(requiredChunks.X, 2), math.log(requiredChunks.Y, 2), math.log(requiredChunks.Z, 2)):Ceil()
		local split
		local splitFrom
		local splitFromIndex = 0
		local splits = meshAsset.splits
		for i = #splits - 1, 0, -1 or 1 do
			local compareSplit = splits[i + 1]
			local compareDivisions = compareSplit.divisions
			if (divisions - compareDivisions):Max(Vector3.zero) ~= Vector3.zero then
				if divisions == compareDivisions then
					split = compareSplit
				else
					splitFrom = compareSplit
					splitFromIndex = i
				end
				break
			end
		end
		if not split then
			if splitFrom == nil then
				splitFrom = meshAsset.sourceSplit
			end
			local startDivisions = splitFrom.divisions
			local minBounds = meshAsset.minBounds
			local maxBounds = meshAsset.maxBounds
			local newMesh = loadFromMesh(splitFrom.mesh)
			for _, axis in { "X", "Y", "Z" } do
				local startDivision = startDivisions[axis]
				local splitSize = meshSize[axis] / math.pow(2, startDivision)
				local minBound = minBounds[axis]
				local maxBound = maxBounds[axis]
				for _ = startDivision + 1, divisions[axis] do
					local newSplitSize = splitSize * 0.5
					for splitPos = minBound + newSplitSize, maxBound - newSplitSize, splitSize or 1 do
						splitMesh(newMesh, axis, splitPos)
					end
					splitSize = newSplitSize
				end
			end
			local divisionCount = divisions.X + divisions.Y + divisions.Z
			split = {
				divisions = divisions,
				divisionCount = divisionCount,
				mesh = newMesh,
				consumers = {},
				contents = {},
			}
			renderContent(meshAsset, split)
			local splitsSize = #splits
			local insertIndex = splitsSize
			for i = splitFromIndex + 1, splitsSize - 1 do
				if divisionCount <= splits[i + 1].divisionCount then
					insertIndex = i
					break
				end
			end
			local _insertIndex = insertIndex
			local _split = split
			table.insert(splits, _insertIndex + 1, _split)
		end
		local resizeEvent
		local contents = split.contents
		table.clear(consumer.meshParts)
		if #contents == 1 then
			local meshPart = createMeshPart(contents[1], consumerSize)
			consumer.instance = meshPart
			local _exp_1 = consumer.meshParts
			table.insert(_exp_1, meshPart)
			resizeEvent = meshPart:GetPropertyChangedSignal("Size"):Connect(function()
				print("hi")
			end)
		else
			local model = Instance.new("Model")
			local rootMesh
			for _, content in contents do
				local meshPart = createMeshPart(content, consumerSize)
				local _exp_1 = consumer.meshParts
				table.insert(_exp_1, meshPart)
				meshPart.Parent = model
				rootMesh = meshPart
			end
			model.PrimaryPart = rootMesh
			consumer.instance = model
			resizeEvent = rootMesh:GetPropertyChangedSignal("Size"):Connect(function()
				print("hi")
			end)
		end
		local meshConsumer = {
			consumer = consumer,
			resizeEvent = resizeEvent,
		}
		local _exp_1 = split.consumers
		table.insert(_exp_1, meshConsumer)
	end
	_container.addConsumer = addConsumer
end
local default = MeshAsset
return {
	MeshAsset = MeshAsset,
	default = default,
}
