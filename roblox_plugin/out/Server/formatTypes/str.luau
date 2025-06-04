--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, 2)
	local strLen = buffer.readu16(readBuffer, readOffset)
	local readBuffer2, readOffset2 = ReceiveMessagesThread.readBuffer(receiveThread, strLen)
	local _args = args
	local _arg0 = buffer.readstring(readBuffer2, readOffset2, strLen)
	table.insert(_args, _arg0)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local value = args[argsCount + 1]
	local strLen = #value
	local data = buffer.create(2 + strLen)
	buffer.writeu16(data, 0, strLen)
	buffer.writestring(data, 2, value, strLen)
	SendMessagesThread.writeBuffer(sendThread, data, 2 + strLen)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
