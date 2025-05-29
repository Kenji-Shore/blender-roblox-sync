import { ServerStorage } from "@rbxts/services";

const STORE_NAME = "BlenderSyncHashStore";
interface Data {
	data: buffer;
	users: number;
}
const data = new Map<string, buffer>();
const store = ServerStorage.FindFirstChild(STORE_NAME) ?? new Instance("Folder", ServerStorage);
store.Name = STORE_NAME;

for (const hashData of store) {
}
export function setData(hash: string, data: buffer) {}

export function getData(hash: string) {}
