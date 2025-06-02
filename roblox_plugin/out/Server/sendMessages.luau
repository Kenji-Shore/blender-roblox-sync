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
		PauseThread.unpause(sendThread)
	end
	_container.sendMessage = sendMessage
	local function writeBuffer(sendThread, data)
		local dataSize = buffer.len(data)
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
end
-- export function Fire(messageName: string, ...args: unknown[]) {
-- 	assert(sendMessageIds[messageName]);
-- 	const messageId = sendMessageIds[messageName];
-- 	const rawBuffer = new Buffer();
-- 	function parseArgs(formatData: FormatData, args: unknown, passedMasks = new Map<string, boolean>()) {
-- 		const masks = deepcopy(passedMasks);
-- 		let getArg: () => unknown;
-- 		if (typeIs(args, "table")) {
-- 			let argsCount = 0;
-- 			getArg = () => {
-- 				const arg = (args as unknown[])[argsCount];
-- 				argsCount += 1;
-- 				return arg;
-- 			};
-- 		} else {
-- 			getArg = () => {
-- 				return args;
-- 			};
-- 		}
-- 		function parse(formatData: FormatData) {
-- 			if (typeIs(formatData, "string")) {
-- 				//is string or number
-- 				(datatypes[formatData].write as WriteBuffer<unknown>)(rawBuffer, getArg());
-- 			} else if ("register_mask" in formatData) {
-- 				const rawRegisterMasks = formatData.register_mask;
-- 				const registerMasks = typeIs(rawRegisterMasks, "table") ? rawRegisterMasks : [rawRegisterMasks];
-- 				const maskCount = registerMasks.size();
-- 				let bitmask = 0;
-- 				for (const i of $range(0, maskCount - 1)) {
-- 					const boolValue = getArg() as boolean;
-- 					bitmask <<= 1;
-- 					bitmask += boolValue ? 1 : 0;
-- 					masks.set(registerMasks[i], boolValue);
-- 				}
-- 				getFormatForCount(maskCount).write(rawBuffer, bitmask);
-- 			} else if ("mask" in formatData) {
-- 				const mask = formatData.mask;
-- 				if (masks.get(mask)) {
-- 					parse(formatData.data);
-- 				}
-- 			} else if ("repeat" in formatData) {
-- 				for (const _ of $range(0, formatData.repeat - 1)) {
-- 					parse(formatData.data);
-- 				}
-- 			} else if ("value" in formatData) {
-- 				if (formatData.index) {
-- 					//is dictionary
-- 					const map = getArg() as Map<unknown, unknown>;
-- 					datatypes.u32.write(rawBuffer, map.size());
-- 					for (const [k, v] of map) {
-- 						parseArgs(formatData.index, k, masks);
-- 						parseArgs(formatData.value, v, masks);
-- 					}
-- 				} else {
-- 					//is array
-- 					const array = getArg() as unknown[];
-- 					datatypes.u32.write(rawBuffer, array.size());
-- 					for (const v of array) {
-- 						parseArgs(formatData.value, v, masks);
-- 					}
-- 				}
-- 			} else {
-- 				//is args list
-- 				for (const subData of formatData) {
-- 					parse(subData);
-- 				}
-- 			}
-- 		}
-- 		parse(formatData);
-- 	}
-- 	messageIdFormat.write(rawBuffer, messageId);
-- 	parseArgs(messages[messageId].data, args);
-- 	const sendBuffer = rawBuffer.toBuffer();
-- 	sendQueue.push(sendBuffer);
-- }
return {
	SendMessagesThread = SendMessagesThread,
}
