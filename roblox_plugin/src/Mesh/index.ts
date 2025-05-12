//!native
import { loadFromBuffer } from "./loadFromBuffer";
import { loadFromMesh } from "./loadFromMesh";
import { renderContent } from "./renderContent";
import { splitMesh } from "./splitMesh";

export class Mesh {
	contents: Content[] | undefined;

	hasUVs: boolean;
	hasColors: boolean;

	minBounds: Vector3;
	maxBounds: Vector3;
	meshSize: Vector3;
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

	chunks: Vector3;
	protected edgeSplitEIs: Map<number, number>;
	protected edgeSplitAlphas: Map<number, number>;
	protected edgeSplitVIs: Map<number, number>;

	loadFromBuffer = loadFromBuffer;
	loadFromMesh = loadFromMesh;
	renderContent = renderContent;
	splitMesh = splitMesh;

	constructor(bufferOrMesh: buffer);
	constructor(bufferOrMesh: Mesh, chunks: Vector3);
	constructor(bufferOrMesh: buffer | Mesh, chunks?: Vector3) {
		if (typeIs(bufferOrMesh, "buffer")) {
			this.chunks = Vector3.one;
			this.loadFromBuffer(bufferOrMesh);
		} else {
			this.chunks = chunks!;
			this.loadFromMesh(bufferOrMesh);
			this.edgeSplitEIs = new Map();
			this.edgeSplitAlphas = new Map();
			this.edgeSplitVIs = new Map();
			for (const axis of ["X", "Y", "Z"] as ("X" | "Y" | "Z")[]) {
				const chunkCount = chunks![axis];
				const splitIncrement = 1 / chunkCount;
				let splitPoint = splitIncrement;
				for (const _ of $range(2, chunkCount)) {
					this.splitMesh(axis, splitPoint);
					splitPoint += splitIncrement;
				}
			}
		}
	}
}
