//!native

import Server from "./Server";
import { MeshAsset } from "./MeshAsset";
import { ImageAsset } from "./ImageAsset";
import { Workspace } from "@rbxts/services";

// const toolbar = plugin.CreateToolbar("test");
// const button = toolbar.CreateButton("testbutton", "", "");
// button.Click.Connect(() => {});

export interface Consumer {
	instance?: Model | MeshPart;
	meshParts: MeshPart[];
	size: Vector3;
	useImageTransparency: boolean;
}

const meshes = new Map<string, MeshAsset>();
const images = new Map<string, ImageAsset>();
const objects = new Map<string, object>();

// Server.Hook("sendObjects", (sendMeshes, sendImages, sendObjects) => {
// 	for (const [meshHash, meshBuffer] of sendMeshes as Map<string, buffer>) {
// 		meshes.set(meshHash, MeshAsset.create(meshBuffer));
// 	}
// 	for (const [imageHash, imageBuffer] of sendImages as Map<string, buffer>) {
// 		images.set(imageHash, ImageAsset.create(imageBuffer));
// 	}
// 	for (const [objectHash, objectData] of sendObjects as Map<string, ObjectData>) {
// 		objects.set(objectHash, Object.create(objectData));
// 	}
// });

plugin.Unloading.Connect(() => {
	Server.Unloading();
});
