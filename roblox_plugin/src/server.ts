//!native

import { HttpService } from "@rbxts/services";
import { RunService } from "@rbxts/services";
import messageFormatsFile from "./message_formats.json";
type UnionParam<Func, Param> = Param extends unknown[]
	? (...args: [...Parameters<Func>, ...Param]) => ReturnType<Func>
	: never;
type OptionalParam<Func, Param> = UnionParam<Func, Param | []>;
type ReadFunc<T> = OptionalParam<(b: buffer, offset: number) => T, [count: number]>;
type WriteFunc<T> = OptionalParam<(b: buffer, offset: number, value: T) => void, [count: number]>;
class Buffer {
	buffer: buffer;

	private static readonly bufferPadding = 100;
	private buffersQueued: buffer[];
	private bufferSize: number;
	private offset: number;
	private yieldedThread: thread | undefined;

	receiveBuffer(newBuffer: buffer) {
		this.buffersQueued.push(newBuffer);
		if (this.yieldedThread) {
			const yieldedThread = this.yieldedThread;
			this.yieldedThread = undefined;
			coroutine.resume(yieldedThread);
		}
	}

	pollBuffer(byteSize: number): LuaTuple<[buffer, number]> {
		let readBuffer = this.buffer;
		let readBufferSize = buffer.len(readBuffer);
		const readOffset = this.offset;
		while (this.bufferSize < this.offset + byteSize) {
			if (this.buffersQueued.size() === 0) {
				this.yieldedThread = coroutine.running();
				coroutine.yield();
			}
			this.buffer = this.buffersQueued.shift()!;
			this.offset -= this.bufferSize;
			this.bufferSize = buffer.len(this.buffer);

			const newReadBufferSize = readBufferSize + this.bufferSize;
			const newReadBuffer = buffer.create(newReadBufferSize);
			buffer.copy(newReadBuffer, 0, readBuffer);
			buffer.copy(newReadBuffer, readBufferSize, this.buffer);
			readBuffer = newReadBuffer;
			readBufferSize = newReadBufferSize;
		}

		this.offset += byteSize;
		return $tuple(readBuffer, readOffset);
	}

	read<T>(readFunc: ReadFunc<T>, byteSize: number): T {
		const [readBuffer, readOffset] = this.pollBuffer(byteSize);
		return readFunc(readBuffer, readOffset, byteSize);
	}

	extendBuffer(byteSize: number): number {
		const offset = this.offset;
		const newSize = offset + byteSize;
		if (this.bufferSize < newSize) {
			this.bufferSize = math.min(math.pow(2, math.ceil(math.log(newSize + Buffer.bufferPadding, 2))), 1073741824);

			const oldBuffer = this.buffer;
			this.buffer = buffer.create(this.bufferSize);
			buffer.copy(this.buffer, 0, oldBuffer);
		}

		this.offset = newSize;
		return offset;
	}

	write<T>(writeFunc: WriteFunc<T>, byteSize: number, value: T) {
		const offset = this.extendBuffer(byteSize);
		writeFunc(this.buffer, offset, value, byteSize);
	}

	toBuffer(): buffer {
		const returnBuffer = buffer.create(this.offset);
		buffer.copy(returnBuffer, 0, this.buffer, 0, this.offset);
		return returnBuffer;
	}

	constructor(b?: buffer) {
		this.buffersQueued = [];
		if (b) {
			this.buffer = b;
			this.bufferSize = buffer.len(b);
		} else {
			this.buffer = buffer.create(0);
			this.bufferSize = 0;
		}
		this.offset = 0;
	}
}

type ReadBuffer<T> = (b: Buffer) => T;
type WriteBuffer<T> = (b: Buffer, value: T) => void;

interface Datatype<T> {
	read: ReadBuffer<T>;
	write: WriteBuffer<T>;
}

