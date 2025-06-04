--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local YAW = 32767 / math.pi
local INV_YAW = 1 / YAW
local PITCH = 32767 / (0.5 * math.pi)
local INV_PITCH = 1 / PITCH
local DATA_SIZE = 4
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local normalYaw = buffer.readi16(readBuffer, readOffset) * INV_YAW
	local normalPitch = buffer.readi16(readBuffer, readOffset + 2) * INV_PITCH
	local horizontal = math.cos(normalPitch)
	local _args = args
	local _vector3 = Vector3.new(math.cos(normalYaw) * horizontal, math.sin(normalPitch), math.sin(normalYaw) * horizontal)
	table.insert(_args, _vector3)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local value = args[argsCount + 1]
	local velMag = value.Magnitude
	local unitVel = if velMag ~= 0 then value / velMag else Vector3.xAxis
	local normalYaw = math.atan2(unitVel.Z, unitVel.X)
	local normalPitch = math.asin(unitVel.Y)
	local data = buffer.create(DATA_SIZE)
	buffer.writei16(data, 0, math.round(normalYaw * YAW))
	buffer.writei16(data, 2, math.round(normalPitch * PITCH))
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
