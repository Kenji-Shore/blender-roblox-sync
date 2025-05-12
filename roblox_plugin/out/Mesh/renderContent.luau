--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.include.RuntimeLib)
local AssetService = TS.import(script, script.Parent.Parent, "include", "node_modules", "@rbxts", "services").AssetService
local function renderContent(self)
	local chunks = self.chunks
	local editableMeshes = {}
	local vertsMaps = {}
	local faceCounts = {}
	for x = 0, chunks.X - 1 do
		for y = 0, chunks.Y - 1 do
			for z = 0, chunks.Z - 1 do
				local chunk = Vector3.new(x, y, z)
				local _arg1 = AssetService:CreateEditableMesh()
				editableMeshes[chunk] = _arg1
				vertsMaps[chunk] = {}
				faceCounts[chunk] = 0
			end
		end
	end
	local chunkSize = self.meshSize / chunks
	local _one = Vector3.one
	local maxChunk = chunks - _one
	local minBounds = self.minBounds
	local vertices = self.vertices
	local fc1VI = self.fc1VI
	local fc2VI = self.fc2VI
	local fc3VI = self.fc3VI
	local fc1N = self.fc1N
	local fc2N = self.fc2N
	local fc3N = self.fc3N
	local fc1UV = self.fc1UV
	local fc2UV = self.fc2UV
	local fc3UV = self.fc3UV
	local fc1Col = self.fc1Col
	local fc1CA = self.fc1CA
	local fc2Col = self.fc2Col
	local fc2CA = self.fc2CA
	local fc3Col = self.fc3Col
	local fc3CA = self.fc3CA
	for i = 0, self.trisCount - 1 do
		local vi1 = fc1VI[i + 1]
		local vi2 = fc2VI[i + 1]
		local vi3 = fc3VI[i + 1]
		local v1 = vertices[vi1 + 1]
		local v2 = vertices[vi2 + 1]
		local v3 = vertices[vi3 + 1]
		local centroid = (v1 + v2 + v3) * 0.3333
		local chunk = ((centroid - minBounds) // chunkSize):Max(Vector3.zero):Min(maxChunk)
		local editableMesh = editableMeshes[chunk]
		local vertsMap = vertsMaps[chunk]
		local _condition = vertsMap[vi1]
		if _condition == nil then
			_condition = editableMesh:AddVertex(v1)
		end
		local cvi1 = _condition
		local _condition_1 = vertsMap[vi2]
		if _condition_1 == nil then
			_condition_1 = editableMesh:AddVertex(v2)
		end
		local cvi2 = _condition_1
		local _condition_2 = vertsMap[vi3]
		if _condition_2 == nil then
			_condition_2 = editableMesh:AddVertex(v3)
		end
		local cvi3 = _condition_2
		vertsMap[vi1] = cvi1
		vertsMap[vi2] = cvi2
		vertsMap[vi3] = cvi3
		local faceId = editableMesh:AddTriangle(cvi1, cvi2, cvi3)
		local _arg1 = faceCounts[chunk] + 1
		faceCounts[chunk] = _arg1
		editableMesh:SetFaceNormals(faceId, { editableMesh:AddNormal(fc1N[i + 1]), editableMesh:AddNormal(fc2N[i + 1]), editableMesh:AddNormal(fc3N[i + 1]) })
		if self.hasUVs then
			editableMesh:SetFaceUVs(faceId, { editableMesh:AddUV(fc1UV[i + 1]), editableMesh:AddUV(fc2UV[i + 1]), editableMesh:AddUV(fc3UV[i + 1]) })
		end
		if self.hasColors then
			editableMesh:SetFaceColors(faceId, { editableMesh:AddColor(fc1Col[i + 1], fc1CA[i + 1]), editableMesh:AddColor(fc2Col[i + 1], fc2CA[i + 1]), editableMesh:AddColor(fc3Col[i + 1], fc3CA[i + 1]) })
		end
	end
	local contents = {}
	self.contents = contents
	for chunk, editableMesh in editableMeshes do
		if faceCounts[chunk] > 0 then
			local _arg0 = Content.fromObject(editableMesh)
			table.insert(contents, _arg0)
		end
	end
end
return {
	renderContent = renderContent,
}
