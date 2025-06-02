import messageFormatsFile from "./message_formats.json";
import type SendMessagesThread from "./sendMessages";
import type ReceiveMessagesThread from "./receiveMessages";

// export const sendMessageIds = new Map<string, number>();

type SimpleFormatTypes = "str" | "pos" | "pos2d" | "cf" | "vec" | "unitvec" | "hash" | "col" | "buf"
type ComplexFormatTypes = "repeat" | "format" | "mask" | "register_mask" | "array" | "dict"
type NumberFormatKeys = keyof typeof messageFormatsFile.datatypes;
type RawFormatData = SimpleFormatTypes | NumberFormatKeys | { index: string | undefined; value: RawFormatData }
					| { register_mask: string | string[]; data: FormatData }
	| { mask: string; data: FormatData }
	| { repeat: number; data: FormatData }
	| FormatData[];


type Formats = {
	str: string;
	pos: Vector3;
	pos2d: Vector2;
	cf: CFrame;
	vec: Vector3;
	unitvec: Vector3;
	hash: string;
	col: Color3;
	buf: buffer;
} & Record<NumberFormatKeys, number>;

type FormatKeys = keyof Formats;
type FormatData =
	| FormatKeys
	| { index: string | undefined; value: FormatData }
	| { register_mask: string | string[]; data: FormatData }
	| { mask: string; data: FormatData }
	| { repeat: number; data: FormatData }
	| FormatData[];

function transformFormat(formatData: unknown, requiredType?: keyof CheckableTypes) {
	assert(!requiredType || typeIs(formatData, requiredType));
	if (typeIs(formatData, "table")) {
		if ("value" in formatData) { //is array or dict
			if ("index" in formatData) {
				formatData["index"] = transformFormat(formatData["index"], "string");
				formatData.set("type", "dict");
			} else {
				formatData["type"] = "array"
			}
			formatData["value"] = transformFormat(formatData["value"])
		} else if ("data" in formatData) { //is masked data or repeated data
			formatData["data"] = transformFormat(formatData["data"])
			if "mask" in formatData:
				formatData["type"] = "mask"
			elif "repeat" in formatData:
				formatData["type"] = "repeat"
			elif "register_mask" in formatData:
				register_mask = formatData["register_mask"]
				formatData["register_mask"] = tuple(register_mask) if type(register_mask) is list else (register_mask,)
				formatData["count_format"] = get_format_for_count(len(formatData["register_mask"]))
				formatData["type"] = "register_mask"
		}
	} else {

	}
	else:
		if parsed_type is str:
			formatData = [formatData]

		stack_datatype = None
		stack_count = 0
		merge_str = ""
		merge_count = 0

		list_len = len(formatData)
		list_index = 0
		while True:
			raw = formatData[list_index] if list_index < list_len else None
			is_str = type(raw) is str
			datatype = datatypes[raw]["python"] if is_str and (raw in datatypes) else None
			if datatype == stack_datatype:
				stack_count += 1
			else:
				if stack_datatype:
					merge_str += (str(stack_count) + stack_datatype) if stack_count > 1 else stack_datatype
					merge_count += stack_count
				stack_datatype = datatype
				stack_count = 1

			if datatype:
				formatData.pop(list_index)
				list_len -= 1
			else:
				if merge_str != "":
					formatData.insert(list_index, {
						"count": merge_count,
						"format": struct.Struct("<" + merge_str),
						"type": "format"
					})
					merge_str = ""
					merge_count = 0
					list_len += 1
					list_index += 1

				if raw:
					formatData[list_index] = {"type": raw} if is_str else transform_format(raw)
				list_index += 1

			if not raw:
				break

		if list_len == 1:
			formatData = formatData[0]
	return formatData
}

type UnionParam<Func, Param> = Param extends unknown[]
	? (...args: [...Parameters<Func>, ...Param]) => ReturnType<Func>
	: never;
type OptionalParam<Func, Param> = UnionParam<Func, Param | []>;
type ReadFunc<T> = OptionalParam<(b: buffer, offset: number) => T, [count: number]>;
type WriteFunc<T> = OptionalParam<(b: buffer, offset: number, value: T) => void, [count: number]>;

type ReadBuffer<T> = (b: Buffer) => T;
type WriteBuffer<T> = (b: Buffer, value: T) => void;

interface Datatype<T> {
	read: ReadBuffer<T>;
	write: WriteBuffer<T>;
}

type ReadBufferKeys = `read${NumberFormatKeys}`;
type WriteBufferKeys = `write${NumberFormatKeys}`;
type Datatypes = {
	[Key in FormatKeys]: Datatype<Formats[Key]>;
};

interface MessageFormat {
	name: string;
	sender: "python" | "luau";
	data: FormatData;
}

type Callback = (...args: unknown[]) => void;
const sendMessageIds: Record<string, number> = {};
const receiveMessageIds: Record<string, number> = {};
const messageListeners: Record<number, Callback[]> = {};

const sendLimit = messageFormatsFile.send_limit;
const messages = messageFormatsFile.messages as MessageFormat[];
const totalMessages = messages.size();
for (const i of $range(0, totalMessages - 1)) {
	const message: MessageFormat = messages[i];
	const messageName = message.name;
	if (message.sender === "luau") {
		sendMessageIds[messageName] = i;
	} else {
		receiveMessageIds[messageName] = i;
		messageListeners[i] = [];
	}
}

function deepcopy<T>(object: T): T {
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

function getFormatForCount(count: number): Datatype<number> {
	return [
		{
			read: (b: Buffer): number => {
				return b.read(buffer.readu8, 1);
			},
			write: (b: Buffer, value: number) => {
				b.write(buffer.writeu8, 1, value);
			},
		},
		{
			read: (b: Buffer): number => {
				return b.read(buffer.readu16, 2);
			},
			write: (b: Buffer, value: number) => {
				b.write(buffer.writeu16, 2, value);
			},
		},
		{
			read: (b: Buffer): number => {
				return b.read(buffer.readu32, 4);
			},
			write: (b: Buffer, value: number) => {
				b.write(buffer.writeu32, 4, value);
			},
		},
	][math.min(math.ceil(math.log(2 * math.max(math.log(count, 256), 1), 2)) - 1, 2)] as Datatype<number>;
}
const messageIdFormat = getFormatForCount(totalMessages);
