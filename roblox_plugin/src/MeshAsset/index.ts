//!native
import { AssetService } from "@rbxts/services";
import { Consumer } from "../index.server";

import { loadFromBuffer } from "./loadFromBuffer";
import { loadFromMesh } from "./loadFromMesh";
import { renderContent } from "./renderContent";
import { splitMesh } from "./splitMesh";

export interface SourceMesh {
	// contents: Content[] | undefined;
	hasUVs: boolean;
	hasColors: boolean;

	vertices: Vector3[];

	vertsCount: number;
	edgesCount: number;
	trisCount: number;

	//edge: start vertex index, end vertex index
	edgeStartVIs: number[];
	edgeEndVIs: number[];
	edgeInvVecs: Vector3[];

	//face corners: vertex index
	fc1VI: number[];
	fc2VI: number[];
	fc3VI: number[];

	//face: edge index
	fEI1: number[];
	fEI2: number[];
	fEI3: number[];

	//face corners: normal
	fc1N: Vector3[];
	fc2N: Vector3[];
	fc3N: Vector3[];

	//face corners: UV
	fc1UV: Vector2[];
	fc2UV: Vector2[];
	fc3UV: Vector2[];

	//face corners: color and alpha
	fc1Col: Color3[];
	fc1CA: number[];
	fc2Col: Color3[];
	fc2CA: number[];
	fc3Col: Color3[];
	fc3CA: number[];
}

export interface SplitMesh extends SourceMesh {
	edgeSplitEIs: Map<number, number>;
	edgeSplitAlphas: Map<number, number>;
	edgeSplitVIs: Map<number, number>;
}

interface MeshConsumer {
	consumer: Consumer;
	resizeEvent: RBXScriptConnection;
}
export interface Split {
	divisions: Vector3;
	divisionCount: number;
	mesh: SourceMesh;
	consumers: MeshConsumer[];
	contents: Content[];
}

export interface MeshAsset {
	name: string;
	minBounds: Vector3;
	maxBounds: Vector3;
	meshSize: Vector3;
	sourceSplit: Split;
	splits: Split[];
}
export namespace MeshAsset {
	export function create(meshBuffer: buffer): MeshAsset {
		const [sourceMesh, minBounds, maxBounds] = loadFromBuffer(Vector3.one, meshBuffer);
		return {
			minBounds: minBounds,
			maxBounds: maxBounds,
			meshSize: maxBounds.sub(minBounds),
			sourceSplit: {
				divisions: Vector3.zero,
				divisionCount: 0,
				mesh: sourceMesh,
				consumers: [],
				contents: [],
			},
			splits: [],
		};
	}

	function createMeshPart(content: Content, size: Vector3): MeshPart {
		const meshPart = AssetService.CreateMeshPartAsync(content, {
			CollisionFidelity: Enum.CollisionFidelity.Box,
			RenderFidelity: Enum.RenderFidelity.Precise,
			FluidFidelity: Enum.FluidFidelity.UseCollisionGeometry,
		});
		meshPart.Anchored = true;
		meshPart.CanCollide = false;
		meshPart.CanTouch = false;
		meshPart.CanQuery = false;
		meshPart.Size = meshPart.Size.mul(size);
		return meshPart;
	}
	export function addConsumer(meshAsset: MeshAsset, consumer: Consumer) {
		const consumerSize = consumer.size;
		const meshSize = meshAsset.meshSize;
		const requiredSize = meshSize.mul(consumerSize).Max(meshSize);
		const requiredChunks = requiredSize.idiv(2048).add(Vector3.one);
		const divisions = new Vector3(
			math.log(requiredChunks.X, 2),
			math.log(requiredChunks.Y, 2),
			math.log(requiredChunks.Z, 2),
		).Ceil();

		let split: Split | undefined;
		let splitFrom: Split | undefined;
		let splitFromIndex = 0;
		const splits = meshAsset.splits;
		for (const i of $range(splits.size() - 1, 0, -1)) {
			const compareSplit = splits[i];
			const compareDivisions = compareSplit.divisions;
			if (divisions.sub(compareDivisions).Max(Vector3.zero) !== Vector3.zero) {
				if (divisions === compareDivisions) {
					split = compareSplit;
				} else {
					splitFrom = compareSplit;
					splitFromIndex = i;
				}
				break;
			}
		}

		if (!split) {
			splitFrom ??= meshAsset.sourceSplit;
			const startDivisions = splitFrom.divisions;
			const minBounds = meshAsset.minBounds;
			const maxBounds = meshAsset.maxBounds;
			const newMesh = loadFromMesh(splitFrom.mesh);
			for (const axis of ["X", "Y", "Z"] as ("X" | "Y" | "Z")[]) {
				const startDivision = startDivisions[axis];
				let splitSize = meshSize[axis] / math.pow(2, startDivision);

				const minBound = minBounds[axis];
				const maxBound = maxBounds[axis];
				for (const _ of $range(startDivision + 1, divisions[axis])) {
					const newSplitSize = splitSize * 0.5;
					for (const splitPos of $range(minBound + newSplitSize, maxBound - newSplitSize, splitSize)) {
						splitMesh(newMesh, axis, splitPos);
					}
					splitSize = newSplitSize;
				}
			}

			const divisionCount = divisions.X + divisions.Y + divisions.Z;
			split = {
				divisions: divisions,
				divisionCount: divisionCount,
				mesh: newMesh,
				consumers: [],
				contents: [],
			};
			renderContent(meshAsset, split);

			const splitsSize = splits.size();
			let insertIndex = splitsSize;
			for (const i of $range(splitFromIndex + 1, splitsSize - 1)) {
				if (divisionCount <= splits[i].divisionCount) {
					insertIndex = i;
					break;
				}
			}
			splits.insert(insertIndex, split);
		}

		let resizeEvent: RBXScriptConnection;
		const contents = split.contents;
		consumer.meshParts.clear();
		if (contents.size() === 1) {
			const meshPart = createMeshPart(contents[0], consumerSize);
			consumer.instance = meshPart;
			consumer.meshParts.push(meshPart);
			resizeEvent = meshPart.GetPropertyChangedSignal("Size").Connect(() => {
				print("hi");
			});
		} else {
			const model = new Instance("Model");
			let rootMesh: MeshPart;
			for (const content of contents) {
				const meshPart = createMeshPart(content, consumerSize);
				consumer.meshParts.push(meshPart);
				meshPart.Parent = model;
				rootMesh = meshPart;
			}
			model.PrimaryPart = rootMesh!;
			consumer.instance = model;
			resizeEvent = rootMesh!.GetPropertyChangedSignal("Size").Connect(() => {
				print("hi");
			});
		}
		const meshConsumer: MeshConsumer = {
			consumer: consumer,
			resizeEvent: resizeEvent,
		};
		split.consumers.push(meshConsumer);
	}
}
export default MeshAsset;
