//!native

import { HttpService } from "@rbxts/services";
import { RunService } from "@rbxts/services";

import * as ProcessFormats from "./processFormats";
import SendMessagesThread from "./sendMessages";
import ReceiveMessagesThread from "./receiveMessages";
import PauseThread from "./pauseThread";

const sendThread = SendMessagesThread.create();
const receiveThread = ReceiveMessagesThread.create();
ProcessFormats.initialize();

let lastClock = os.clock();
const rateLimit = 60 / 1800;
let retryString: string | undefined;
const connection = RunService.Heartbeat.Connect(() => {
	const newClock = os.clock();
	const delta = newClock - lastClock;
	if (delta >= rateLimit) {
		lastClock = newClock - (delta - rateLimit);

		let response: RequestAsyncResponse | undefined = undefined;
		let sendString: string;
		if (retryString) {
			sendString = retryString;
		} else if (sendThread.buffersQueued.size() > 0) {
			const sendBuffer = sendThread.buffersQueued.shift()!;
			sendString = buffer.tostring(sendBuffer);
		} else {
			sendString = "";
		}

		try {
			response = HttpService.RequestAsync({
				Url: "http://localhost:50520",
				Method: "POST",
				Body: sendString,
			});
		} catch (error) {
			retryString = sendString;
			print(error === "HttpError: ConnectFail");
			if (error === "Number of requests exceeded limit") {
				connection.Disconnect();
			}
		} finally {
			if (response) {
				retryString = undefined;
				if (response.Success) {
					const responseBuffer = buffer.fromstring(response.Body);
					if (buffer.len(responseBuffer) > 0) {
						ReceiveMessagesThread.receiveMessage(receiveThread, responseBuffer);
					}
				} else {
					print("Fail", response.StatusMessage);
				}
			}
		}
	}
});

export namespace Server {
	export function hook(messageName: string, callback: ProcessFormats.Callback) {
		assert(messageName in ProcessFormats.receiveMessageIds);
		const messageId = ProcessFormats.receiveMessageIds.get(messageName)!;
		ProcessFormats.listenMessage(messageId, callback);
	}
	export function unhook(messageName: string, callback: ProcessFormats.Callback) {
		assert(messageName in ProcessFormats.receiveMessageIds);
		const messageId = ProcessFormats.receiveMessageIds.get(messageName)!;
		ProcessFormats.unlistenMessage(messageId, callback);
	}
	export function fire(messageName: string, ...args: defined[]) {
		SendMessagesThread.sendMessage(sendThread, messageName, ...args);
	}

	export function Unloading() {
		connection.Disconnect();
		PauseThread.stop(sendThread);
		PauseThread.stop(receiveThread);
	}
}
export default Server;
