--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.include.RuntimeLib)
local HttpService = TS.import(script, script.Parent, "include", "node_modules", "@rbxts", "services").HttpService
local RunService = TS.import(script, script.Parent, "include", "node_modules", "@rbxts", "services").RunService
local messageFormatsFile = TS.import(script, script.Parent, "message_formats")
local Buffer
do
	Buffer = setmetatable({}, {
		__tostring = function()
			return "Buffer"
		end,
	})
	Buffer.__index = Buffer
	function Buffer.new(...)
		local self = setmetatable({}, Buffer)
		return self:constructor(...) or self
	end
	function Buffer:constructor(b)
		self.buffersQueued = {}
		if b then
			self.buffer = b
			self.bufferSize = buffer.len(b)
		else
			self.buffer = buffer.create(0)
			self.bufferSize = 0
		end
		self.offset = 0
	end
	function Buffer:receiveBuffer(newBuffer)
		local _buffersQueued = self.buffersQueued
		local _newBuffer = newBuffer
		table.insert(_buffersQueued, _newBuffer)
		if self.yieldedThread then
			local yieldedThread = self.yieldedThread
			self.yieldedThread = nil
			coroutine.resume(yieldedThread)
		end
	end
	function Buffer:pollBuffer(byteSize)
		local readBuffer = self.buffer
		local readBufferSize = buffer.len(readBuffer)
		local readOffset = self.offset
		while self.bufferSize < self.offset + byteSize do
			if #self.buffersQueued == 0 then
				self.yieldedThread = coroutine.running()
				coroutine.yield()
			end
			self.buffer = table.remove(self.buffersQueued, 1)
			self.offset -= self.bufferSize
			self.bufferSize = buffer.len(self.buffer)
			local newReadBufferSize = readBufferSize + self.bufferSize
			local newReadBuffer = buffer.create(newReadBufferSize)
			buffer.copy(newReadBuffer, 0, readBuffer)
			buffer.copy(newReadBuffer, readBufferSize, self.buffer)
			readBuffer = newReadBuffer
			readBufferSize = newReadBufferSize
		end
		self.offset += byteSize
		return readBuffer, readOffset
	end
	function Buffer:read(readFunc, byteSize)
		local readBuffer, readOffset = self:pollBuffer(byteSize)
		return readFunc(readBuffer, readOffset, byteSize)
	end
	function Buffer:extendBuffer(byteSize)
		local offset = self.offset
		local newSize = offset + byteSize
		if self.bufferSize < newSize then
			self.bufferSize = math.min(math.pow(2, math.ceil(math.log(newSize + Buffer.bufferPadding, 2))), 1073741824)
			local oldBuffer = self.buffer
			self.buffer = buffer.create(self.bufferSize)
			buffer.copy(self.buffer, 0, oldBuffer)
		end
		self.offset = newSize
		return offset
	end
	function Buffer:write(writeFunc, byteSize, value)
		local offset = self:extendBuffer(byteSize)
		writeFunc(self.buffer, offset, value, byteSize)
	end
	function Buffer:toBuffer()
		local returnBuffer = buffer.create(self.offset)
		buffer.copy(returnBuffer, 0, self.buffer, 0, self.offset)
		return returnBuffer
	end
	Buffer.bufferPadding = 100
