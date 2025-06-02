//!native

import { HttpService } from "@rbxts/services";
import { RunService } from "@rbxts/services";

// const signalReceiver = new ReceiveSignalThread();

// const sendQueue: buffer[] = [];
// let lastClock = os.clock();
// const rateLimit = 60 / 1800;
// let retryString: string | undefined;
// const connection = RunService.Heartbeat.Connect(() => {
// 	const newClock = os.clock();
// 	const delta = newClock - lastClock;
// 	if (delta >= rateLimit) {
// 		lastClock = newClock - (delta - rateLimit);

// 		let response: RequestAsyncResponse | undefined = undefined;

// 		let sendString: string;
// 		if (retryString) {
// 			sendString = retryString;
// 		} else {
// 			const sendStrings: string[] = [];
// 			let queueSize = sendQueue.size();
// 			if (queueSize > 0) {
// 				let sendSize = 0;
// 				while (queueSize > 0 && sendSize < sendLimit) {
// 					const buf = sendQueue.shift()!;
// 					const bufferSize = buffer.len(buf);
// 					sendSize += bufferSize;
// 					queueSize -= 1;
// 					if (sendSize <= sendLimit) {
// 						sendStrings.push(buffer.tostring(buf));
// 					} else {
// 						const overflow = sendSize - sendLimit;
// 						sendStrings.push(buffer.readstring(buf, 0, overflow));
// 						const remainingBuffer = buffer.create(bufferSize - overflow);
// 						buffer.copy(remainingBuffer, 0, buf, overflow);
// 						sendQueue.insert(0, remainingBuffer);
// 					}
// 				}
// 			}
// 			sendString = sendStrings.join("");
// 		}

// 		try {
// 			response = HttpService.RequestAsync({
// 				Url: "http://localhost:50520",
// 				Method: "POST",
// 				Body: sendString,
// 			});
// 		} catch (error) {
// 			retryString = sendString;
// 			print(error);
// 			if (error === "Number of requests exceeded limit") {
// 				connection.Disconnect();
// 			}
// 		} finally {
// 			if (response) {
// 				retryString = undefined;
// 				if (response.Success) {
// 					const response_buffer = buffer.fromstring(response.Body);
// 					if (buffer.len(response_buffer) > 0) {
// 						signalReceiver.receiveSignal(response_buffer);
// 					}
// 				} else {
// 					print("Fail", response.StatusMessage);
// 				}
// 			}
// 		}
// 	}
// });

// export namespace Server {
// 	export function Hook(messageName: string, callback: Callback) {
// 		assert(messageName in receiveMessageIds);
// 		const messageId = receiveMessageIds[messageName];
// 		messageListeners[messageId].push(callback);
// 	}

// 	export function Unhook(messageName: string, callback: Callback) {
// 		assert(messageName in receiveMessageIds);
// 		const messageId = receiveMessageIds[messageName];
// 		const listeners = messageListeners[messageId];
// 		const index = listeners.indexOf(callback);
// 		if (index > -1) {
// 			listeners.remove(index);
// 		}
// 	}

// 	export function Unloading() {
// 		connection.Disconnect();
// 		signalReceiver.stop();
// 	}
// }
// export default Server;
