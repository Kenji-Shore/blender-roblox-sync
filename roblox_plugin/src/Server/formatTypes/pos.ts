//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

const DATA_SIZE = 12;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const x = buffer.readf32(readBuffer, readOffset);
	const y = buffer.readf32(readBuffer, readOffset + 4);
	const z = buffer.readf32(readBuffer, readOffset + 8);
	args.push(new Vector3(x, y, z));
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const value = args[argsCount] as Vector3;

	const data = buffer.create(DATA_SIZE);
	buffer.writef32(data, 0, value.X);
	buffer.writef32(data, 4, value.Y);
	buffer.writef32(data, 8, value.Z);
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);
	return argsCount + 1;
}
