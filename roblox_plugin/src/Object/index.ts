//!native
import { MeshAsset } from "../MeshAsset";
import { ImageAsset } from "../ImageAsset";
import { Workspace } from "@rbxts/services";

export interface Consumer {
	instance?: Model | MeshPart;
	meshParts: MeshPart[];
	size: Vector3;
	useImageTransparency: boolean;
}

type MeshImageData = [
	hasImage: boolean,
	useImageTransparency: boolean,
	meshHash: string,
	alpha: number,
	imageHash?: string,
];
type ObjectData = [name: string, cframe: CFrame, size: Vector3, meshImages: MeshImageData[]];

export interface Object {
	name: string;
	instance: Model | MeshPart;
	consumers: Consumer[];
}
export namespace Object {
	export function create(objectData: ObjectData): Object {
		const [name, cframe, size, meshImages] = objectData;

		const consumers: Consumer[] = [];
		for (const meshImage of meshImages) {
			const [hasImage, useImageTransparency, meshHash, alpha, imageHash] = meshImage;
			// const meshAsset = meshes.get(meshHash)!;

			// const consumer: Consumer = {
			// 	meshParts: [],
			// 	size: size,
			// 	useImageTransparency: useImageTransparency,
			// };
			// MeshAsset.addConsumer(meshAsset, consumer);
			// if (hasImage) {
			// 	ImageAsset.addConsumer(images.get(imageHash!), consumer);
			// }
			// for (const meshPart of consumer.meshParts) {
			// 	meshPart.Material = Enum.Material.Fabric;
			// 	meshPart.CastShadow = false;
			// 	meshPart.CFrame = cframe;
			// 	if (!useImageTransparency) {
			// 		meshPart.Transparency = 1 - alpha / 255;
			// 	}
			// }
			// consumers.push(consumer);
		}

		let instance: Model | MeshPart;
		if (consumers.size() > 1) {
			instance = new Instance("Model");
			for (const consumer of consumers) {
				consumer.instance!.Parent = instance;
			}
		} else {
			instance = consumers[0].instance!;
		}
		instance.Name = name;
		instance.Parent = Workspace;

		return {
			name: name,
			instance: instance,
			consumers: consumers,
		};
	}
}
export default Object;
