//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

interface MaskFormatData {
	type: "mask";
	mask: string;
	invert?: boolean;
	data: ProcessFormats.FormatData;
}
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: MaskFormatData,
	masks: Map<string, boolean>,
) {
	const mask = formatData.mask;
	let condition = !!masks.get(mask);
	if ("invert" in formatData && formatData.invert) {
		condition = !condition;
	}
	if (condition) {
		ReceiveMessagesThread.parse(receiveThread, args, formatData.data, masks);
	}
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: MaskFormatData,
	masks: Map<string, boolean>,
): number {
	const mask = formatData.mask;
	let condition = !!masks.get(mask);
	if ("invert" in formatData && formatData.invert) {
		condition = !condition;
	}
	if (condition) {
		argsCount = SendMessagesThread.parse(sendThread, args, argsCount, formatData.data, masks);
	}
	return argsCount;
}
