import * as ProcessFormats from "./processFormats";
import PauseThread from "./pauseThread";
export interface ReceiveMessagesThread extends PauseThread {
    buffer: buffer;
    bufLen: number;
    offset: number;
    buffersQueued: buffer[];
}
export declare namespace ReceiveMessagesThread {
    function receiveMessage(receiveThread: ReceiveMessagesThread, newBuffer: buffer): void;
    function readBuffer(receiveThread: ReceiveMessagesThread, dataSize: number): LuaTuple<[buffer, number]>;
    function parse(receiveThread: ReceiveMessagesThread, args: defined[], formatData: ProcessFormats.FormatData, masks: Map<string, boolean>): void;
    function create(): ReceiveMessagesThread;
}
export default ReceiveMessagesThread;
