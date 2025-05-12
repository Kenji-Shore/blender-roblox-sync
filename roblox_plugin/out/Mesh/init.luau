--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.include.RuntimeLib)
local loadFromBuffer = TS.import(script, script, "loadFromBuffer").loadFromBuffer
local loadFromMesh = TS.import(script, script, "loadFromMesh").loadFromMesh
local renderContent = TS.import(script, script, "renderContent").renderContent
local splitMesh = TS.import(script, script, "splitMesh").splitMesh
local Mesh
do
	Mesh = setmetatable({}, {
		__tostring = function()
			return "Mesh"
		end,
	})
	Mesh.__index = Mesh
	function Mesh.new(...)
		local self = setmetatable({}, Mesh)
		return self:constructor(...) or self
	end
	function Mesh:constructor(bufferOrMesh, chunks)
		self.loadFromBuffer = loadFromBuffer
		self.loadFromMesh = loadFromMesh
		self.renderContent = renderContent
		self.splitMesh = splitMesh
		local _bufferOrMesh = bufferOrMesh
		if type(_bufferOrMesh) == "buffer" then
			self.chunks = Vector3.one
			self:loadFromBuffer(bufferOrMesh)
		else
			self.chunks = chunks
			self:loadFromMesh(bufferOrMesh)
			self.edgeSplitEIs = {}
			self.edgeSplitAlphas = {}
			self.edgeSplitVIs = {}
			for _, axis in { "X", "Y", "Z" } do
				local chunkCount = chunks[axis]
				local splitIncrement = 1 / chunkCount
				local splitPoint = splitIncrement
				for _ = 2, chunkCount do
					self:splitMesh(axis, splitPoint)
					splitPoint += splitIncrement
				end
			end
		end
	end
end
return {
	Mesh = Mesh,
}
