//!native
import * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";

interface ArrayFormatData {
	type: "array";
	value: ProcessFormats.FormatData;
}
const DATA_SIZE = 4;
export function read(
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: ArrayFormatData,
	masks: Map<string, boolean>,
) {
	const [readBuffer, readOffset] = ReceiveMessagesThread.readBuffer(receiveThread, DATA_SIZE);
	const arraySize = buffer.readu32(readBuffer, readOffset);
	const array = new Array(arraySize);
	for (const i of $range(0, arraySize - 1)) {
		const v: defined[] = [];
		ReceiveMessagesThread.parse(receiveThread, v, formatData.value, masks);
		array[i] = v.size() > 1 ? v : v[0];
	}
	args.push(array);
}
export function write(
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: ArrayFormatData,
	masks: Map<string, boolean>,
): number {
	const array = args[argsCount] as defined[];
	const arraySize = array.size();
	const data = buffer.create(DATA_SIZE);
	buffer.writeu32(data, 0, arraySize);
	SendMessagesThread.writeBuffer(sendThread, data, DATA_SIZE);
	if (arraySize > 0) {
		if (typeIs(array[0], "table")) {
			for (const v of array) {
				SendMessagesThread.parse(sendThread, v as defined[], 0, formatData.value, masks);
			}
		} else {
			for (const v of array) {
				SendMessagesThread.parse(sendThread, [v], 0, formatData.value, masks);
			}
		}
	}
	return argsCount + 1;
}
