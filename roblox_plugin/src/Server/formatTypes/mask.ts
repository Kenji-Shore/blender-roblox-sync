//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

interface MaskFormatData {
	type: "mask";
	mask: string;
	data: ProcessFormats.FormatData;
}
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: MaskFormatData,
	masks: Map<string, boolean>,
) {
	const mask = formatData.mask;
	if (masks.get(mask)) {
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
	if (masks.get(mask)) {
		argsCount = SendMessagesThread.parse(sendThread, args, argsCount, formatData.data, masks);
	}
	return argsCount;
}
