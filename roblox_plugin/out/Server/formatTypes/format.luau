--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, formatData.totalSize)
	local offset = 0
	for _, format in formatData.format do
		local _args = args
		local _arg0 = format.read(readBuffer, readOffset + offset)
		table.insert(_args, _arg0)
		offset += format.size
	end
end
local function write(sendThread, args, argsCount, formatData, masks)
	local data = buffer.create(formatData.totalSize)
	local offset = 0
	for _, format in formatData.format do
		format.write(data, offset, args[argsCount + 1])
		argsCount += 1
		offset += format.size
	end
	SendMessagesThread.writeBuffer(sendThread, data, formatData.totalSize)
	return argsCount
end
return {
	read = read,
	write = write,
}
