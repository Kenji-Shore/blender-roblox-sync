//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

const YAW = 32767 / math.pi;
const INV_YAW = 1 / YAW;
const PITCH = 32767 / (0.5 * math.pi);
const INV_PITCH = 1 / PITCH;

const DATA_SIZE = 4;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const normalYaw = buffer.readi16(readBuffer, readOffset) * INV_YAW;
	const normalPitch = buffer.readi16(readBuffer, readOffset + 2) * INV_PITCH;
	const horizontal = math.cos(normalPitch);
	args.push(new Vector3(math.cos(normalYaw) * horizontal, math.sin(normalPitch), math.sin(normalYaw) * horizontal));
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ProcessFormats.FormatData,
	masks: Map<string, boolean>,
): number {
	const value = args[argsCount] as Vector3;
	const velMag = value.Magnitude;
	const unitVel = velMag !== 0 ? value.div(velMag) : Vector3.xAxis;
	const normalYaw = math.atan2(unitVel.Z, unitVel.X);
	const normalPitch = math.asin(unitVel.Y);

	const data = buffer.create(DATA_SIZE);
	buffer.writei16(data, 0, math.round(normalYaw * YAW));
	buffer.writei16(data, 2, math.round(normalPitch * PITCH));
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);
	return argsCount + 1;
}
