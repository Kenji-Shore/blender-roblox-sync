import * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";
interface RegisterMaskFormatData {
    type: "register_mask";
    register_mask: string[];
    data: ProcessFormats.FormatData;
}
export declare function read(receiveThread: ReceiveMessagesThread, args: defined[], formatData: RegisterMaskFormatData, masks: Map<string, boolean>): void;
export declare function write(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: RegisterMaskFormatData, masks: Map<string, boolean>): number;
export {};
