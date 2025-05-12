--!native
-- Compiled with roblox-ts v3.0.0
local function loadFromMesh(self, mesh)
	local _arg0 = mesh.chunks == Vector3.one
	assert(_arg0)
	self.hasUVs = mesh.hasUVs
	self.hasColors = mesh.hasColors
	self.minBounds = mesh.minBounds
	self.maxBounds = mesh.maxBounds
	self.meshSize = mesh.meshSize
	self.vertices = table.clone(mesh.vertices)
	--edge: start vertex index, end vertex index
	self.edgeStartVIs = table.clone(mesh.edgeStartVIs)
	self.edgeEndVIs = table.clone(mesh.edgeEndVIs)
	self.edgeInvVecs = table.clone(mesh.edgeInvVecs)
	self.vertsCount = mesh.vertsCount
	self.edgesCount = mesh.edgesCount
	self.trisCount = mesh.trisCount
	--face corners: vertex index
	self.fc1VI = table.clone(mesh.fc1VI)
	self.fc2VI = table.clone(mesh.fc2VI)
	self.fc3VI = table.clone(mesh.fc3VI)
	--face: edge index
	self.fEI1 = table.clone(mesh.fEI1)
	self.fEI2 = table.clone(mesh.fEI2)
	self.fEI3 = table.clone(mesh.fEI3)
	--face corners: normal
	self.fc1N = table.clone(mesh.fc1N)
	self.fc2N = table.clone(mesh.fc2N)
	self.fc3N = table.clone(mesh.fc3N)
	--face corners: UV
	self.fc1UV = table.clone(mesh.fc1UV)
	self.fc2UV = table.clone(mesh.fc2UV)
	self.fc3UV = table.clone(mesh.fc3UV)
	--face corners: color and alpha
	self.fc1Col = table.clone(mesh.fc1Col)
	self.fc1CA = table.clone(mesh.fc1CA)
	self.fc2Col = table.clone(mesh.fc2Col)
	self.fc2CA = table.clone(mesh.fc2CA)
	self.fc3Col = table.clone(mesh.fc3Col)
	self.fc3CA = table.clone(mesh.fc3CA)
end
return {
	loadFromMesh = loadFromMesh,
}
