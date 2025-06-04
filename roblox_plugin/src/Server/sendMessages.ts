import * as ProcessFormats from "./processFormats";
import PauseThread from "./pauseThread";

export interface SendMessagesThread extends PauseThread {
	buffer: buffer[];
	bufLen: number;
	buffersQueued: buffer[];
	argsQueued: defined[][];
}
export namespace SendMessagesThread {
	export function sendMessage(sendThread: SendMessagesThread, messageName: string, ...args: defined[]) {
		assert(messageName in ProcessFormats.sendMessageIds);
		const messageId = ProcessFormats.sendMessageIds.get(messageName);
		args.unshift(messageId as defined);
		sendThread.argsQueued.push(args);
		PauseThread.unpause(sendThread);
	}
	export function writeBuffer(sendThread: SendMessagesThread, data: buffer, dataSize: number) {
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

	export function parse(
		sendThread: SendMessagesThread,
		args: defined[],
		argsCount: number,
		formatData: ProcessFormats.FormatData,
		masks: Map<string, boolean>,
	): number {
		if (!("type" in formatData)) {
			for (const subFormatData of formatData) {
				argsCount = parse(sendThread, args, argsCount, subFormatData, masks);
			}
		} else {
			argsCount = ProcessFormats.writeFuncs.get(formatData.type)!(sendThread, args, argsCount, formatData, masks);
		}
		return argsCount;
	}

	export function create(): SendMessagesThread {
		const sendThread: SendMessagesThread = {
			buffer: [],
			bufLen: 0,
			buffersQueued: [],
			argsQueued: [],
			stopThread: false,
		};

		task.spawn(() => {
			while (!sendThread.stopThread) {
				if (sendThread.argsQueued.size() === 0) {
					PauseThread.pause(sendThread);
				}
				const args = sendThread.argsQueued.shift()!;
				const messageId = args[0] as number;
				const format = ProcessFormats.messageIdFormat;
				const data = buffer.create(format.size);
				format.write(data, 0, messageId);
				writeBuffer(sendThread, data, format.size);
				const masks = new Map<string, boolean>();
				parse(sendThread, args, 1, ProcessFormats.messageFormats[messageId], masks);

				const joinedBuffer = buffer.create(sendThread.bufLen);
				let offset = 0;
				for (const segment of sendThread.buffer) {
					buffer.copy(joinedBuffer, offset, segment);
					offset += buffer.len(segment);
				}
				sendThread.buffersQueued.push(joinedBuffer);
				sendThread.buffer.clear();
				sendThread.bufLen = 0;
			}
		});
		return sendThread;
	}
}
export default SendMessagesThread;
