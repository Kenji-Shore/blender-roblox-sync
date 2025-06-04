//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

interface FormatFormatData {
	type: "format";
	totalSize: number;
	format: ProcessFormats.Values<ProcessFormats.BufferFunctions>[];
}
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: FormatFormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, formatData.totalSize);
	let offset = 0;
	for (const format of formatData.format) {
		args.push(format.read(readBuffer, readOffset + offset));
		offset += format.size;
	}
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: FormatFormatData,
	masks: Map<string, boolean>,
): number {
	const data = buffer.create(formatData.totalSize);
	let offset = 0;
	for (const format of formatData.format) {
		format.write(data, offset, args[argsCount] as number);
		argsCount += 1;
		offset += format.size;
	}
	SendMessagesThread.writeBuffer(sendThread, data, formatData.totalSize);
	return argsCount;
}
