import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";
interface RepeatFormatData {
    type: "repeat";
    repeat: number;
    data: ProcessFormats.FormatData;
}
export declare function read(receiveThread: ReceiveMessagesThread, args: defined[], formatData: RepeatFormatData, masks: Map<string, boolean>): void;
export declare function write(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: RepeatFormatData, masks: Map<string, boolean>): number;
export {};
