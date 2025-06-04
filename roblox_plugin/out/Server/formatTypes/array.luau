--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local ProcessFormats = TS.import(script, script.Parent.Parent, "processFormats")
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local DATA_SIZE = 4
local function read(receiveThread, args, formatData, masks)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE)
	local arraySize = buffer.readu32(readBuffer, readOffset)
	local array = table.create(arraySize)
	for i = 0, arraySize - 1 do
		local v = {}
		ReceiveMessagesThread.parse(receiveThread, v, formatData.value, masks)
		array[i + 1] = if #v > 1 then v else v[1]
	end
	table.insert(args, array)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local array = args[argsCount + 1]
	local arraySize = #array
	local data = buffer.create(DATA_SIZE)
	buffer.writeu32(data, 0, arraySize)
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE)
	if arraySize > 0 then
		local _arg0 = array[1]
		if type(_arg0) == "table" then
			for _, v in array do
				SendMessagesThread.parse(sendThread, v, 0, formatData.value, masks)
			end
		else
			for _, v in array do
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
