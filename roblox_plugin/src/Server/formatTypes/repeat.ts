//!native
import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

interface RepeatFormatData {
	type: "repeat";
	repeat: number;
	data: ProcessFormats.FormatData;
}
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: RepeatFormatData,
	masks: Map<string, boolean>,
) {
	for (const _ of $range(1, formatData.repeat)) {
		ReceiveMessagesThread.parse(receiveThread, args, formatData.data, masks);
	}
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: RepeatFormatData,
	masks: Map<string, boolean>,
): number {
	for (const _ of $range(1, formatData.repeat)) {
		argsCount = SendMessagesThread.parse(sendThread, args, argsCount, formatData.data, masks);
	}
	return argsCount;
}
