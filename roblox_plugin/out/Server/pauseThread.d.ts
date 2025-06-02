export interface PauseThread {
    thread?: thread;
}
export declare namespace PauseThread {
    function pause(pauseThread: PauseThread): void;
    function unpause(pauseThread: PauseThread): void;
}
export default PauseThread;
