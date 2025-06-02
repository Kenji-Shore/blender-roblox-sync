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
			local pausedThread = pauseThread.thread
			pauseThread.thread = nil
			coroutine.resume(pausedThread)
		end
	end
	_container.unpause = unpause
end
local default = PauseThread
return {
	PauseThread = PauseThread,
	default = default,
}
