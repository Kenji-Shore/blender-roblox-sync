import * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";
interface ArrayFormatData {
    type: "array";
    value: ProcessFormats.FormatData;
}
export declare function read(receiveThread: ReceiveMessagesThread, args: defined[], formatData: ArrayFormatData, masks: Map<string, boolean>): void;
export declare function write(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: ArrayFormatData, masks: Map<string, boolean>): number;
export {};
