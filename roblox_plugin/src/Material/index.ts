//!native
import { ImageAsset } from "../ImageAsset";
import { Workspace } from "@rbxts/services";

export type MaterialData = [
	name: string,
	hasImage: boolean,
	useImageTransparency: boolean,
	imageHash: string,
	alpha: number,
];
export interface Material {
	name: string;
	useImageTransparency: boolean;
	image?: ImageAsset;
	transparency: number;
	// consumers: Consumer[];
}
export namespace Material {
	export function create(materialData: MaterialData) {
		const [name, hasImage, useImageTransparency, imageHash, alpha] = materialData;

		// const consumers: Consumer[] = [];
		// for (const meshImage of meshImages) {
		// 	const [hasImage, useImageTransparency, meshHash, alpha, imageHash] = meshImage;
		// 	const meshAsset = meshes.get(meshHash)!;

		// 	const consumer: Consumer = {
		// 		meshParts: [],
		// 		size: size,
		// 		useImageTransparency: useImageTransparency,
		// 	};
		// 	MeshAsset.addConsumer(meshAsset, consumer);
		// 	if (hasImage) {
		// 		ImageAsset.addConsumer(images.get(imageHash), consumer);
		// 	}
		// 	for (const meshPart of consumer.meshParts) {
		// 		meshPart.Material = Enum.Material.Fabric;
		// 		meshPart.CastShadow = false;
		// 		meshPart.CFrame = cframe;
		// 		if (!useImageTransparency) {
		// 			meshPart.Transparency = 1 - alpha / 255;
		// 		}
		// 	}
		// 	consumers.push(consumer);
		// }

		let instance: Model | MeshPart;
		// if (consumers.size() > 1) {
		// 	instance = new Instance("Model");
		// 	for (const consumer of consumers) {
		// 		consumer.instance!.Parent = instance;
		// 	}
		// } else {
		// 	instance = consumers[0].instance!;
		// }
		// instance.Name = name;
		// instance.Parent = Workspace;

		// return {
		// 	name: name,
		// 	instance: instance,
		// 	consumers: consumers,
		// };
	}

	export function addConsumer() {}
}
export default Material;
