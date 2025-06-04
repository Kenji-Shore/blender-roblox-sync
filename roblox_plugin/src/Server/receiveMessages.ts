import * as ProcessFormats from "./processFormats";
import PauseThread from "./pauseThread";

export interface ReceiveMessagesThread extends PauseThread {
	buffer: buffer;
	bufLen: number;
	offset: number;
	buffersQueued: buffer[];
}
export namespace ReceiveMessagesThread {
	export function receiveMessage(receiveThread: ReceiveMessagesThread, newBuffer: buffer) {
		receiveThread.buffersQueued.push(newBuffer);
		PauseThread.unpause(receiveThread);
	}
	export function readBuffer(receiveThread: ReceiveMessagesThread, dataSize: number): LuaTuple<[buffer, number]> {
		let readBuffer = receiveThread.buffer;
		let readBufferSize = buffer.len(readBuffer);
		const readOffset = receiveThread.offset;
		while (receiveThread.bufLen < receiveThread.offset + dataSize) {
			if (receiveThread.buffersQueued.size() === 0) {
				PauseThread.pause(receiveThread);
			}
			receiveThread.buffer = receiveThread.buffersQueued.shift()!;
			receiveThread.offset -= receiveThread.bufLen;
			receiveThread.bufLen = buffer.len(receiveThread.buffer);

			const newReadBufferSize = readBufferSize + receiveThread.bufLen;
			const newReadBuffer = buffer.create(newReadBufferSize);
			buffer.copy(newReadBuffer, 0, readBuffer);
			buffer.copy(newReadBuffer, readBufferSize, receiveThread.buffer);
			readBuffer = newReadBuffer;
			readBufferSize = newReadBufferSize;
		}

		receiveThread.offset += dataSize;
		return $tuple(readBuffer, readOffset);
	}

	export function parse(
		receiveThread: ReceiveMessagesThread,
		args: defined[],
		formatData: ProcessFormats.FormatData,
		masks: Map<string, boolean>,
	) {
		if (!("type" in formatData)) {
			for (const subFormatData of formatData) {
				parse(receiveThread, args, subFormatData, masks);
			}
		} else {
			ProcessFormats.readFuncs.get(formatData.type)!(receiveThread, args, formatData, masks);
		}
	}

	export function create(): ReceiveMessagesThread {
		const receiveThread: ReceiveMessagesThread = {
			buffer: buffer.create(0),
			bufLen: 0,
			offset: 0,
			buffersQueued: [],
			stopThread: false,
		};

		task.spawn(() => {
			while (!receiveThread.stopThread) {
				const format = ProcessFormats.messageIdFormat;
				const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, format.size);
				const messageId = format.read(readBuffer, readOffset);
				const args: defined[] = [];
				const masks = new Map<string, boolean>();
				parse(receiveThread, args, ProcessFormats.messageFormats[messageId], masks);
				for (const callback of ProcessFormats.messageListeners[messageId]) {
					task.spawn(callback, ...ProcessFormats.deepcopy(args));
				}
			}
		});
		return receiveThread;
	}
}
export default ReceiveMessagesThread;
