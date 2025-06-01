//!native
import { AssetService } from "@rbxts/services";

export interface ImageAsset {
	name: string;
	content: Content;
}
export namespace ImageAsset {
	const imageAssets = new Map<string, ImageAsset>();
	export function update(imageHash: string, imageBuffer: buffer) {
		const width = buffer.readu16(imageBuffer, 0);
		const height = buffer.readu16(imageBuffer, 2);
		const size = new Vector2(width, height);
		const image = AssetService.CreateEditableImage({ Size: size });

		const totalBytes = width * height * 4;
		const pixelsBuffer = buffer.create(totalBytes);
		buffer.copy(pixelsBuffer, 0, imageBuffer, 4);

		image.WritePixelsBuffer(Vector2.zero, size, pixelsBuffer);
		const content = Content.fromObject(image);
		//if (imageAssets)
	}
	export function create(imageBuffer: buffer): ImageAsset {
		const width = buffer.readu16(imageBuffer, 0);
		const height = buffer.readu16(imageBuffer, 2);
		const size = new Vector2(width, height);
		const image = AssetService.CreateEditableImage({ Size: size });

		const totalBytes = width * height * 4;
		const pixelsBuffer = buffer.create(totalBytes);
		buffer.copy(pixelsBuffer, 0, imageBuffer, 4);

		image.WritePixelsBuffer(Vector2.zero, size, pixelsBuffer);
		return {
			name: "test",
			content: Content.fromObject(image),
			// consumers: [],
		};
	}

	// export function addConsumer(imageAsset: ImageAsset, consumer: Consumer) {
	// 	const imageConsumer: ImageConsumer = {
	// 		consumer: consumer,
	// 	};
	// 	imageAsset.consumers.push(imageConsumer);
	// 	if (consumer.useImageTransparency) {
	// 		for (const meshPart of consumer.meshParts) {
	// 			meshPart.TextureContent = imageAsset.content;
	// 			meshPart.Transparency = 0.02;
	// 			// let surfaceAppearance = new Instance("SurfaceAppearance");
	// 			// surfaceAppearance.AlphaMode = Enum.AlphaMode.Transparency;
	// 			// surfaceAppearance.ColorMap = this.assetId;
	// 			// surfaceAppearance.Parent = meshPart;
	// 		}
	// 	} else {
	// 		for (const meshPart of consumer.meshParts) {
	// 			meshPart.TextureContent = imageAsset.content;
	// 		}
	// 	}
	// }
}
export default ImageAsset;