end
local function getDatatypes()
	local datatypes = {}
	for formatData, rawData in pairs(messageFormatsFile.datatypes) do
		local readFunc = buffer[("read" .. formatData)]
		local writeFunc = buffer[("write" .. formatData)]
		local byteSize = rawData.luau
		datatypes[formatData] = {
			read = function(b)
				return b:read(readFunc, byteSize)
			end,
			write = function(b, value)
				b:write(writeFunc, byteSize, value)
			end,
		}
	end
	datatypes.str = {
		read = function(b)
			local strLen = b:read(buffer.readu16, 2)
			return b:read(buffer.readstring, strLen)
		end,
		write = function(b, value)
			local strLen = #value
			b:write(buffer.writeu16, 2, strLen)
			b:write(buffer.writestring, strLen, value)
		end,
	}
	datatypes.pos = {
		read = function(b)
			local x = b:read(buffer.readf32, 4)
			local y = b:read(buffer.readf32, 4)
			local z = b:read(buffer.readf32, 4)
			return Vector3.new(x, y, z)
		end,
		write = function(b, value)
			b:write(buffer.writef32, 4, value.X)
			b:write(buffer.writef32, 4, value.Y)
			b:write(buffer.writef32, 4, value.Z)
		end,
	}
	datatypes.pos2d = {
		read = function(b)
			local x = b:read(buffer.readf32, 4)
			local y = b:read(buffer.readf32, 4)
			return Vector2.new(x, y)
		end,
		write = function(b, value)
			b:write(buffer.writef32, 4, value.X)
			b:write(buffer.writef32, 4, value.Y)
		end,
	}
	datatypes.cf = {
		read = function(b)
			local x = b:read(buffer.readf64, 8)
			local y = b:read(buffer.readf64, 8)
			local z = b:read(buffer.readf64, 8)
			local qX = b:read(buffer.readi16, 2) / 32767
			local qY = b:read(buffer.readi16, 2) / 32767
			local qZ = b:read(buffer.readi16, 2) / 32767
			local qW = b:read(buffer.readi16, 2) / 32767
			return CFrame.new(x, y, z, qX, qY, qZ, qW)
		end,
		write = function(b, value)
			b:write(buffer.writef64, 8, value.X)
			b:write(buffer.writef64, 8, value.Y)
			b:write(buffer.writef64, 8, value.Z)
			local axis, angle = value.Rotation:ToAxisAngle()
			local cos = math.cos(angle / 2)
			local sin = math.sin(angle / 2)
			b:write(buffer.writei16, 2, math.round(axis.X * sin * 32767))
			b:write(buffer.writei16, 2, math.round(axis.Y * sin * 32767))
			b:write(buffer.writei16, 2, math.round(axis.Z * sin * 32767))
			b:write(buffer.writei16, 2, math.round(cos * 32767))
		end,
	}
	local YAW = 32767 / math.pi
	local INV_YAW = 1 / YAW
	local PITCH = 32767 / (0.5 * math.pi)
	local INV_PITCH = 1 / PITCH
	datatypes.vec = {
		read = function(b)
			local normalYaw = b:read(buffer.readi16, 2) * INV_YAW
			local normalPitch = b:read(buffer.readi16, 2) * INV_PITCH
			local velMag = b:read(buffer.readf32, 4)
			local horizontal = math.cos(normalPitch)
			return Vector3.new(math.cos(normalYaw) * horizontal, math.sin(normalPitch), math.sin(normalYaw) * horizontal) * velMag
		end,
		write = function(b, value)
			local velMag = value.Magnitude
			local unitVel = if velMag ~= 0 then value / velMag else Vector3.xAxis
			local normalYaw = math.atan2(unitVel.Z, unitVel.X)
			local normalPitch = math.asin(unitVel.Y)
			b:write(buffer.writei16, 2, math.round(normalYaw * YAW))
			b:write(buffer.writei16, 2, math.round(normalPitch * PITCH))
			b:write(buffer.writef32, 4, velMag)
		end,
	}
	datatypes.unitvec = {
		read = function(b)
			local normalYaw = b:read(buffer.readi16, 2) * INV_YAW
			local normalPitch = b:read(buffer.readi16, 2) * INV_PITCH
			local horizontal = math.cos(normalPitch)
			return Vector3.new(math.cos(normalYaw) * horizontal, math.sin(normalPitch), math.sin(normalYaw) * horizontal)
		end,
		write = function(b, value)
			local normalYaw = math.atan2(value.Z, value.X)
			local normalPitch = math.asin(value.Y)
			b:write(buffer.writei16, 2, math.round(normalYaw * YAW))
			b:write(buffer.writei16, 2, math.round(normalPitch * PITCH))
		end,
	}
	datatypes.hash = {
		read = function(b)
			return b:read(buffer.readstring, 8)
		end,
		write = function(b, value)
			b:write(buffer.writestring, 8, value)
		end,
	}
	datatypes.col = {
		read = function(b)
			return Color3.new(b:read(buffer.readu8, 1) / 255, b:read(buffer.readu8, 1) / 255, b:read(buffer.readu8, 1) / 255)
		end,
		write = function(b, value)
			b:write(buffer.writeu8, 1, math.round(255 * value.R))
			b:write(buffer.writeu8, 1, math.round(255 * value.G))
			b:write(buffer.writeu8, 1, math.round(255 * value.B))
		end,
	}
	datatypes.buf = {
		read = function(b)
			local bufLen = b:read(buffer.readu32, 4)
			local readBuffer, readOffset = b:pollBuffer(bufLen)
			local bufferValue = buffer.create(bufLen)
			buffer.copy(bufferValue, 0, readBuffer, readOffset, bufLen)
			return bufferValue
		end,
		write = function(b, value)
			local bufLen = buffer.len(value)
			b:write(buffer.writeu32, 4, bufLen)
			local offset = b:extendBuffer(bufLen)
			buffer.copy(b.buffer, offset, value)
		end,
	}
	return datatypes
