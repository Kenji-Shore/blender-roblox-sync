import type SendMessagesThread from "./sendMessages";
import type ReceiveMessagesThread from "./receiveMessages";
export type Values<T> = T[keyof T];
type SimpleFormats = "str" | "pos" | "pos2d" | "cf" | "vec" | "unitvec" | "hash" | "col" | "buf";
declare const DATATYPES: {
    readonly u8: 1;
    readonly i8: 1;
    readonly u16: 2;
    readonly i16: 2;
    readonly u32: 4;
    readonly i32: 4;
    readonly f32: 4;
    readonly f64: 8;
};
type Datatypes = typeof DATATYPES;
export type BufferFunctions = {
    [T in keyof Datatypes]: {
        size: Datatypes[T];
        read: (typeof buffer)[`read${T}`];
        write: (typeof buffer)[`write${T}`];
    };
};
type CountFormat = BufferFunctions["u8" | "u16" | "u32"];
export declare function getFormatForCount(count: number): CountFormat;
export type FormatData = Values<{
    [T in SimpleFormats]: {
        type: T;
    };
}> | {
    type: "format";
    totalSize: number;
    format: Values<BufferFunctions>[];
} | {
    type: "array";
    value: FormatData;
} | {
    type: "dict";
    index: FormatData;
    value: FormatData;
} | {
    type: "register_mask";
    register_mask: string[];
    count_format: CountFormat;
    data: FormatData;
} | {
    type: "mask";
    mask: string;
    invert?: boolean;
    data: FormatData;
} | {
    type: "repeat";
    repeat: number;
    data: FormatData;
} | FormatData[];
export type Callback = (...args: defined[]) => void;
export declare const messageListeners: Record<number, Callback[]>;
export declare function listenMessage(messageId: number, callback: Callback): void;
export declare function unlistenMessage(messageId: number, callback: Callback): void;
export declare const sendMessageIds: Map<string, number>;
export declare const receiveMessageIds: Map<string, number>;
export declare const messageFormats: FormatData[];
export declare const SEND_LIMIT = 20000000;
export declare const messageIdFormat: CountFormat;
export declare function deepcopy<T>(object: T): T;
type ReadFunc = (receiveThread: ReceiveMessagesThread, args: defined[], formatData: FormatData, masks: Map<string, boolean>) => void;
type WriteFunc = (sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: FormatData, masks: Map<string, boolean>) => number;
export declare const readFuncs: Map<string, ReadFunc>;
export declare const writeFuncs: Map<string, WriteFunc>;
export declare function initialize(): void;
export {};
