--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local ProcessFormats = TS.import(script, script.Parent.Parent, "processFormats")
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local DATA_SIZE = 4
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local dictSize = buffer.readu32(readBuffer, readOffset)
	local dict = {}
	for _ = 1, dictSize do
		local k = {}
		local v = {}
		ReceiveMessagesThread.parse(receiveThread, k, formatData.index, masks)
		ReceiveMessagesThread.parse(receiveThread, v, formatData.value, masks)
		local _arg0 = k[1]
		local _arg1 = if #v > 1 then v else v[1]
		dict[_arg0] = _arg1
	end
	table.insert(args, dict)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local dict = args[argsCount + 1]
	-- ▼ ReadonlyMap.size ▼
	local _size = 0
	for _ in dict do
		_size += 1
	end
	-- ▲ ReadonlyMap.size ▲
	local dictSize = _size
	local data = buffer.create(DATA_SIZE)
	buffer.writeu32(data, 0, dictSize)
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	if dictSize > 0 then
		local _, testValue = next(dict)
		if type(testValue) == "table" then
			for k, v in dict do
				SendMessagesThread.parse(sendThread, { k }, 0, formatData.index, masks)
				SendMessagesThread.parse(sendThread, v, 0, formatData.value, masks)
			end
		else
			for k, v in dict do
				SendMessagesThread.parse(sendThread, { k }, 0, formatData.index, masks)
				SendMessagesThread.parse(sendThread, { v }, 0, formatData.value, masks)
			end
		end
	end
	return argsCount + 1
end
return {
	read = read,
	write = write,
}