end
local datatypes = getDatatypes()
local sendMessageIds = {}
local receiveMessageIds = {}
local messageListeners = {}
local sendLimit = messageFormatsFile.send_limit
local messages = messageFormatsFile.messages
local totalMessages = #messages
for i = 0, totalMessages - 1 do
	local message = messages[i + 1]
	local messageName = message.name
	if message.sender == "luau" then
		sendMessageIds[messageName] = i
	else
		receiveMessageIds[messageName] = i
		messageListeners[i] = {}
	end
end
local function getFormatForCount(count)
	return ({ {
		read = function(b)
			return b:read(buffer.readu8, 1)
		end,
		write = function(b, value)
			b:write(buffer.writeu8, 1, value)
		end,
	}, {
		read = function(b)
			return b:read(buffer.readu16, 2)
		end,
		write = function(b, value)
			b:write(buffer.writeu16, 2, value)
		end,
	}, {
		read = function(b)
			return b:read(buffer.readu32, 4)
		end,
		write = function(b, value)
			b:write(buffer.writeu32, 4, value)
		end,
	} })[math.min(math.ceil(math.log(2 * math.max(math.log(count, 256), 1), 2)) - 1, 2) + 1]
end
local messageIdFormat = getFormatForCount(totalMessages)
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
local ReceiveSignalThread
do
	ReceiveSignalThread = setmetatable({}, {
		__tostring = function()
			return "ReceiveSignalThread"
		end,
	})
	ReceiveSignalThread.__index = ReceiveSignalThread
	function ReceiveSignalThread.new(...)
		local self = setmetatable({}, ReceiveSignalThread)
		return self:constructor(...) or self
	end
	function ReceiveSignalThread:constructor()
		self.buffer = Buffer.new()
		self.stopThread = false
		task.spawn(function()
			while not self.stopThread do
				local messageId = messageIdFormat.read(self.buffer)
				local args = self:parseArgs(messages[messageId + 1].data)
				for _, callback in messageListeners[messageId] do
					task.spawn(callback, unpack(deepcopy(args)))
				end
			end
		end)
	end
	function ReceiveSignalThread:receiveSignal(newBuffer)
		self.buffer:receiveBuffer(newBuffer)
	end
	function ReceiveSignalThread:parseArgs(formatData, masks)
		if masks == nil then
			masks = {}
		end
		local args = {}
		local argCount = 0
		local parse
		parse = function(formatData, masks)
			local _formatData = formatData
			if type(_formatData) == "string" then
				--is string or number
				local value = datatypes[formatData].read(self.buffer)
				args[argCount + 1] = value
				argCount += 1
			elseif formatData.register_mask ~= nil then
				local rawRegisterMasks = formatData.register_mask
				local registerMasks = if type(rawRegisterMasks) == "table" then rawRegisterMasks else { rawRegisterMasks }
				local maskCount = #registerMasks
				local bools = {}
				local bitmask = getFormatForCount(maskCount).read(self.buffer)
				for _ = 0, maskCount - 1 do
					local _value = (bit32.band(bitmask, 1))
					table.insert(bools, 1, not not (_value ~= 0 and _value == _value and _value))
					bitmask = bit32.arshift(bitmask, 1)
				end
				local newMasks = deepcopy(masks)
				for i = 0, maskCount - 1 do
					args[argCount + i + 1] = bools[i + 1]
					local _arg0 = registerMasks[i + 1]
					local _arg1 = bools[i + 1]
					newMasks[_arg0] = _arg1
				end
				argCount += maskCount
				parse(formatData.data, newMasks)
			elseif formatData.mask ~= nil then
				local mask = formatData.mask
				if masks[mask] then
					parse(formatData.data, masks)
				end
			elseif formatData["repeat"] ~= nil then
				for _ = 0, formatData["repeat"] - 1 do
					parse(formatData.data, masks)
				end
			elseif formatData.value ~= nil then
				if formatData.index then
					--is dictionary
					local map = {}
					local mapSize = datatypes.u32.read(self.buffer)
					for _ = 0, mapSize - 1 do
						local k = self:parseArgs(formatData.index, masks)[1]
						local v = self:parseArgs(formatData.value, masks)
						local _arg1 = if #v > 1 then v else v[1]
						map[k] = _arg1
					end
					args[argCount + 1] = map
				else
					-- //is array
					local arraySize = datatypes.u32.read(self.buffer)
					local array = table.create(arraySize)
					for i = 0, arraySize - 1 do
						local v = self:parseArgs(formatData.value, masks)
						array[i + 1] = if #v > 1 then v else v[1]
					end
					args[argCount + 1] = array
				end
				argCount += 1
			else
				--is args list
				for _, subData in formatData do
					parse(subData, masks)
				end
			end
		end
		parse(formatData, masks)
		return args
	end
	function ReceiveSignalThread:stop()
		self.stopThread = true
	end
