import * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";
interface DictFormatData {
    type: "dict";
    index: ProcessFormats.FormatData;
    value: ProcessFormats.FormatData;
}
export declare function read(receiveThread: ReceiveMessagesThread, args: defined[], formatData: DictFormatData, masks: Map<string, boolean>): void;
export declare function write(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: DictFormatData, masks: Map<string, boolean>): number;
export {};
