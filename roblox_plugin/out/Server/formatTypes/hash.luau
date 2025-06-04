--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local DATA_SIZE = 8
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local _args = args
	local _arg0 = buffer.readstring(readBuffer, readOffset, DATA_SIZE)
	table.insert(_args, _arg0)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local value = args[argsCount + 1]
	local data = buffer.create(DATA_SIZE)
	buffer.writestring(data, 0, value, DATA_SIZE)
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
