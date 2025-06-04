-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.include.RuntimeLib)
local ProcessFormats = TS.import(script, script.Parent, "processFormats")
local PauseThread = TS.import(script, script.Parent, "pauseThread").default
local ReceiveMessagesThread
local ReceiveMessagesThread = {}
do
	local _container = ReceiveMessagesThread
	local function receiveMessage(receiveThread, newBuffer)
		local _buffersQueued = receiveThread.buffersQueued
		local _newBuffer = newBuffer
		table.insert(_buffersQueued, _newBuffer)
		PauseThread.unpause(receiveThread)
	end
	_container.receiveMessage = receiveMessage
	local function readBuffer(receiveThread, dataSize)
		local readBuffer = receiveThread.buffer
		local readBufferSize = buffer.len(readBuffer)
		local readOffset = receiveThread.offset
		while receiveThread.bufLen < receiveThread.offset + dataSize do
			if #receiveThread.buffersQueued == 0 then
				PauseThread.pause(receiveThread)
			end
			receiveThread.buffer = table.remove(receiveThread.buffersQueued, 1)
			receiveThread.offset -= receiveThread.bufLen
			receiveThread.bufLen = buffer.len(receiveThread.buffer)
			local newReadBufferSize = readBufferSize + receiveThread.bufLen
			local newReadBuffer = buffer.create(newReadBufferSize)
			buffer.copy(newReadBuffer, 0, readBuffer)
			buffer.copy(newReadBuffer, readBufferSize, receiveThread.buffer)
			readBuffer = newReadBuffer
			readBufferSize = newReadBufferSize
		end
		receiveThread.offset += dataSize
		return readBuffer, readOffset
	end
	_container.readBuffer = readBuffer
	local function parse(receiveThread, args, formatData, masks)
		if not (formatData.type ~= nil) then
			for _, subFormatData in formatData do
				parse(receiveThread, args, subFormatData, masks)
			end
		else
			local _readFuncs = ProcessFormats.readFuncs
			local _type = formatData.type
			_readFuncs[_type](receiveThread, args, formatData, masks)
		end
	end
	_container.parse = parse
	local function create()
		local receiveThread = {
			buffer = buffer.create(0),
			bufLen = 0,
			offset = 0,
			buffersQueued = {},
			stopThread = false,
		}
		task.spawn(function()
			while not receiveThread.stopThread do
				local format = ProcessFormats.messageIdFormat
				local readBuffer, readOffset = ReceiveMessagesThread.readBuffer(receiveThread, format.size)
				local messageId = format.read(readBuffer, readOffset)
				local args = {}
				local masks = {}
				parse(receiveThread, args, ProcessFormats.messageFormats[messageId + 1], masks)
				for _, callback in ProcessFormats.messageListeners[messageId] do
					task.spawn(callback, unpack(ProcessFormats.deepcopy(args)))
				end
			end
		end)
		return receiveThread
	end
	_container.create = create
end
local default = ReceiveMessagesThread
return {
	ReceiveMessagesThread = ReceiveMessagesThread,
	default = default,
}
