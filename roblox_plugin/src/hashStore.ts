// import { ServerStorage } from "@rbxts/services";
// import { Server } from "./server";

// const STORE_NAME = "BlenderSyncHashStore";
// const store = ServerStorage.FindFirstChild(STORE_NAME) ?? new Instance("Folder", ServerStorage);
// store.Name = STORE_NAME;

// interface HashValue {
// 	data: buffer;
// 	users: number;
// }

// export namespace HashStore {
// 	const data = new Map<string, buffer>();
// 	export function init() {
// 		for (const hashData of store) {
// 		}
// 	}
// 	function set(hash: string, data: buffer) {}

// 	export function get(hash: string) {}

// 	Server.Hook("sendHash", (sendMeshes, sendImages, sendObjects) => {
// 		for (const [meshHash, meshBuffer] of sendMeshes as Map<string, buffer>) {
// 			meshes.set(meshHash, MeshAsset.create(meshBuffer));
// 		}
// 		for (const [imageHash, imageBuffer] of sendImages as Map<string, buffer>) {
// 			images.set(imageHash, ImageAsset.create(imageBuffer));
// 		}
// 		for (const [objectHash, objectData] of sendObjects as Map<string, ObjectData>) {
// 			objects.set(objectHash, Object.create(objectData));
// 		}
// 	});
// }

// // const increment: number = (plugin.GetSetting("increment") as number | null) ?? 0;
// // plugin.SetSetting("increment", increment + 1);
// // print("plugin ran", increment, plugin.GetSetting("Rojo_confirmationBehavior"));