type NumberFormatKeys = keyof typeof messageFormatsFile.datatypes;
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
type ReadBufferKeys = `read${NumberFormatKeys}`;
type WriteBufferKeys = `write${NumberFormatKeys}`;
type Datatypes = {
	[Key in FormatKeys]: Datatype<Formats[Key]>;
};

function getDatatypes(): Datatypes {
	const datatypes: Partial<Datatypes> = {};
	for (const [formatData, rawData] of pairs(
		messageFormatsFile.datatypes as Record<NumberFormatKeys, { luau: number; python: string }>,
	)) {
		const readFunc = buffer[("read" + formatData) as ReadBufferKeys];
		const writeFunc = buffer[("write" + formatData) as WriteBufferKeys];
		const byteSize: number = rawData.luau;

		datatypes[formatData] = {
			read: (b: Buffer): number => {
				return b.read(readFunc, byteSize);
			},
			write: (b: Buffer, value: number) => {
				b.write(writeFunc, byteSize, value);
			},
		};
	}
	datatypes.str = {
		read: (b: Buffer): string => {
			const strLen = b.read(buffer.readu16, 2);
			return b.read(buffer.readstring, strLen);
		},
		write: (b: Buffer, value: string) => {
			const strLen = value.size();
			b.write(buffer.writeu16, 2, strLen);
			b.write(buffer.writestring, strLen, value);
		},
	};
	datatypes.pos = {
		read: (b: Buffer): Vector3 => {
			const x = b.read(buffer.readf32, 4);
			const y = b.read(buffer.readf32, 4);
			const z = b.read(buffer.readf32, 4);
			return new Vector3(x, y, z);
		},
		write: (b: Buffer, value: Vector3) => {
			b.write(buffer.writef32, 4, value.X);
			b.write(buffer.writef32, 4, value.Y);
			b.write(buffer.writef32, 4, value.Z);
		},
	};
	datatypes.pos2d = {
		read: (b: Buffer): Vector2 => {
			const x = b.read(buffer.readf32, 4);
			const y = b.read(buffer.readf32, 4);
			return new Vector2(x, y);
		},
		write: (b: Buffer, value: Vector2) => {
			b.write(buffer.writef32, 4, value.X);
			b.write(buffer.writef32, 4, value.Y);
		},
	};
	datatypes.cf = {
		read: (b: Buffer): CFrame => {
			const x = b.read(buffer.readf64, 8);
			const y = b.read(buffer.readf64, 8);
			const z = b.read(buffer.readf64, 8);

			const qX = b.read(buffer.readi16, 2) / 32767;
			const qY = b.read(buffer.readi16, 2) / 32767;
			const qZ = b.read(buffer.readi16, 2) / 32767;
			const qW = b.read(buffer.readi16, 2) / 32767;
			return new CFrame(x, y, z, qX, qY, qZ, qW);
		},
		write: (b: Buffer, value: CFrame) => {
			b.write(buffer.writef64, 8, value.X);
			b.write(buffer.writef64, 8, value.Y);
			b.write(buffer.writef64, 8, value.Z);

			const [axis, angle] = value.Rotation.ToAxisAngle();
			const cos = math.cos(angle / 2);
			const sin = math.sin(angle / 2);
			b.write(buffer.writei16, 2, math.round(axis.X * sin * 32767));
			b.write(buffer.writei16, 2, math.round(axis.Y * sin * 32767));
			b.write(buffer.writei16, 2, math.round(axis.Z * sin * 32767));
			b.write(buffer.writei16, 2, math.round(cos * 32767));
		},
	};

	const YAW = 32767 / math.pi;
	const INV_YAW = 1 / YAW;
	const PITCH = 32767 / (0.5 * math.pi);
	const INV_PITCH = 1 / PITCH;
	datatypes.vec = {
		read: (b: Buffer): Vector3 => {
			const normalYaw = b.read(buffer.readi16, 2) * INV_YAW;
			const normalPitch = b.read(buffer.readi16, 2) * INV_PITCH;
			const velMag = b.read(buffer.readf32, 4);
			const horizontal = math.cos(normalPitch);
			return new Vector3(
				math.cos(normalYaw) * horizontal,
				math.sin(normalPitch),
				math.sin(normalYaw) * horizontal,
			).mul(velMag);
		},
		write: (b: Buffer, value: Vector3) => {
			const velMag = value.Magnitude;
			const unitVel = velMag !== 0 ? value.div(velMag) : Vector3.xAxis;
			const normalYaw = math.atan2(unitVel.Z, unitVel.X);
			const normalPitch = math.asin(unitVel.Y);
			b.write(buffer.writei16, 2, math.round(normalYaw * YAW));
			b.write(buffer.writei16, 2, math.round(normalPitch * PITCH));
			b.write(buffer.writef32, 4, velMag);
		},
	};
	datatypes.unitvec = {
		read: (b: Buffer): Vector3 => {
			const normalYaw = b.read(buffer.readi16, 2) * INV_YAW;
			const normalPitch = b.read(buffer.readi16, 2) * INV_PITCH;
			const horizontal = math.cos(normalPitch);
			return new Vector3(
				math.cos(normalYaw) * horizontal,
				math.sin(normalPitch),
				math.sin(normalYaw) * horizontal,
			);
		},
		write: (b: Buffer, value: Vector3) => {
			const normalYaw = math.atan2(value.Z, value.X);
			const normalPitch = math.asin(value.Y);
			b.write(buffer.writei16, 2, math.round(normalYaw * YAW));
			b.write(buffer.writei16, 2, math.round(normalPitch * PITCH));
		},
	};
	datatypes.hash = {
		read: (b: Buffer): string => {
			return b.read(buffer.readstring, 8);
		},
		write: (b: Buffer, value: string) => {
			b.write(buffer.writestring, 8, value);
		},
	};
	datatypes.col = {
		read: (b: Buffer): Color3 => {
			return new Color3(
				b.read(buffer.readu8, 1) / 255,
				b.read(buffer.readu8, 1) / 255,
				b.read(buffer.readu8, 1) / 255,
			);
		},
		write: (b: Buffer, value: Color3) => {
			b.write(buffer.writeu8, 1, math.round(255 * value.R));
			b.write(buffer.writeu8, 1, math.round(255 * value.G));
			b.write(buffer.writeu8, 1, math.round(255 * value.B));
		},
	};
	datatypes.buf = {
		read: (b: Buffer): buffer => {
			const bufLen = b.read(buffer.readu32, 4);
			const [readBuffer, readOffset] = b.pollBuffer(bufLen);
			const bufferValue = buffer.create(bufLen);
			buffer.copy(bufferValue, 0, readBuffer, readOffset, bufLen);
			return bufferValue;
		},
		write: (b: Buffer, value: buffer) => {
			const bufLen = buffer.len(value);
			b.write(buffer.writeu32, 4, bufLen);
			const offset = b.extendBuffer(bufLen);
			buffer.copy(b.buffer, offset, value);
		},
	};

	return datatypes as Datatypes;
}
const datatypes = getDatatypes();