end
local signalReceiver = ReceiveSignalThread.new()
local sendQueue = {}
local lastClock = os.clock()
local rateLimit = 60 / 1800
local retryString
local connection
connection = RunService.Heartbeat:Connect(function()
	local newClock = os.clock()
	local delta = newClock - lastClock
	if delta >= rateLimit then
		lastClock = newClock - (delta - rateLimit)
		local response = nil
		local sendString
		if retryString ~= "" and retryString then
			sendString = retryString
		else
			local sendStrings = {}
			local queueSize = #sendQueue
			if queueSize > 0 then
				local sendSize = 0
				while queueSize > 0 and sendSize < sendLimit do
					local buf = table.remove(sendQueue, 1)
					local bufferSize = buffer.len(buf)
					sendSize += bufferSize
					queueSize -= 1
					if sendSize <= sendLimit then
						local _arg0 = buffer.tostring(buf)
						table.insert(sendStrings, _arg0)
					else
						local overflow = sendSize - sendLimit
						local _arg0 = buffer.readstring(buf, 0, overflow)
						table.insert(sendStrings, _arg0)
						local remainingBuffer = buffer.create(bufferSize - overflow)
						buffer.copy(remainingBuffer, 0, buf, overflow)
						table.insert(sendQueue, 1, remainingBuffer)
					end
				end
			end
			sendString = table.concat(sendStrings, "")
		end
		TS.try(function()
			response = HttpService:RequestAsync({
				Url = "http://localhost:50520",
				Method = "POST",
				Body = sendString,
			})
		end, function(error)
			retryString = sendString
			print(error)
			if error == "Number of requests exceeded limit" then
				connection:Disconnect()
			end
		end, function()
			if response then
				retryString = nil
				if response.Success then
					local response_buffer = buffer.fromstring(response.Body)
					if buffer.len(response_buffer) > 0 then
						signalReceiver:receiveSignal(response_buffer)
					end
				else
					print("Fail", response.StatusMessage)
				end
			end
		end)
	end
end)
local Server = {}
do
	local _container = Server
	local function Hook(messageName, callback)
		local _arg0 = receiveMessageIds[messageName] ~= nil
		assert(_arg0)
		local messageId = receiveMessageIds[messageName]
		local _exp = messageListeners[messageId]
		local _callback = callback
		table.insert(_exp, _callback)
	end
	_container.Hook = Hook
	local function Unhook(messageName, callback)
		local _arg0 = receiveMessageIds[messageName] ~= nil
		assert(_arg0)
		local messageId = receiveMessageIds[messageName]
		local listeners = messageListeners[messageId]
		local _callback = callback
		local index = (table.find(listeners, _callback) or 0) - 1
		if index > -1 then
			table.remove(listeners, index + 1)
		end
	end
	_container.Unhook = Unhook
	local function Fire(messageName, ...)
		local args = { ... }
		local _arg0 = sendMessageIds[messageName]
		assert(_arg0 ~= 0 and _arg0 == _arg0 and _arg0)
		local messageId = sendMessageIds[messageName]
		local rawBuffer = Buffer.new()
		local function parseArgs(formatData, args, passedMasks)
			if passedMasks == nil then
				passedMasks = {}
			end
			local masks = deepcopy(passedMasks)
			local getArg
			local _args = args
			if type(_args) == "table" then
				local argsCount = 0
				getArg = function()
					local arg = args[argsCount + 1]
					argsCount += 1
					return arg
				end
			else
				getArg = function()
					return args
				end
			end
			local function parse(formatData)
				local _formatData = formatData
				if type(_formatData) == "string" then
					--is string or number
					datatypes[formatData].write(rawBuffer, getArg())
				elseif formatData.register_mask ~= nil then
					local rawRegisterMasks = formatData.register_mask
					local registerMasks = if type(rawRegisterMasks) == "table" then rawRegisterMasks else { rawRegisterMasks }
					local maskCount = #registerMasks
					local bitmask = 0
					for i = 0, maskCount - 1 do
						local boolValue = getArg()
						bitmask = bit32.lshift(bitmask, 1)
						bitmask += if boolValue then 1 else 0
						local _arg0_1 = registerMasks[i + 1]
						masks[_arg0_1] = boolValue
					end
					getFormatForCount(maskCount).write(rawBuffer, bitmask)
				elseif formatData.mask ~= nil then
					local mask = formatData.mask
					if masks[mask] then
						parse(formatData.data)
					end
				elseif formatData["repeat"] ~= nil then
					for _ = 0, formatData["repeat"] - 1 do
						parse(formatData.data)
					end
				elseif formatData.value ~= nil then
					if formatData.index then
						--is dictionary
						local map = getArg()
						local _u32 = datatypes.u32
						-- ▼ ReadonlyMap.size ▼
						local _size = 0
						for _ in map do
							_size += 1
						end
						-- ▲ ReadonlyMap.size ▲
						_u32.write(rawBuffer, _size)
						for k, v in map do
							parseArgs(formatData.index, k, masks)
							parseArgs(formatData.value, v, masks)
						end
					else
						--is array
						local array = getArg()
						datatypes.u32.write(rawBuffer, #array)
						for _, v in array do
							parseArgs(formatData.value, v, masks)
						end
					end
				else
					--is args list
					for _, subData in formatData do
						parse(subData)
					end
				end
			end
			parse(formatData)
		end
		messageIdFormat.write(rawBuffer, messageId)
		parseArgs(messages[messageId + 1].data, args)
		local sendBuffer = rawBuffer:toBuffer()
		table.insert(sendQueue, sendBuffer)
	end
	_container.Fire = Fire
	local function Unloading()
		connection:Disconnect()
		signalReceiver:stop()
	end
	_container.Unloading = Unloading
end
local default = Server
return {
	Server = Server,
	default = default,
}
