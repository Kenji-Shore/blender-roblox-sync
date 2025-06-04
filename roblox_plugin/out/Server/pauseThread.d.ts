export interface PauseThread {
    thread?: thread;
    stopThread: boolean;
}
export declare namespace PauseThread {
    function pause(pauseThread: PauseThread): void;
    function unpause(pauseThread: PauseThread): void;
    function stop(pauseThread: PauseThread): void;
}
export default PauseThread;
