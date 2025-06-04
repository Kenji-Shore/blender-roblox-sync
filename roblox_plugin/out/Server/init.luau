--!native
-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.include.RuntimeLib)
local HttpService = TS.import(script, script.Parent, "include", "node_modules", "@rbxts", "services").HttpService
local RunService = TS.import(script, script.Parent, "include", "node_modules", "@rbxts", "services").RunService
local ProcessFormats = TS.import(script, script, "processFormats")
local SendMessagesThread = TS.import(script, script, "sendMessages").default
local ReceiveMessagesThread = TS.import(script, script, "receiveMessages").default
local PauseThread = TS.import(script, script, "pauseThread").default
local sendThread = SendMessagesThread.create()
local receiveThread = ReceiveMessagesThread.create()
ProcessFormats.initialize()
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
		elseif #sendThread.buffersQueued > 0 then
			local sendBuffer = table.remove(sendThread.buffersQueued, 1)
			sendString = buffer.tostring(sendBuffer)
		else
			sendString = ""
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
					local responseBuffer = buffer.fromstring(response.Body)
					if buffer.len(responseBuffer) > 0 then
						ReceiveMessagesThread.receiveMessage(receiveThread, responseBuffer)
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
	local function hook(messageName, callback)
		local _arg0 = ProcessFormats.receiveMessageIds[messageName] ~= nil
		assert(_arg0)
		local _receiveMessageIds = ProcessFormats.receiveMessageIds
		local _messageName = messageName
		local messageId = _receiveMessageIds[_messageName]
		ProcessFormats.listenMessage(messageId, callback)
	end
	_container.hook = hook
	local function unhook(messageName, callback)
		local _arg0 = ProcessFormats.receiveMessageIds[messageName] ~= nil
		assert(_arg0)
		local _receiveMessageIds = ProcessFormats.receiveMessageIds
		local _messageName = messageName
		local messageId = _receiveMessageIds[_messageName]
		ProcessFormats.unlistenMessage(messageId, callback)
	end
	_container.unhook = unhook
	local function fire(messageName, ...)
		local args = { ... }
		SendMessagesThread.sendMessage(sendThread, messageName, unpack(args))
	end
	_container.fire = fire
	local function Unloading()
		connection:Disconnect()
		PauseThread.stop(sendThread)
		PauseThread.stop(receiveThread)
	end
	_container.Unloading = Unloading
end
local default = Server
return {
	Server = Server,
	default = default,
}
