//!native
import * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

interface DictFormatData {
	type: "dict";
	index: ProcessFormats.FormatData;
	value: ProcessFormats.FormatData;
}
const DATA_SIZE = 4;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: DictFormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const dictSize = buffer.readu32(readBuffer, readOffset);
	const dict = new Map<defined, defined>();

	for (const _ of $range(1, dictSize)) {
		const k: defined[] = [];
		const v: defined[] = [];
		ReceiveMessagesThread.parse(receiveThread, k, formatData.index, masks);
		ReceiveMessagesThread.parse(receiveThread, v, formatData.value, masks);
		dict.set(k[0], v.size() > 1 ? v : v[0]);
	}
	args.push(dict);
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: DictFormatData,
	masks: Map<string, boolean>,
): number {
	const dict = args[argsCount] as Map<defined, defined>;
	const dictSize = dict.size();
	const data = buffer.create(DATA_SIZE);
	buffer.writeu32(data, 0, dictSize);
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);

	if (dictSize > 0) {
		const [_, testValue] = next(dict);
		if (typeIs(testValue, "table")) {
			for (const [k, v] of dict) {
				SendMessagesThread.parse(sendThread, [k], 0, formatData.index, masks);
				SendMessagesThread.parse(sendThread, v as defined[], 0, formatData.value, masks);
			}
		} else {
			for (const [k, v] of dict) {
				SendMessagesThread.parse(sendThread, [k], 0, formatData.index, masks);
				SendMessagesThread.parse(sendThread, [v], 0, formatData.value, masks);
			}
		}
	}
	return argsCount + 1;
}
