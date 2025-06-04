import * as ProcessFormats from "./processFormats";
import PauseThread from "./pauseThread";
export interface SendMessagesThread extends PauseThread {
    buffer: buffer[];
    bufLen: number;
    buffersQueued: buffer[];
    argsQueued: defined[][];
}
export declare namespace SendMessagesThread {
    function sendMessage(sendThread: SendMessagesThread, messageName: string, ...args: defined[]): void;
    function writeBuffer(sendThread: SendMessagesThread, data: buffer, dataSize: number): void;
    function parse(sendThread: SendMessagesThread, args: defined[], argsCount: number, formatData: ProcessFormats.FormatData, masks: Map<string, boolean>): number;
    function create(): SendMessagesThread;
}
export default SendMessagesThread;
