--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local DATA_SIZE = 3
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local r = buffer.readu8(readBuffer, readOffset) / 255
	local g = buffer.readu8(readBuffer, readOffset + 1) / 255
	local b = buffer.readu8(readBuffer, readOffset + 2) / 255
	local _args = args
	local _color3 = Color3.new(r, g, b)
	table.insert(_args, _color3)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local value = args[argsCount + 1]
	local data = buffer.create(DATA_SIZE)
	buffer.writeu8(data, 0, math.round(255 * value.R))
	buffer.writeu8(data, 1, math.round(255 * value.G))
	buffer.writeu8(data, 2, math.round(255 * value.B))
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
