export interface PauseThread {
	thread?: thread;
	stopThread: boolean;
}
export namespace PauseThread {
	export function pause(pauseThread: PauseThread) {
		pauseThread.thread = coroutine.running();
		coroutine.yield();
	}
	export function unpause(pauseThread: PauseThread) {
		if (pauseThread.thread) {
			const thread = pauseThread.thread;
			pauseThread.thread = undefined;
			if (pauseThread.stopThread) {
				coroutine.close(thread);
			} else {
				coroutine.resume(thread);
			}
		}
	}
	export function stop(pauseThread: PauseThread) {
		pauseThread.stopThread = true;
	}
}
export default PauseThread;
