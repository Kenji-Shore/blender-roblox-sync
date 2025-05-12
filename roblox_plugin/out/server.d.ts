type Callback = (...args: unknown[]) => void;
export declare namespace Server {
    function Hook(messageName: string, callback: Callback): void;
    function Unhook(messageName: string, callback: Callback): void;
    function Fire(messageName: string, ...args: unknown[]): void;
    function Unloading(): void;
}
export default Server;
