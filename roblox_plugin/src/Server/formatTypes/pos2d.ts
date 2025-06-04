//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

const DATA_SIZE = 8;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const x = buffer.readf32(readBuffer, readOffset);
	const y = buffer.readf32(readBuffer, readOffset + 4);
	args.push(new Vector2(x, y));
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const value = args[argsCount] as Vector2;

	const data = buffer.create(DATA_SIZE);
	buffer.writef32(data, 0, value.X);
	buffer.writef32(data, 4, value.Y);
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);
	return argsCount + 1;
}
