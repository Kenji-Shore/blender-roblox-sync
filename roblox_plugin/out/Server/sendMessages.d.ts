import PauseThread from "./pauseThread";
interface SendMessagesThread extends PauseThread {
    buffer: buffer[];
    bufLen: number;
    buffersQueued: buffer[];
    argsQueued: unknown[][];
}
export declare namespace SendMessagesThread {
    function sendMessage(sendThread: SendMessagesThread, messageName: string, ...args: defined[]): void;
    function writeBuffer(sendThread: SendMessagesThread, data: buffer): void;
}
export default SendMessagesThread;
