--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local DATA_SIZE = 32
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local hashValue = buffer.readstring(readBuffer, readOffset, DATA_SIZE)
	table.insert(args, hashValue)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local hashValue = args[argsCount + 1]
	local data = buffer.fromstring(hashValue)
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
