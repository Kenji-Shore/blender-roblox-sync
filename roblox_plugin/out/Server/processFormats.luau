-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.include.RuntimeLib)
local messageFormatsFile = TS.import(script, script.Parent, "message_formats")
local DATATYPES = {
	u8 = 1,
	i8 = 1,
	u16 = 2,
	i16 = 2,
	u32 = 4,
	i32 = 4,
	f32 = 4,
	f64 = 8,
}
local function getFormatForCount(count)
	return ({ {
		size = 1,
		read = buffer.readu8,
		write = buffer.writeu8,
	}, {
		size = 2,
		read = buffer.readu16,
		write = buffer.writeu16,
	}, {
		size = 4,
		read = buffer.readu32,
		write = buffer.writeu32,
	} })[math.min(math.ceil(math.log(2 * math.max(math.log(count, 256), 1), 2)) - 1, 2) + 1]
end
local function transformFormat(rawFormatData, requiredType)
	local _condition = not requiredType
	if not _condition then
		local _rawFormatData = rawFormatData
		local _requiredType = requiredType
		_condition = typeof(_rawFormatData) == _requiredType
	end
	assert(_condition)
	local _rawFormatData = rawFormatData
	if type(_rawFormatData) == "table" then
		if rawFormatData.value ~= nil then
			--is array or dict
			local value = transformFormat(rawFormatData.value)
			if rawFormatData.index ~= nil then
				return {
					type = "dict",
					index = transformFormat(rawFormatData.index, "string"),
					value = value,
				}
			else
				return {
					type = "array",
					value = value,
				}
			end
		elseif rawFormatData.data ~= nil then
			local data = transformFormat(rawFormatData.data)
			if rawFormatData.mask ~= nil then
				return {
					type = "mask",
					mask = rawFormatData.mask,
					invert = rawFormatData.invert,
					data = data,
				}
			elseif rawFormatData["repeat"] ~= nil then
				return {
					type = "repeat",
					["repeat"] = rawFormatData["repeat"],
					data = data,
				}
			elseif rawFormatData.register_mask ~= nil then
				local raw_register_mask = rawFormatData.register_mask
				local register_mask = if type(raw_register_mask) == "table" then raw_register_mask else { raw_register_mask }
				return {
					type = "register_mask",
					register_mask = register_mask,
					count_format = getFormatForCount(#register_mask),
					data = data,
				}
			end
		end
	end
	local _rawFormatData_1 = rawFormatData
	if not (type(_rawFormatData_1) == "table") then
		rawFormatData = { rawFormatData }
	end
	local formatData = {}
	local mergeFormats = {}
	local totalSize = 0
	local function writeFormat()
		if #mergeFormats > 0 then
			local _arg0 = {
				type = "format",
				totalSize = totalSize,
				format = mergeFormats,
			}
			table.insert(formatData, _arg0)
			mergeFormats = {}
			totalSize = 0
		end
	end
	for _, raw in rawFormatData do
		local isStr = type(raw) == "string"
		if isStr and DATATYPES[raw] ~= nil then
			local size = DATATYPES[raw]
			totalSize += size
			local _mergeFormats = mergeFormats
			local _arg0 = {
				size = size,
				read = buffer[`read{raw}`],
				write = buffer[`write{raw}`],
			}
			table.insert(_mergeFormats, _arg0)
		else
			writeFormat()
			if isStr then
				local _arg0 = {
					type = raw,
				}
				table.insert(formatData, _arg0)
			else
				local _arg0 = transformFormat(raw)
				table.insert(formatData, _arg0)
			end
		end
	end
	writeFormat()
	if #formatData == 1 then
		return formatData[1]
	else
		return formatData
	end
end
local messageListeners = {}
local function listenMessage(messageId, callback)
	local _exp = messageListeners[messageId]
	local _callback = callback
	table.insert(_exp, _callback)
end
local function unlistenMessage(messageId, callback)
	local _exp = messageListeners[messageId]
	local _exp_1 = messageListeners[messageId]
	local _callback = callback
	local _arg0 = (table.find(_exp_1, _callback) or 0) - 1
	table.remove(_exp, _arg0 + 1)
end
local rawMessages = messageFormatsFile.messages
local totalMessages = #rawMessages
local sendMessageIds = {}
local receiveMessageIds = {}
local messageFormats = {}
local SEND_LIMIT = 20000000
local messageIdFormat = getFormatForCount(totalMessages)
for i = 0, totalMessages - 1 do
	local rawMessage = rawMessages[i + 1]
	local messageName = rawMessage.name
	if rawMessage.sender == "luau" then
		sendMessageIds[messageName] = i
	else
		receiveMessageIds[messageName] = i
		messageListeners[i] = {}
	end
	local _arg0 = transformFormat(rawMessage.data)
	table.insert(messageFormats, _arg0)
end
local function deepcopy(object)
	local _object = object
	if type(_object) == "table" then
		local copyObject = {}
		for k, v in object do
			local _arg1 = deepcopy(v)
			copyObject[k] = _arg1
		end
		return copyObject
	else
		return object
	end
end
local readFuncs = {}
local writeFuncs = {}
local function initialize()
	for _, moduleScript in script.Parent:FindFirstChild("formatTypes"):GetChildren() do
		if moduleScript.ClassName == "ModuleScript" then
			local moduleName = moduleScript.Name
			local module = require(moduleScript)
			local _read = module.read
			readFuncs[moduleName] = _read
			local _write = module.write
			writeFuncs[moduleName] = _write
		end
	end
end
return {
	getFormatForCount = getFormatForCount,
	listenMessage = listenMessage,
	unlistenMessage = unlistenMessage,
	deepcopy = deepcopy,
	initialize = initialize,
	messageListeners = messageListeners,
	sendMessageIds = sendMessageIds,
	receiveMessageIds = receiveMessageIds,
	messageFormats = messageFormats,
	SEND_LIMIT = SEND_LIMIT,
	messageIdFormat = messageIdFormat,
	readFuncs = readFuncs,
	writeFuncs = writeFuncs,
}
