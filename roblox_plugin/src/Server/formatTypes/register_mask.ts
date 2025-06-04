//!native
import * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

interface RegisterMaskFormatData {
	type: "register_mask";
	register_mask: string[];
	data: ProcessFormats.FormatData;
}
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: RegisterMaskFormatData,
	masks: Map<string, boolean>,
) {
	const registerMasks = formatData.register_mask;
	const maskCount = registerMasks.size();
	const countFormat = ProcessFormats.getFormatForCount(maskCount);

	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, countFormat.size);
	let bitmask = countFormat.read(readBuffer, readOffset);
	const bools: boolean[] = [];
	for (const _ of $range(0, maskCount - 1)) {
		bools.insert(0, !!(bitmask & 1));
		bitmask >>= 1;
	}

	const newMasks = ProcessFormats.deepcopy(masks);
	for (const i of $range(0, maskCount - 1)) {
		args.push(bools[i]);
		newMasks.set(registerMasks[i], bools[i]);
	}
	ReceiveMessagesThread.parse(receiveThread, args, formatData.data, newMasks);
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: RegisterMaskFormatData,
	masks: Map<string, boolean>,
): number {
	const registerMasks = formatData.register_mask;
	const maskCount = registerMasks.size();
	const countFormat = ProcessFormats.getFormatForCount(maskCount);

	let bitmask = 0;
	const newMasks = ProcessFormats.deepcopy(masks);
	for (const i of $range(0, maskCount - 1)) {
		const boolValue = args[argsCount] as boolean;
		argsCount += 1;
		bitmask <<= 1;
		bitmask += boolValue ? 1 : 0;
		newMasks.set(registerMasks[i], boolValue);
	}
	const data = buffer.create(countFormat.size);
	countFormat.write(data, 0, bitmask);
	SendMessagesThread.writeBuffer(sendThread, data, countFormat.size);
	return SendMessagesThread.parse(sendThread, args, argsCount, formatData.data, newMasks);
}
