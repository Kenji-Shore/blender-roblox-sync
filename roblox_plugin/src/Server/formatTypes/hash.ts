//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

const DATA_SIZE = 32;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const hashValue = buffer.readstring(readBuffer, readOffset, DATA_SIZE);
	args.push(hashValue);
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const hashValue = args[argsCount] as string;
	const data = buffer.fromstring(hashValue);
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);
	return argsCount + 1;
}
