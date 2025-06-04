import type * as ProcessFormats from "../processFormats";
import SendMessagesThread from "../sendMessages";
import ReceiveMessagesThread from "../receiveMessages";
export declare function read(receiveThread: ReceiveMessagesThread, args: defined[], formatData: ProcessFormats.FormatData, masks: Map<string, boolean>): void;
export declare function write(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: ProcessFormats.FormatData, masks: Map<string, boolean>): number;
