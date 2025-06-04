-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.include.RuntimeLib)
local ProcessFormats = TS.import(script, script.Parent, "processFormats")
local PauseThread = TS.import(script, script.Parent, "pauseThread").default
local SendMessagesThread = {}
do
	local _container = SendMessagesThread
	local function sendMessage(sendThread, messageName, ...)
		local args = { ... }
		local _arg0 = ProcessFormats.sendMessageIds[messageName] ~= nil
		assert(_arg0)
		local _sendMessageIds = ProcessFormats.sendMessageIds
		local _messageName = messageName
		local messageId = _sendMessageIds[_messageName]
		table.insert(args, 1, messageId)
		local _argsQueued = sendThread.argsQueued
		local _args = args
		table.insert(_argsQueued, _args)
		PauseThread.unpause(sendThread)
	end
	_container.sendMessage = sendMessage
	local function writeBuffer(sendThread, data, dataSize)
		sendThread.bufLen += dataSize
		if sendThread.bufLen <= ProcessFormats.SEND_LIMIT then
			local _buffer = sendThread.buffer
			local _data = data
			table.insert(_buffer, _data)
		else
			local overflow = sendThread.bufLen - ProcessFormats.SEND_LIMIT
			local joinedBuffer = buffer.create(ProcessFormats.SEND_LIMIT)
			local offset = 0
			for _, segment in sendThread.buffer do
				buffer.copy(joinedBuffer, offset, segment)
				offset += buffer.len(segment)
			end
			buffer.copy(joinedBuffer, offset, data, 0, dataSize - overflow)
			local _exp = sendThread.buffersQueued
			table.insert(_exp, joinedBuffer)
			table.clear(sendThread.buffer)
			local overflowSegment = buffer.create(overflow)
			buffer.copy(overflowSegment, 0, data, dataSize - overflow)
			local _exp_1 = sendThread.buffer
			table.insert(_exp_1, overflowSegment)
			sendThread.bufLen = overflow
		end
	end
	_container.writeBuffer = writeBuffer
	local function parse(sendThread, args, argsCount, formatData, masks)
		if not (formatData.type ~= nil) then
			for _, subFormatData in formatData do
				argsCount = parse(sendThread, args, argsCount, subFormatData, masks)
			end
		else
			local _writeFuncs = ProcessFormats.writeFuncs
			local _type = formatData.type
			argsCount = _writeFuncs[_type](sendThread, args, argsCount, formatData, masks)
		end
		return argsCount
	end
	_container.parse = parse
	local function create()
		local sendThread = {
			buffer = {},
			bufLen = 0,
			buffersQueued = {},
			argsQueued = {},
			stopThread = false,
		}
		task.spawn(function()
			while not sendThread.stopThread do
				if #sendThread.argsQueued == 0 then
					PauseThread.pause(sendThread)
				end
				local args = table.remove(sendThread.argsQueued, 1)
				local messageId = args[1]
				local format = ProcessFormats.messageIdFormat
				local data = buffer.create(format.size)
				format.write(data, 0, messageId)
				writeBuffer(sendThread, data, format.size)
				local masks = {}
				parse(sendThread, args, 1, ProcessFormats.messageFormats[messageId + 1], masks)
				local joinedBuffer = buffer.create(sendThread.bufLen)
				local offset = 0
				for _, segment in sendThread.buffer do
					buffer.copy(joinedBuffer, offset, segment)
					offset += buffer.len(segment)
				end
				local _exp = sendThread.buffersQueued
				table.insert(_exp, joinedBuffer)
				table.clear(sendThread.buffer)
				sendThread.bufLen = 0
			end
		end)
		return sendThread
	end
	_container.create = create
end
local default = SendMessagesThread
return {
	SendMessagesThread = SendMessagesThread,
	default = default,
}
