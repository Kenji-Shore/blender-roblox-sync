import * as ProcessFormats from "./processFormats";
export declare namespace Server {
    function hook(messageName: string, callback: ProcessFormats.Callback): void;
    function unhook(messageName: string, callback: ProcessFormats.Callback): void;
    function fire(messageName: string, ...args: defined[]): void;
    function Unloading(): void;
}
export default Server;
