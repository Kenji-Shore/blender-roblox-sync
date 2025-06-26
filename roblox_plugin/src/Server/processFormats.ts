import messageFormatsFile from "./message_formats.json";
import type SendMessagesThread from "./sendMessages";
import type ReceiveMessagesThread from "./receiveMessages";

export type Values<T> = T[keyof T];
type SimpleFormats = "str" | "pos" | "pos2d" | "cf" | "vec" | "unitvec" | "hash" | "col" | "buf";
const DATATYPES = {
	u8: 1,
	i8: 1,
	u16: 2,
	i16: 2,
	u32: 4,
	i32: 4,
	f32: 4,
	f64: 8,
} as const;
type Datatypes = typeof DATATYPES;

type RawFormatData =
	| SimpleFormats
	| keyof Datatypes
	| { index?: RawFormatData; value: RawFormatData }
	| { register_mask: string | string[]; data: RawFormatData }
	| { mask: string; invert?: boolean; data: RawFormatData }
	| { repeat: number; data: RawFormatData }
	| RawFormatData[];

export type BufferFunctions = {
	[T in keyof Datatypes]: {
		size: Datatypes[T];
		read: (typeof buffer)[`read${T}`];
		write: (typeof buffer)[`write${T}`];
	};
};

type CountFormat = BufferFunctions["u8" | "u16" | "u32"];
export function getFormatForCount(count: number): CountFormat {
	return [
		{
			size: 1,
			read: buffer.readu8,
			write: buffer.writeu8,
		},
		{
			size: 2,
			read: buffer.readu16,
			write: buffer.writeu16,
		},
		{
			size: 4,
			read: buffer.readu32,
			write: buffer.writeu32,
		},
	][math.min(math.ceil(math.log(2 * math.max(math.log(count, 256), 1), 2)) - 1, 2)] as CountFormat;
}

export type FormatData =
	| Values<{
			[T in SimpleFormats]: {
				type: T;
			};
	  }>
	| {
			type: "format";
			totalSize: number;
			format: Values<BufferFunctions>[];
	  }
	| { type: "array"; value: FormatData }
	| { type: "dict"; index: FormatData; value: FormatData }
	| { type: "register_mask"; register_mask: string[]; count_format: CountFormat; data: FormatData }
	| { type: "mask"; mask: string; invert?: boolean; data: FormatData }
	| { type: "repeat"; repeat: number; data: FormatData }
	| FormatData[];

function transformFormat(rawFormatData: RawFormatData, requiredType?: keyof CheckableTypes): FormatData {
	assert(!requiredType || typeIs(rawFormatData, requiredType));
	if (typeIs(rawFormatData, "table")) {
		if ("value" in rawFormatData) {
			//is array or dict
			const value = transformFormat(rawFormatData.value);
			if ("index" in rawFormatData) {
				return {
					type: "dict",
					index: transformFormat(rawFormatData.index!, "string"),
					value: value,
				};
			} else {
				return {
					type: "array",
					value: value,
				};
			}
		} else if ("data" in rawFormatData) {
			const data = transformFormat(rawFormatData.data);
			if ("mask" in rawFormatData) {
				return {
					type: "mask",
					mask: rawFormatData.mask,
					invert: rawFormatData.invert,
					data: data,
				};
			} else if ("repeat" in rawFormatData) {
				return {
					type: "repeat",
					repeat: rawFormatData.repeat,
					data: data,
				};
			} else if ("register_mask" in rawFormatData) {
				const raw_register_mask = rawFormatData.register_mask;
				const register_mask = typeIs(raw_register_mask, "table") ? raw_register_mask : [raw_register_mask];
				return {
					type: "register_mask",
					register_mask: register_mask,
					count_format: getFormatForCount(register_mask.size()),
					data: data,
				};
			}
		}
	}

	if (!typeIs(rawFormatData, "table")) {
		rawFormatData = [rawFormatData];
	}
	const formatData: FormatData[] = [];
	let mergeFormats: Values<BufferFunctions>[] = [];
	let totalSize = 0;
	function writeFormat() {
		if (mergeFormats.size() > 0) {
			formatData.push({
				type: "format",
				totalSize: totalSize,
				format: mergeFormats,
			});
			mergeFormats = [];
			totalSize = 0;
		}
	}
	for (const raw of rawFormatData) {
		const isStr = typeIs(raw, "string");
		if (isStr && raw in DATATYPES) {
			const size = DATATYPES[raw as keyof Datatypes];
			totalSize += size;
			mergeFormats.push({
				size: size,
				read: buffer[`read${raw as keyof Datatypes}`],
				write: buffer[`write${raw as keyof Datatypes}`],
			});
		} else {
			writeFormat();
			if (isStr) {
				formatData.push({
					type: raw as SimpleFormats,
				});
			} else {
				formatData.push(transformFormat(raw));
			}
		}
	}
	writeFormat();

	if (formatData.size() === 1) {
		return formatData[0];
	} else {
		return formatData;
	}
}

interface MessageFormat<T> {
	name: string;
	sender: "python" | "luau";
	data: T;
}

export type Callback = (...args: defined[]) => void;
export const messageListeners: Record<number, Callback[]> = {};
export function listenMessage(messageId: number, callback: Callback) {
	messageListeners[messageId].push(callback);
}
export function unlistenMessage(messageId: number, callback: Callback) {
	messageListeners[messageId].remove(messageListeners[messageId].indexOf(callback));
}

const rawMessages = messageFormatsFile.messages as MessageFormat<RawFormatData>[];
const totalMessages = rawMessages.size();
export const sendMessageIds = new Map<string, number>();
export const receiveMessageIds = new Map<string, number>();
export const messageFormats: FormatData[] = [];
export const SEND_LIMIT = 20000000;
export const messageIdFormat = getFormatForCount(totalMessages);
for (const i of $range(0, totalMessages - 1)) {
	const rawMessage = rawMessages[i];
	const messageName = rawMessage.name;
	if (rawMessage.sender === "luau") {
		sendMessageIds.set(messageName, i);
	} else {
		receiveMessageIds.set(messageName, i);
		messageListeners[i] = [];
	}
	messageFormats.push(transformFormat(rawMessage.data));
}

export function deepcopy<T>(object: T): T {
	if (typeIs(object, "table")) {
		const copyObject = new Map<unknown, unknown>();
		for (const [k, v] of object as unknown as Map<unknown, unknown>) {
			copyObject.set(k, deepcopy(v));
		}
		return copyObject as T;
	} else {
		return object;
	}
}

type ReadFunc = (
	receiveThread: ReceiveMessagesThread,
	args: defined[],
	formatData: FormatData,
	masks: Map<string, boolean>,
) => void;
type WriteFunc = (
	sendThread: SendMessagesThread,
	args: defined[],
	argsCount: number,
	formatData: FormatData,
	masks: Map<string, boolean>,
) => number;
interface Module {
	read: ReadFunc;
	write: WriteFunc;
}

export const readFuncs = new Map<string, ReadFunc>();
export const writeFuncs = new Map<string, WriteFunc>();
export function initialize() {
	for (const moduleScript of script.Parent!.FindFirstChild("formatTypes")!.GetChildren()) {
		if (classIs(moduleScript, "ModuleScript")) {
			const moduleName = moduleScript.Name;
			const module = require(moduleScript) as Module;
			readFuncs.set(moduleName, module.read);
			writeFuncs.set(moduleName, module.write);
		}
	}
}
