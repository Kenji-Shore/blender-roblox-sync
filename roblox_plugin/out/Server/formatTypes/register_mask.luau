--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.Parent.include.RuntimeLib)
local ProcessFormats = TS.import(script, script.Parent.Parent, "processFormats")
local SendMessagesThread = TS.import(script, script.Parent.Parent, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script.Parent.Parent, "receiveMessages").default
local function read(receiveThread, args, formatData, masks)
	local registerMasks = formatData.register_mask
	local maskCount = #registerMasks
	local countFormat = ProcessFormats.getFormatForCount(maskCount)
	local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, countFormat.size)
	local bitmask = countFormat.read(readBuffer, readOffset)
	local bools = {}
	for _ = 0, maskCount - 1 do
		local _value = (bit32.band(bitmask, 1))
		table.insert(bools, 1, not not (_value ~= 0 and _value == _value and _value))
		bitmask = bit32.arshift(bitmask, 1)
	end
	local newMasks = ProcessFormats.deepcopy(masks)
	for i = 0, maskCount - 1 do
		local _args = args
		local _arg0 = bools[i + 1]
		table.insert(_args, _arg0)
		local _arg0_1 = registerMasks[i + 1]
		local _arg1 = bools[i + 1]
		newMasks[_arg0_1] = _arg1
	end
	ReceiveMessagesThread.parse(receiveThread, args, formatData.data, newMasks)
end
local function write(sendThread, args, argsCount, formatData, masks)
	local registerMasks = formatData.register_mask
	local maskCount = #registerMasks
	local countFormat = ProcessFormats.getFormatForCount(maskCount)
	local bitmask = 0
	local newMasks = ProcessFormats.deepcopy(masks)
	for i = 0, maskCount - 1 do
		local boolValue = args[argsCount + 1]
		argsCount += 1
		bitmask = bit32.lshift(bitmask, 1)
		bitmask += if boolValue then 1 else 0
		local _arg0 = registerMasks[i + 1]
		newMasks[_arg0] = boolValue
	end
	local data = buffer.create(countFormat.size)
	countFormat.write(data, 0, bitmask)
	SendMessagesThread.writeBuffer(sendThread, data, countFormat.size)
	return SendMessagesThread.parse(sendThread, args, argsCount, formatData.data, newMasks)
end
return {
	read = read,
	write = write,
}
