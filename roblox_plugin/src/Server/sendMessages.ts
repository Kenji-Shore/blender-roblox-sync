import * as ProcessFormats from "./processFormats";
import PauseThread from "./pauseThread";

interface SendMessagesThread extends PauseThread {
	buffer: buffer[];
	bufLen: number;
	buffersQueued: buffer[];
	argsQueued: unknown[][];
}
export namespace SendMessagesThread {
	export function sendMessage(sendThread: SendMessagesThread, messageName: string, ...args: defined[]) {
		assert(messageName in ProcessFormats.sendMessageIds);
		const messageId = ProcessFormats.sendMessageIds.get(messageName);
		args.insert(0, messageId as defined);
		PauseThread.unpause(sendThread);
	}
	export function writeBuffer(sendThread: SendMessagesThread, data: buffer) {
		const dataSize = buffer.len(data);
		sendThread.bufLen += dataSize;
		if (sendThread.bufLen <= ProcessFormats.SEND_LIMIT) {
			sendThread.buffer.push(data);
		} else {
			const overflow = sendThread.bufLen - ProcessFormats.SEND_LIMIT;
			const joinedBuffer = buffer.create(ProcessFormats.SEND_LIMIT);
			let offset = 0;
			for (const segment of sendThread.buffer) {
				buffer.copy(joinedBuffer, offset, segment);
				offset += buffer.len(segment);
			}
			buffer.copy(joinedBuffer, offset, data, 0, dataSize - overflow);
			sendThread.buffersQueued.push(joinedBuffer);
			sendThread.buffer.clear();

			const overflowSegment = buffer.create(overflow);
			buffer.copy(overflowSegment, 0, data, dataSize - overflow);
			sendThread.buffer.push(overflowSegment);
			sendThread.bufLen = overflow;
		}
	}
}
export default SendMessagesThread;

// export function Fire(messageName: string, ...args: unknown[]) {
// 	assert(sendMessageIds[messageName]);
// 	const messageId = sendMessageIds[messageName];
// 	const rawBuffer = new Buffer();

// 	function parseArgs(formatData: FormatData, args: unknown, passedMasks = new Map<string, boolean>()) {
// 		const masks = deepcopy(passedMasks);
// 		let getArg: () => unknown;
// 		if (typeIs(args, "table")) {
// 			let argsCount = 0;
// 			getArg = () => {
// 				const arg = (args as unknown[])[argsCount];
// 				argsCount += 1;
// 				return arg;
// 			};
// 		} else {
// 			getArg = () => {
// 				return args;
// 			};
// 		}

// 		function parse(formatData: FormatData) {
// 			if (typeIs(formatData, "string")) {
// 				//is string or number
// 				(datatypes[formatData].write as WriteBuffer<unknown>)(rawBuffer, getArg());
// 			} else if ("register_mask" in formatData) {
// 				const rawRegisterMasks = formatData.register_mask;
// 				const registerMasks = typeIs(rawRegisterMasks, "table") ? rawRegisterMasks : [rawRegisterMasks];
// 				const maskCount = registerMasks.size();

// 				let bitmask = 0;
// 				for (const i of $range(0, maskCount - 1)) {
// 					const boolValue = getArg() as boolean;
// 					bitmask <<= 1;
// 					bitmask += boolValue ? 1 : 0;
// 					masks.set(registerMasks[i], boolValue);
// 				}
// 				getFormatForCount(maskCount).write(rawBuffer, bitmask);
// 			} else if ("mask" in formatData) {
// 				const mask = formatData.mask;
// 				if (masks.get(mask)) {
// 					parse(formatData.data);
// 				}
// 			} else if ("repeat" in formatData) {
// 				for (const _ of $range(0, formatData.repeat - 1)) {
// 					parse(formatData.data);
// 				}
// 			} else if ("value" in formatData) {
// 				if (formatData.index) {
// 					//is dictionary
// 					const map = getArg() as Map<unknown, unknown>;
// 					datatypes.u32.write(rawBuffer, map.size());
// 					for (const [k, v] of map) {
// 						parseArgs(formatData.index, k, masks);
// 						parseArgs(formatData.value, v, masks);
// 					}
// 				} else {
// 					//is array
// 					const array = getArg() as unknown[];
// 					datatypes.u32.write(rawBuffer, array.size());
// 					for (const v of array) {
// 						parseArgs(formatData.value, v, masks);
// 					}
// 				}
// 			} else {
// 				//is args list
// 				for (const subData of formatData) {
// 					parse(subData);
// 				}
// 			}
// 		}
// 		parse(formatData);
// 	}

// 	messageIdFormat.write(rawBuffer, messageId);
// 	parseArgs(messages[messageId].data, args);
// 	const sendBuffer = rawBuffer.toBuffer();
// 	sendQueue.push(sendBuffer);
// }
