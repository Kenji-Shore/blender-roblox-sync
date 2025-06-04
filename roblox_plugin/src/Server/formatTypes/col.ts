//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

const DATA_SIZE = 3;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const r = buffer.readu8(readBuffer, readOffset) / 255;
	const g = buffer.readu8(readBuffer, readOffset + 1) / 255;
	const b = buffer.readu8(readBuffer, readOffset + 2) / 255;
	args.push(new Color3(r, g, b));
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const value = args[argsCount] as Color3;
	const data = buffer.create(DATA_SIZE);
	buffer.writeu8(data, 0, math.round(255 * value.R));
	buffer.writeu8(data, 1, math.round(255 * value.G));
	buffer.writeu8(data, 2, math.round(255 * value.B));
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);
	return argsCount + 1;
}
