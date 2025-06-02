import PauseThread from "./pauseThread";
export interface ReceiveMessagesThread extends PauseThread {
    buffer: buffer;
    bufLen: number;
    offset: number;
    buffersQueued: buffer[];
    argsQueued: unknown[][];
}
export declare namespace ReceiveMessagesThread {
    function receiveMessage(receiveThread: ReceiveMessagesThread, newBuffer: buffer): void;
    function readBuffer(receiveThread: ReceiveMessagesThread, dataSize: number): LuaTuple<[buffer, number]>;
    function test(): void;
}
export default ReceiveMessagesThread;
