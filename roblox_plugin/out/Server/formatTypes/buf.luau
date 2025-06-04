--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, 4)
	local bufLen = buffer.readu32(readBuffer, readOffset)
	local readBuffer2, readOffset2 = ReceiveMessagesThread.readBuffer(receiveThread, bufLen)
	local bufferValue = buffer.create(bufLen)
	buffer.copy(bufferValue, 0, readBuffer2, readOffset2, bufLen)
	table.insert(args, bufferValue)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local value = args[argsCount + 1]
	local bufLen = buffer.len(value)
	local data = buffer.create(4 + bufLen)
	buffer.writeu32(data, 0, bufLen)
	buffer.copy(data, 4, value)
	SendMessagesThread.writeBuffer(sendThread, data, 4 + bufLen)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
