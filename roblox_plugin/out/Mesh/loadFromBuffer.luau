--!native
-- Compiled with roblox-ts v3.0.0
local INV_NORMAL = 1 / 127
local INV_COLOR = 1 / 255
local function loadFromBuffer(self, meshBuffer)
	local offset = 0
	local flags = buffer.readu8(meshBuffer, offset)
	offset += 1
	local _value = (bit32.band(flags, 1))
	local hasColors = not not (_value ~= 0 and _value == _value and _value)
	flags = bit32.arshift(flags, 1)
	local _value_1 = (bit32.band(flags, 1))
	local hasUVs = not not (_value_1 ~= 0 and _value_1 == _value_1 and _value_1)
	self.hasUVs = hasUVs
	self.hasColors = hasColors
	local minX = math.huge
	local maxX = -math.huge
	local minY = math.huge
	local maxY = -math.huge
	local minZ = math.huge
	local maxZ = -math.huge
	local vertices = {}
	self.vertices = vertices
	local edgesCount = 0
	local edgeMap = {}
	local edgeStartVIs = {}
	local edgeEndVIs = {}
	local edgeInvVecs = {}
	self.edgeStartVIs = edgeStartVIs
	self.edgeEndVIs = edgeEndVIs
	self.edgeInvVecs = edgeInvVecs
	local fc1VI = {}
	local fc2VI = {}
	local fc3VI = {}
	self.fc1VI = fc1VI
	self.fc2VI = fc2VI
	self.fc3VI = fc3VI
	local fEI1 = {}
	local fEI2 = {}
	local fEI3 = {}
	self.fEI1 = fEI1
	self.fEI2 = fEI2
	self.fEI3 = fEI3
	local fc1N = {}
	local fc2N = {}
	local fc3N = {}
	self.fc1N = fc1N
	self.fc2N = fc2N
	self.fc3N = fc3N
	local fc1UV = {}
	local fc2UV = {}
	local fc3UV = {}
	self.fc1UV = fc1UV
	self.fc2UV = fc2UV
	self.fc3UV = fc3UV
	local fc1Col = {}
	local fc1CA = {}
	local fc2Col = {}
	local fc2CA = {}
	local fc3Col = {}
	local fc3CA = {}
	self.fc1Col = fc1Col
	self.fc1CA = fc1CA
	self.fc2Col = fc2Col
	self.fc2CA = fc2CA
	self.fc3Col = fc3Col
	self.fc3CA = fc3CA
	local vertsCount = buffer.readu16(meshBuffer, offset)
	self.vertsCount = vertsCount
	offset += 2
	for i = 0, vertsCount - 1 do
		local x = buffer.readf32(meshBuffer, offset + 4)
		local y = buffer.readf32(meshBuffer, offset + 8)
		local z = buffer.readf32(meshBuffer, offset)
		offset += 12
		minX = math.min(minX, x)
		maxX = math.max(maxX, x)
		minY = math.min(minY, y)
		maxY = math.max(maxY, y)
		minZ = math.min(minZ, z)
		maxZ = math.max(maxZ, z)
		vertices[i + 1] = Vector3.new(x, y, z)
	end
	self.minBounds = Vector3.new(minX, minY, minZ)
	self.maxBounds = Vector3.new(maxX, maxY, maxZ)
	local _maxBounds = self.maxBounds
	local _minBounds = self.minBounds
	self.meshSize = _maxBounds - _minBounds
	local trisCount = buffer.readu16(meshBuffer, offset)
	self.trisCount = trisCount
	offset += 2
	for _ = 0, trisCount - 1 do
		local vi1 = buffer.readu16(meshBuffer, offset)
		local vi2 = buffer.readu16(meshBuffer, offset + 2)
		local vi3 = buffer.readu16(meshBuffer, offset + 4)
		offset += 6
		local eh1 = Vector3.new(math.min(vi1, vi2), math.max(vi1, vi2))
		local eh2 = Vector3.new(math.min(vi1, vi3), math.max(vi1, vi3))
		local eh3 = Vector3.new(math.min(vi2, vi3), math.max(vi2, vi3))
		local ei1 = edgeMap[eh1]
		local ei2 = edgeMap[eh2]
		local ei3 = edgeMap[eh3]
		if ei1 == nil then
			ei1 = edgesCount
			local _ei1 = ei1
			edgeMap[eh1] = _ei1
			table.insert(edgeStartVIs, vi1)
			table.insert(edgeEndVIs, vi2)
			local _one = Vector3.one
			local _exp = vertices[vi1 + 1]
			local _arg0 = vertices[vi2 + 1]
			table.insert(edgeInvVecs, _one / (_exp - _arg0))
			edgesCount += 1
		end
		if ei2 == nil then
			ei2 = edgesCount
			local _ei2 = ei2
			edgeMap[eh2] = _ei2
			table.insert(edgeStartVIs, vi1)
			table.insert(edgeEndVIs, vi3)
			local _one = Vector3.one
			local _exp = vertices[vi1 + 1]
			local _arg0 = vertices[vi3 + 1]
			table.insert(edgeInvVecs, _one / (_exp - _arg0))
			edgesCount += 1
		end
		if ei3 == nil then
			ei3 = edgesCount
			local _ei3 = ei3
			edgeMap[eh3] = _ei3
			table.insert(edgeStartVIs, vi2)
			table.insert(edgeEndVIs, vi3)
			local _one = Vector3.one
			local _exp = vertices[vi2 + 1]
			local _arg0 = vertices[vi3 + 1]
			table.insert(edgeInvVecs, _one / (_exp - _arg0))
			edgesCount += 1
		end
		table.insert(fc1VI, vi1)
		table.insert(fc2VI, vi2)
		table.insert(fc3VI, vi3)
		local _ei1 = ei1
		table.insert(fEI1, _ei1)
		local _ei2 = ei2
		table.insert(fEI2, _ei2)
		local _ei3 = ei3
		table.insert(fEI3, _ei3)
	end
	self.edgesCount = edgesCount
	for _ = 0, trisCount - 1 do
		local _arg0 = Vector3.new(buffer.readi8(meshBuffer, offset + 1), buffer.readi8(meshBuffer, offset + 2), buffer.readi8(meshBuffer, offset)) * INV_NORMAL
		table.insert(fc1N, _arg0)
		local _arg0_1 = Vector3.new(buffer.readi8(meshBuffer, offset + 4), buffer.readi8(meshBuffer, offset + 5), buffer.readi8(meshBuffer, offset + 3)) * INV_NORMAL
		table.insert(fc2N, _arg0_1)
		local _arg0_2 = Vector3.new(buffer.readi8(meshBuffer, offset + 7), buffer.readi8(meshBuffer, offset + 8), buffer.readi8(meshBuffer, offset + 6)) * INV_NORMAL
		table.insert(fc3N, _arg0_2)
		offset += 9
	end
	if hasUVs then
		for _ = 0, trisCount - 1 do
			local _vector2 = Vector2.new(buffer.readf32(meshBuffer, offset), buffer.readf32(meshBuffer, offset + 4))
			table.insert(fc1UV, _vector2)
			local _vector2_1 = Vector2.new(buffer.readf32(meshBuffer, offset + 8), buffer.readf32(meshBuffer, offset + 12))
			table.insert(fc2UV, _vector2_1)
			local _vector2_2 = Vector2.new(buffer.readf32(meshBuffer, offset + 16), buffer.readf32(meshBuffer, offset + 20))
			table.insert(fc3UV, _vector2_2)
			offset += 24
		end
	end
	if hasColors then
		for _ = 0, trisCount - 1 do
			local _arg0 = Color3.fromRGB(buffer.readu8(meshBuffer, offset + 0), buffer.readu8(meshBuffer, offset + 1), buffer.readu8(meshBuffer, offset + 2))
			table.insert(fc1Col, _arg0)
			local _arg0_1 = buffer.readu8(meshBuffer, offset + 3) * INV_COLOR
			table.insert(fc1CA, _arg0_1)
			local _arg0_2 = Color3.fromRGB(buffer.readu8(meshBuffer, offset + 4), buffer.readu8(meshBuffer, offset + 5), buffer.readu8(meshBuffer, offset + 6))
			table.insert(fc2Col, _arg0_2)
			local _arg0_3 = buffer.readu8(meshBuffer, offset + 7) * INV_COLOR
			table.insert(fc2CA, _arg0_3)
			local _arg0_4 = Color3.fromRGB(buffer.readu8(meshBuffer, offset + 8), buffer.readu8(meshBuffer, offset + 9), buffer.readu8(meshBuffer, offset + 10))
			table.insert(fc3Col, _arg0_4)
			local _arg0_5 = buffer.readu8(meshBuffer, offset + 11) * INV_COLOR
			table.insert(fc3CA, _arg0_5)
			offset += 12
		end
	end
end
return {
	loadFromBuffer = loadFromBuffer,
}
