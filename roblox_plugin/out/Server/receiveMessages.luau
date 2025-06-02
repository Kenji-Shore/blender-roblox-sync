-- Compiled with roblox-ts v3.0.0
local TS = require(script.Parent.Parent.include.RuntimeLib)
local ProcessFormats = TS.import(script, script.Parent, "processFormats")
local PauseThread = TS.import(script, script.Parent, "pauseThread").default
print(ProcessFormats.SEND_LIMIT)
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
	local function test()
		print("huh")
	end
	_container.test = test
end
local default = ReceiveMessagesThread
-- class ReceiveSignalThread {
-- 	private buffer: Buffer;
-- 	private stopThread: boolean;
-- 	receiveSignal(newBuffer: buffer) {
-- 		this.buffer.receiveBuffer(newBuffer);
-- 	}
-- 	private parseArgs(formatData: FormatData, masks = new Map<string, boolean>()): unknown[] {
-- 		const args: unknown[] = [];
-- 		let argCount = 0;
-- 		const parse = (formatData: FormatData, masks: Map<string, boolean>) => {
-- 			if (typeIs(formatData, "string")) {
-- 				//is string or number
-- 				const value = (datatypes[formatData].read as ReadBuffer<unknown>)(this.buffer);
-- 				args[argCount] = value;
-- 				argCount += 1;
-- 			} else if ("register_mask" in formatData) {
-- 				const rawRegisterMasks = formatData.register_mask;
-- 				const registerMasks = typeIs(rawRegisterMasks, "table") ? rawRegisterMasks : [rawRegisterMasks];
-- 				const maskCount = registerMasks.size();
-- 				const bools: boolean[] = [];
-- 				let bitmask = getFormatForCount(maskCount).read(this.buffer);
-- 				for (const _ of $range(0, maskCount - 1)) {
-- 					bools.insert(0, !!(bitmask & 1));
-- 					bitmask >>= 1;
-- 				}
-- 				const newMasks = deepcopy(masks);
-- 				for (const i of $range(0, maskCount - 1)) {
-- 					args[argCount + i] = bools[i];
-- 					newMasks.set(registerMasks[i], bools[i]);
-- 				}
-- 				argCount += maskCount;
-- 				parse(formatData.data, newMasks);
-- 			} else if ("mask" in formatData) {
-- 				const mask = formatData.mask;
-- 				if (masks.get(mask)) {
-- 					parse(formatData.data, masks);
-- 				}
-- 			} else if ("repeat" in formatData) {
-- 				for (const _ of $range(0, formatData.repeat - 1)) {
-- 					parse(formatData.data, masks);
-- 				}
-- 			} else if ("value" in formatData) {
-- 				if (formatData.index) {
-- 					//is dictionary
-- 					const map = new Map();
-- 					const mapSize = datatypes.u32.read(this.buffer);
-- 					for (const _ of $range(0, mapSize - 1)) {
-- 						const k = this.parseArgs(formatData.index, masks)[0];
-- 						const v = this.parseArgs(formatData.value, masks);
-- 						map.set(k, v.size() > 1 ? v : v[0]);
-- 					}
-- 					args[argCount] = map;
-- 				} else {
-- 					// //is array
-- 					const arraySize = datatypes.u32.read(this.buffer);
-- 					const array = new Array(arraySize);
-- 					for (const i of $range(0, arraySize - 1)) {
-- 						const v = this.parseArgs(formatData.value, masks);
-- 						array[i] = v.size() > 1 ? v : v[0];
-- 					}
-- 					args[argCount] = array;
-- 				}
-- 				argCount += 1;
-- 			} else {
-- 				//is args list
-- 				for (const subData of formatData) {
-- 					parse(subData, masks);
-- 				}
-- 			}
-- 		};
-- 		parse(formatData, masks);
-- 		return args;
-- 	}
-- 	stop() {
-- 		this.stopThread = true;
-- 	}
-- 	constructor() {
-- 		this.buffer = new Buffer();
-- 		this.stopThread = false;
-- 		task.spawn(() => {
-- 			while (!this.stopThread) {
-- 				const messageId = messageIdFormat.read(this.buffer);
-- 				const args = this.parseArgs(messages[messageId].data);
-- 				for (const callback of messageListeners[messageId]) {
-- 					task.spawn(callback, ...deepcopy(args));
-- 				}
-- 			}
-- 		});
-- 	}
-- }
return {
	ReceiveMessagesThread = ReceiveMessagesThread,
	default = default,
}
