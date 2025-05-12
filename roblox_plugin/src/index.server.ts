//!native

import Server from "./server";
import { Mesh } from "./Mesh";
import { AssetService, Workspace } from "@rbxts/services";

export function makeHello(name: string) {
	return `Hello from ${name}!`;
}

const toolbar = plugin.CreateToolbar("test");
const button = toolbar.CreateButton("testbutton", "", "");
button.Click.Connect(() => {});

// const increment: number = (plugin.GetSetting("increment") as number | null) ?? 0;
// plugin.SetSetting("increment", increment + 1);
// print("plugin ran", increment, plugin.GetSetting("Rojo_confirmationBehavior"));

class Image {
	content: Content;
	assetId?: string;
	isAlpha: boolean;

	apply(meshPart: MeshPart, useImageTransparency: boolean) {
		if (useImageTransparency) {
			// && this.assetId) {
			meshPart.TextureContent = this.content;
			meshPart.Transparency = 0.02;
			// let surfaceAppearance = new Instance("SurfaceAppearance");
			// surfaceAppearance.AlphaMode = Enum.AlphaMode.Transparency;
			// surfaceAppearance.ColorMap = this.assetId;
			// surfaceAppearance.Parent = meshPart;
		} else {
			meshPart.TextureContent = this.content;
		}
	}

	constructor(imageBuffer: buffer) {
		const width = buffer.readu16(imageBuffer, 0);
		const height = buffer.readu16(imageBuffer, 2);
		const size = new Vector2(width, height);
		const image = AssetService.CreateEditableImage({ Size: size });

		const totalBytes = width * height * 4;
		const pixelsBuffer = buffer.create(totalBytes);
		buffer.copy(pixelsBuffer, 0, imageBuffer, 4);

		image.WritePixelsBuffer(Vector2.zero, size, pixelsBuffer);
		this.content = Content.fromObject(image);
		// if (this.isAlpha) {
		// 	const [result, assetId] = AssetService.CreateAssetAsync(this.content.Object!, Enum.AssetType.Image, {
		// 		Name: "test",
		// 	}) as LuaTuple<[Enum.CreateAssetResult, number]>;
		// 	if (result === Enum.CreateAssetResult.Success) {
		// 		this.assetId = `rbxassetid://${assetId}`;
		// 	}
		// }
	}
}

const meshes = new Map<string, Mesh>();
const images = new Map<string, Image>();
const objects = new Map<string, MeshObject>();

type MeshImageData = [
	hasImage: boolean,
	useImageTransparency: boolean,
	meshHash: string,
	alpha: number,
	imageHash?: string,
];
type ObjectData = [name: string, cframe: CFrame, size: Vector3, meshImages: MeshImageData[]];
class MeshObject {
	name: string;
	object: Model | MeshPart;

	constructor(objectData: ObjectData) {
		const [name, cframe, size, meshImages] = objectData;

		const separatedMeshes: MeshPart[] = [];
		for (const meshImage of meshImages) {
			const [hasImage, useImageTransparency, meshHash, alpha, imageHash] = meshImage;
			const sourceMesh = meshes.get(meshHash)!;
			const meshSize = sourceMesh.meshSize;
			const chunks = meshSize.mul(size).Max(meshSize).idiv(2048).add(Vector3.one);
			const mesh = new Mesh(sourceMesh, chunks);
			mesh.renderContent();
			for (const content of mesh.contents!) {
				const meshPart = AssetService.CreateMeshPartAsync(content, {
					CollisionFidelity: Enum.CollisionFidelity.Box,
					RenderFidelity: Enum.RenderFidelity.Precise,
					FluidFidelity: Enum.FluidFidelity.UseCollisionGeometry,
				});
				if (hasImage) {
					images.get(imageHash!)!.apply(meshPart, useImageTransparency);
				}
				meshPart.Material = Enum.Material.Fabric;
				meshPart.CastShadow = false;
				meshPart.CFrame = cframe;
				meshPart.Size = meshPart.Size.mul(size);
				if (!useImageTransparency) {
					meshPart.Transparency = 1 - alpha / 255;
				}
				separatedMeshes.push(meshPart);
			}
		}

		let object: Model | MeshPart;
		if (separatedMeshes.size() > 1) {
			object = new Instance("Model");
			for (const meshPart of separatedMeshes) {
				meshPart.Parent = object;
			}
		} else {
			object = separatedMeshes[0];
		}
		object.Name = name;
		object.Parent = Workspace;

		this.name = name;
		this.object = object;
	}
}

Server.Hook("sendObjects", (sendMeshes, sendImages, sendObjects) => {
	for (const [meshHash, meshBuffer] of sendMeshes as Map<string, buffer>) {
		const sourceMesh = new Mesh(meshBuffer);
		meshes.set(meshHash, sourceMesh);
	}
	for (const [imageHash, imageBuffer] of sendImages as Map<string, buffer>) {
		images.set(imageHash, new Image(imageBuffer));
	}
	for (const [objectHash, objectData] of sendObjects as Map<string, ObjectData>) {
		objects.set(objectHash, new MeshObject(objectData));
	}
});

plugin.Unloading.Connect(() => {
	Server.Unloading();
});