type FormatData =
	| FormatKeys
	| { index: FormatKeys | undefined; value: FormatData }
	| { register_mask: string | string[]; data: FormatData }
	| { mask: string; data: FormatData }
	| { repeat: number; data: FormatData }
	| FormatData[];
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

class ReceiveSignalThread {
	private buffer: Buffer;
	private stopThread: boolean;

	receiveSignal(newBuffer: buffer) {
		this.buffer.receiveBuffer(newBuffer);
	}

	private parseArgs(formatData: FormatData, masks = new Map<string, boolean>()): unknown[] {
		const args: unknown[] = [];
		let argCount = 0;

		const parse = (formatData: FormatData, masks: Map<string, boolean>) => {
			if (typeIs(formatData, "string")) {
				//is string or number
				const value = (datatypes[formatData].read as ReadBuffer<unknown>)(this.buffer);
				args[argCount] = value;
				argCount += 1;
			} else if ("register_mask" in formatData) {
				const rawRegisterMasks = formatData.register_mask;
				const registerMasks = typeIs(rawRegisterMasks, "table") ? rawRegisterMasks : [rawRegisterMasks];
				const maskCount = registerMasks.size();
				const bools: boolean[] = [];
				let bitmask = getFormatForCount(maskCount).read(this.buffer);
				for (const _ of $range(0, maskCount - 1)) {
					bools.insert(0, !!(bitmask & 1));
					bitmask >>= 1;
				}

				const newMasks = deepcopy(masks);
				for (const i of $range(0, maskCount - 1)) {
					args[argCount + i] = bools[i];
					newMasks.set(registerMasks[i], bools[i]);
				}
				argCount += maskCount;
				parse(formatData.data, newMasks);
			} else if ("mask" in formatData) {
				const mask = formatData.mask;
				if (masks.get(mask)) {
					parse(formatData.data, masks);
				}
			} else if ("repeat" in formatData) {
				for (const _ of $range(0, formatData.repeat - 1)) {
					parse(formatData.data, masks);
				}
			} else if ("value" in formatData) {
				if (formatData.index) {
					//is dictionary
					const map = new Map();
					const mapSize = datatypes.u32.read(this.buffer);
					for (const _ of $range(0, mapSize - 1)) {
						const k = this.parseArgs(formatData.index, masks)[0];
						const v = this.parseArgs(formatData.value, masks);
						map.set(k, v.size() > 1 ? v : v[0]);
					}
					args[argCount] = map;
				} else {
					// //is array
					const arraySize = datatypes.u32.read(this.buffer);
					const array = new Array(arraySize);
					for (const i of $range(0, arraySize - 1)) {
						const v = this.parseArgs(formatData.value, masks);
						array[i] = v.size() > 1 ? v : v[0];
					}
					args[argCount] = array;
				}
				argCount += 1;
			} else {
				//is args list
				for (const subData of formatData) {
					parse(subData, masks);
				}
			}
		};
		parse(formatData, masks);
		return args;
	}

