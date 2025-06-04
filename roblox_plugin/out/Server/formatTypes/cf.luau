--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local YAW = 32767
local INV_YAW = 1 / YAW
local DATA_SIZE = 32
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local x = buffer.readf64(readBuffer, readOffset)
	local y = buffer.readf64(readBuffer, readOffset + 8)
	local z = buffer.readf64(readBuffer, readOffset + 16)
	local qX = buffer.readi16(readBuffer, readOffset + 24) * INV_YAW
	local qY = buffer.readi16(readBuffer, readOffset + 26) * INV_YAW
	local qZ = buffer.readi16(readBuffer, readOffset + 28) * INV_YAW
	local qW = buffer.readi16(readBuffer, readOffset + 30) * INV_YAW
	local _args = args
	local _cFrame = CFrame.new(x, y, z, qX, qY, qZ, qW)
	table.insert(_args, _cFrame)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local value = args[argsCount + 1]
	local data = buffer.create(DATA_SIZE)
	buffer.writef64(data, 0, value.X)
	buffer.writef64(data, 8, value.Y)
	buffer.writef64(data, 16, value.Z)
	local axis, angle = value.Rotation:ToAxisAngle()
	local cos = math.cos(angle / 2)
	local sin = math.sin(angle / 2)
	buffer.writei16(data, 24, math.round(axis.X * sin * YAW))
	buffer.writei16(data, 26, math.round(axis.Y * sin * YAW))
	buffer.writei16(data, 28, math.round(axis.Z * sin * YAW))
	buffer.writei16(data, 30, math.round(cos * YAW))
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
