//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

const YAW = 32767;
const INV_YAW = 1 / YAW;

const DATA_SIZE = 32;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const x = buffer.readf64(readBuffer, readOffset);
	const y = buffer.readf64(readBuffer, readOffset + 8);
	const z = buffer.readf64(readBuffer, readOffset + 16);

	const qX = buffer.readi16(readBuffer, readOffset + 24) * INV_YAW;
	const qY = buffer.readi16(readBuffer, readOffset + 26) * INV_YAW;
	const qZ = buffer.readi16(readBuffer, readOffset + 28) * INV_YAW;
	const qW = buffer.readi16(readBuffer, readOffset + 30) * INV_YAW;
	args.push(new CFrame(x, y, z, qX, qY, qZ, qW));
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const value = args[argsCount] as CFrame;
	const data = buffer.create(DATA_SIZE);
	buffer.writef64(data, 0, value.X);
	buffer.writef64(data, 8, value.Y);
	buffer.writef64(data, 16, value.Z);

	const [axis, angle] = value.Rotation.ToAxisAngle();
	const cos = math.cos(angle / 2);
	const sin = math.sin(angle / 2);
	buffer.writei16(data, 24, math.round(axis.X * sin * YAW));
	buffer.writei16(data, 26, math.round(axis.Y * sin * YAW));
	buffer.writei16(data, 28, math.round(axis.Z * sin * YAW));
	buffer.writei16(data, 30, math.round(cos * YAW));
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);
	return argsCount + 1;
}
