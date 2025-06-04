--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local DATA_SIZE = 8
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local x = buffer.readf32(readBuffer, readOffset)
	local y = buffer.readf32(readBuffer, readOffset + 4)
	local _args = args
	local _vector2 = Vector2.new(x, y)
	table.insert(_args, _vector2)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local value = args[argsCount + 1]
	local data = buffer.create(DATA_SIZE)
	buffer.writef32(data, 0, value.X)
	buffer.writef32(data, 4, value.Y)
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
