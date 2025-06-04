-- Compiled with roblox-ts v3.0.0
local PauseThread = {}
do
	local _container = PauseThread
	local function pause(pauseThread)
		pauseThread.thread = coroutine.running()
		coroutine.yield()
	end
	_container.pause = pause
	local function unpause(pauseThread)
		if pauseThread.thread then
			local thread = pauseThread.thread
			pauseThread.thread = nil
			if pauseThread.stopThread then
				coroutine.close(thread)
			else
				coroutine.resume(thread)
			end
		end
	end
	_container.unpause = unpause
	local function stop(pauseThread)
		pauseThread.stopThread = true
	end
	_container.stop = stop
end
local default = PauseThread
return {
	PauseThread = PauseThread,
	default = default,
}
