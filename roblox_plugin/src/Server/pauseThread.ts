export interface PauseThread {
	thread?: thread;
}
export namespace PauseThread {
	export function pause(pauseThread: PauseThread) {
		pauseThread.thread = coroutine.running();
		coroutine.yield();
	}
	export function unpause(pauseThread: PauseThread) {
		if (pauseThread.thread) {
			const pausedThread = pauseThread.thread;
			pauseThread.thread = undefined;
			coroutine.resume(pausedThread);
		}
	}
}
export default PauseThread;