	stop() {
		this.stopThread = true;
	}

	constructor() {
		this.buffer = new Buffer();
		this.stopThread = false;

		task.spawn(() => {
			while (!this.stopThread) {
				const messageId = messageIdFormat.read(this.buffer);
				const args = this.parseArgs(messages[messageId].data);
				for (const callback of messageListeners[messageId]) {
					task.spawn(callback, ...deepcopy(args));
				}
			}
		});
	}
}
const signalReceiver = new ReceiveSignalThread();

const sendQueue: buffer[] = [];
let lastClock = os.clock();
const rateLimit = 60 / 1800;
let retryString: string | undefined;
const connection = RunService.Heartbeat.Connect(() => {
	const newClock = os.clock();
	const delta = newClock - lastClock;
	if (delta >= rateLimit) {
		lastClock = newClock - (delta - rateLimit);

		let response: RequestAsyncResponse | undefined = undefined;

		let sendString: string;
		if (retryString) {
			sendString = retryString;
		} else {
			const sendStrings: string[] = [];
			let queueSize = sendQueue.size();
			if (queueSize > 0) {
				let sendSize = 0;
				while (queueSize > 0 && sendSize < sendLimit) {
					const buf = sendQueue.shift()!;
					const bufferSize = buffer.len(buf);
					sendSize += bufferSize;
					queueSize -= 1;
					if (sendSize <= sendLimit) {
						sendStrings.push(buffer.tostring(buf));
					} else {
						const overflow = sendSize - sendLimit;
						sendStrings.push(buffer.readstring(buf, 0, overflow));
						const remainingBuffer = buffer.create(bufferSize - overflow);
						buffer.copy(remainingBuffer, 0, buf, overflow);
						sendQueue.insert(0, remainingBuffer);
					}
				}
			}
			sendString = sendStrings.join("");
		}

		try {
			response = HttpService.RequestAsync({
				Url: "http://localhost:50520",
				Method: "POST",
				Body: sendString,
			});
		} catch (error) {
			retryString = sendString;
			print(error);
			if (error === "Number of requests exceeded limit") {
				connection.Disconnect();
			}
		} finally {
			if (response) {
				retryString = undefined;
				if (response.Success) {
					const response_buffer = buffer.fromstring(response.Body);
					if (buffer.len(response_buffer) > 0) {
						signalReceiver.receiveSignal(response_buffer);
					}
				} else {
					print("Fail", response.StatusMessage);
				}
			}
		}
	}
});

