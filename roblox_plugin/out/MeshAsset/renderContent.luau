--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.include.RuntimeLib)
local AssetService = TS.import(script, script.Parent.Parent, "include", "node_modules", "@rbxts", "services").AssetService
local function renderContent(meshAsset, split)
	local divisions = split.divisions
	local chunks = Vector3.new(math.pow(2, divisions.X), math.pow(2, divisions.Y), math.pow(2, divisions.Z))
	local editableRawMeshes = {}
	local vertsMaps = {}
	local faceCounts = {}
	for x = 0, chunks.X - 1 do
		for y = 0, chunks.Y - 1 do
			for z = 0, chunks.Z - 1 do
				local chunk = Vector3.new(x, y, z)
				local _arg1 = AssetService:CreateEditableMesh()
				editableRawMeshes[chunk] = _arg1
				vertsMaps[chunk] = {}
				faceCounts[chunk] = 0
			end
		end
	end
	local chunkSize = meshAsset.meshSize / chunks
	local _one = Vector3.one
	local maxChunk = chunks - _one
	local minBounds = meshAsset.minBounds
	local mesh = split.mesh
	local vertices = mesh.vertices
	local fc1VI = mesh.fc1VI
	local fc2VI = mesh.fc2VI
	local fc3VI = mesh.fc3VI
	local fc1N = mesh.fc1N
	local fc2N = mesh.fc2N
	local fc3N = mesh.fc3N
	local fc1UV = mesh.fc1UV
	local fc2UV = mesh.fc2UV
	local fc3UV = mesh.fc3UV
	local fc1Col = mesh.fc1Col
	local fc1CA = mesh.fc1CA
	local fc2Col = mesh.fc2Col
	local fc2CA = mesh.fc2CA
	local fc3Col = mesh.fc3Col
	local fc3CA = mesh.fc3CA
	for i = 0, mesh.trisCount - 1 do
		local vi1 = fc1VI[i + 1]
		local vi2 = fc2VI[i + 1]
		local vi3 = fc3VI[i + 1]
		local v1 = vertices[vi1 + 1]
		local v2 = vertices[vi2 + 1]
		local v3 = vertices[vi3 + 1]
		local centroid = (v1 + v2 + v3) * 0.3333
		local chunk = ((centroid - minBounds) // chunkSize):Max(Vector3.zero):Min(maxChunk)
		local editableRawMesh = editableRawMeshes[chunk]
		local vertsMap = vertsMaps[chunk]
		local _condition = vertsMap[vi1]
		if _condition == nil then
			_condition = editableRawMesh:AddVertex(v1)
		end
		local cvi1 = _condition
		local _condition_1 = vertsMap[vi2]
		if _condition_1 == nil then
			_condition_1 = editableRawMesh:AddVertex(v2)
		end
		local cvi2 = _condition_1
		local _condition_2 = vertsMap[vi3]
		if _condition_2 == nil then
			_condition_2 = editableRawMesh:AddVertex(v3)
		end
		local cvi3 = _condition_2
		vertsMap[vi1] = cvi1
		vertsMap[vi2] = cvi2
		vertsMap[vi3] = cvi3
		local faceId = editableRawMesh:AddTriangle(cvi1, cvi2, cvi3)
		local _arg1 = faceCounts[chunk] + 1
		faceCounts[chunk] = _arg1
		editableRawMesh:SetFaceNormals(faceId, { editableRawMesh:AddNormal(fc1N[i + 1]), editableRawMesh:AddNormal(fc2N[i + 1]), editableRawMesh:AddNormal(fc3N[i + 1]) })
		if mesh.hasUVs then
			editableRawMesh:SetFaceUVs(faceId, { editableRawMesh:AddUV(fc1UV[i + 1]), editableRawMesh:AddUV(fc2UV[i + 1]), editableRawMesh:AddUV(fc3UV[i + 1]) })
		end
		if mesh.hasColors then
			editableRawMesh:SetFaceColors(faceId, { editableRawMesh:AddColor(fc1Col[i + 1], fc1CA[i + 1]), editableRawMesh:AddColor(fc2Col[i + 1], fc2CA[i + 1]), editableRawMesh:AddColor(fc3Col[i + 1], fc3CA[i + 1]) })
		end
	end
	local contents = split.contents
	for chunk, editableRawMesh in editableRawMeshes do
		if faceCounts[chunk] > 0 then
			local _arg0 = Content.fromObject(editableRawMesh)
			table.insert(contents, _arg0)
		end
	end
end
return {
	renderContent = renderContent,
}
