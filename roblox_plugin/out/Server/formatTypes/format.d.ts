import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";
interface FormatFormatData {
    type: "format";
    totalSize: number;
    format: ProcessFormats.Values<ProcessFormats.BufferFunctions>[];
}
export declare function read(receiveThread: ReceiveMessagesThread, args: defined[], formatData: FormatFormatData, masks: Map<string, boolean>): void;
export declare function write(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: FormatFormatData, masks: Map<string, boolean>): number;
export {};
