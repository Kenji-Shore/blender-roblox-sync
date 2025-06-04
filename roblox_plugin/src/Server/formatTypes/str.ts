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
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, 2);
	const strLen = buffer.readu16(readBuffer, readOffset);
	const [readBuffer2, readOffset2] = ReceiveMessagesThread.readBuffer(receiveThread, strLen);
	args.push(buffer.readstring(readBuffer2, readOffset2, strLen));
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const value = args[argsCount] as string;
	const strLen = value.size();

	const data = buffer.create(2 + strLen);
	buffer.writeu16(data, 0, strLen);
	buffer.writestring(data, 2, value, strLen);
	SendMessagesThread.writeBuffer(sendThread, data, 2 + strLen);
	return argsCount + 1;
}
