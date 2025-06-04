//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, 4);
	const bufLen = buffer.readu32(readBuffer, readOffset);
	const [readBuffer2, readOffset2] = ReceiveMessagesThread.readBuffer(receiveThread, bufLen);
	const bufferValue = buffer.create(bufLen);
	buffer.copy(bufferValue, 0, readBuffer2, readOffset2, bufLen);
	args.push(bufferValue);
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const value = args[argsCount] as buffer;
	const bufLen = buffer.len(value);

	const data = buffer.create(4 + bufLen);
	buffer.writeu32(data, 0, bufLen);
	buffer.copy(data, 4, value);
	SendMessagesThread.writeBuffer(sendThread, data, 4 + bufLen);
	return argsCount + 1;
}
