import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";
interface MaskFormatData {
    type: "mask";
    mask: string;
    invert?: boolean;
    data: ProcessFormats.FormatData;
}
export declare function read(receiveThread: ReceiveMessagesThread, args: defined[], formatData: MaskFormatData, masks: Map<string, boolean>): void;
export declare function write(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: MaskFormatData, masks: Map<string, boolean>): number;
export {};