export namespace Server {
	export function Hook(messageName: string, callback: Callback) {
		assert(messageName in receiveMessageIds);
		const messageId = receiveMessageIds[messageName];
		messageListeners[messageId].push(callback);
	}

	export function Unhook(messageName: string, callback: Callback) {
		assert(messageName in receiveMessageIds);
		const messageId = receiveMessageIds[messageName];
		const listeners = messageListeners[messageId];
		const index = listeners.indexOf(callback);
		if (index > -1) {
			listeners.remove(index);
		}
	}

	export function Fire(messageName: string, ...args: unknown[]) {
		assert(sendMessageIds[messageName]);
		const messageId = sendMessageIds[messageName];
		const rawBuffer = new Buffer();

		function parseArgs(formatData: FormatData, args: unknown, passedMasks = new Map<string, boolean>()) {
			const masks = deepcopy(passedMasks);
			let getArg: () => unknown;
			if (typeIs(args, "table")) {
				let argsCount = 0;
				getArg = () => {
					const arg = (args as unknown[])[argsCount];
					argsCount += 1;
					return arg;
				};
			} else {
				getArg = () => {
					return args;
				};
			}

			function parse(formatData: FormatData) {
				if (typeIs(formatData, "string")) {
					//is string or number
					(datatypes[formatData].write as WriteBuffer<unknown>)(rawBuffer, getArg());
				} else if ("register_mask" in formatData) {
					const rawRegisterMasks = formatData.register_mask;
					const registerMasks = typeIs(rawRegisterMasks, "table") ? rawRegisterMasks : [rawRegisterMasks];
					const maskCount = registerMasks.size();

					let bitmask = 0;
					for (const i of $range(0, maskCount - 1)) {
						const boolValue = getArg() as boolean;
						bitmask <<= 1;
						bitmask += boolValue ? 1 : 0;
						masks.set(registerMasks[i], boolValue);
					}
					getFormatForCount(maskCount).write(rawBuffer, bitmask);
				} else if ("mask" in formatData) {
					const mask = formatData.mask;
					if (masks.get(mask)) {
						parse(formatData.data);
					}
				} else if ("repeat" in formatData) {
					for (const _ of $range(0, formatData.repeat - 1)) {
						parse(formatData.data);
					}
				} else if ("value" in formatData) {
					if (formatData.index) {
						//is dictionary
						const map = getArg() as Map<unknown, unknown>;
						datatypes.u32.write(rawBuffer, map.size());
						for (const [k, v] of map) {
							parseArgs(formatData.index, k, masks);
							parseArgs(formatData.value, v, masks);
						}
					} else {
						//is array
						const array = getArg() as unknown[];
						datatypes.u32.write(rawBuffer, array.size());
						for (const v of array) {
							parseArgs(formatData.value, v, masks);
						}
					}
				} else {
					//is args list
					for (const subData of formatData) {
						parse(subData);
					}
				}
			}
			parse(formatData);
		}

		messageIdFormat.write(rawBuffer, messageId);
		parseArgs(messages[messageId].data, args);
		const sendBuffer = rawBuffer.toBuffer();
		sendQueue.push(sendBuffer);
	}

	export function Unloading() {
		connection.Disconnect();
		signalReceiver.stop();
	}
}
export default Server;
