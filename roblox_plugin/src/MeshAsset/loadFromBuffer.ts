//!native
import { SourceMesh } from "./index";

const INV_NORMAL = 1 / 127;
const INV_COLOR = 1 / 255;
export function loadFromBuffer(chunks: Vector3, meshBuffer: buffer): LuaTuple<[SourceMesh, Vector3, Vector3]> {
	let offset = 0;
	let flags = buffer.readu8(meshBuffer, offset);
	offset += 1;

	const hasColors = !!(flags & 1);
	flags >>= 1;
	const hasUVs = !!(flags & 1);

	let minX = math.huge;
	let maxX = -math.huge;
	let minY = math.huge;
	let maxY = -math.huge;
	let minZ = math.huge;
	let maxZ = -math.huge;
	const vertices: Vector3[] = [];

	let edgesCount = 0;
	const edgeMap = new Map<Vector3, number>();
	const edgeStartVIs: number[] = [];
	const edgeEndVIs: number[] = [];
	const edgeInvVecs: Vector3[] = [];

	const fc1VI: number[] = [];
	const fc2VI: number[] = [];
	const fc3VI: number[] = [];

	const fEI1: number[] = [];
	const fEI2: number[] = [];
	const fEI3: number[] = [];

	const fc1N: Vector3[] = [];
	const fc2N: Vector3[] = [];
	const fc3N: Vector3[] = [];

	const fc1UV: Vector2[] = [];
	const fc2UV: Vector2[] = [];
	const fc3UV: Vector2[] = [];

	const fc1Col: Color3[] = [];
	const fc1CA: number[] = [];
	const fc2Col: Color3[] = [];
	const fc2CA: number[] = [];
	const fc3Col: Color3[] = [];
	const fc3CA: number[] = [];

	const vertsCount = buffer.readu16(meshBuffer, offset);
	offset += 2;
	for (const i of $range(0, vertsCount - 1)) {
		const x = buffer.readf32(meshBuffer, offset + 4);
		const y = buffer.readf32(meshBuffer, offset + 8);
		const z = buffer.readf32(meshBuffer, offset);
		offset += 12;

		minX = math.min(minX, x);
		maxX = math.max(maxX, x);
		minY = math.min(minY, y);
		maxY = math.max(maxY, y);
		minZ = math.min(minZ, z);
		maxZ = math.max(maxZ, z);
		vertices[i] = new Vector3(x, y, z);
	}

	const trisCount = buffer.readu16(meshBuffer, offset);
	offset += 2;
	for (const _ of $range(0, trisCount - 1)) {
		const vi1 = buffer.readu16(meshBuffer, offset);
		const vi2 = buffer.readu16(meshBuffer, offset + 2);
		const vi3 = buffer.readu16(meshBuffer, offset + 4);
		offset += 6;

		const eh1 = new Vector3(math.min(vi1, vi2), math.max(vi1, vi2));
		const eh2 = new Vector3(math.min(vi1, vi3), math.max(vi1, vi3));
		const eh3 = new Vector3(math.min(vi2, vi3), math.max(vi2, vi3));
		let ei1: number | undefined = edgeMap.get(eh1);
		let ei2: number | undefined = edgeMap.get(eh2);
		let ei3: number | undefined = edgeMap.get(eh3);
		if (ei1 === undefined) {
			ei1 = edgesCount;
			edgeMap.set(eh1, ei1);
			edgeStartVIs.push(vi1);
			edgeEndVIs.push(vi2);
			edgeInvVecs.push(Vector3.one.div(vertices[vi1].sub(vertices[vi2])));
			edgesCount += 1;
		}
		if (ei2 === undefined) {
			ei2 = edgesCount;
			edgeMap.set(eh2, ei2);
			edgeStartVIs.push(vi1);
			edgeEndVIs.push(vi3);
			edgeInvVecs.push(Vector3.one.div(vertices[vi1].sub(vertices[vi3])));
			edgesCount += 1;
		}
		if (ei3 === undefined) {
			ei3 = edgesCount;
			edgeMap.set(eh3, ei3);
			edgeStartVIs.push(vi2);
			edgeEndVIs.push(vi3);
			edgeInvVecs.push(Vector3.one.div(vertices[vi2].sub(vertices[vi3])));
			edgesCount += 1;
		}

		fc1VI.push(vi1);
		fc2VI.push(vi2);
		fc3VI.push(vi3);
		fEI1.push(ei1);
		fEI2.push(ei2);
		fEI3.push(ei3);
	}
	for (const _ of $range(0, trisCount - 1)) {
		fc1N.push(
			new Vector3(
				buffer.readi8(meshBuffer, offset + 1),
				buffer.readi8(meshBuffer, offset + 2),
				buffer.readi8(meshBuffer, offset),
			).mul(INV_NORMAL),
		);
		fc2N.push(
			new Vector3(
				buffer.readi8(meshBuffer, offset + 4),
				buffer.readi8(meshBuffer, offset + 5),
				buffer.readi8(meshBuffer, offset + 3),
			).mul(INV_NORMAL),
		);
		fc3N.push(
			new Vector3(
				buffer.readi8(meshBuffer, offset + 7),
				buffer.readi8(meshBuffer, offset + 8),
				buffer.readi8(meshBuffer, offset + 6),
			).mul(INV_NORMAL),
		);
		offset += 9;
	}

	if (hasUVs) {
		for (const _ of $range(0, trisCount - 1)) {
			fc1UV.push(new Vector2(buffer.readf32(meshBuffer, offset), buffer.readf32(meshBuffer, offset + 4)));
			fc2UV.push(new Vector2(buffer.readf32(meshBuffer, offset + 8), buffer.readf32(meshBuffer, offset + 12)));
			fc3UV.push(new Vector2(buffer.readf32(meshBuffer, offset + 16), buffer.readf32(meshBuffer, offset + 20)));
			offset += 24;
		}
	}

	if (hasColors) {
		for (const _ of $range(0, trisCount - 1)) {
			fc1Col.push(
				Color3.fromRGB(
					buffer.readu8(meshBuffer, offset + 0),
					buffer.readu8(meshBuffer, offset + 1),
					buffer.readu8(meshBuffer, offset + 2),
				),
			);
			fc1CA.push(buffer.readu8(meshBuffer, offset + 3) * INV_COLOR);

			fc2Col.push(
				Color3.fromRGB(
					buffer.readu8(meshBuffer, offset + 4),
					buffer.readu8(meshBuffer, offset + 5),
					buffer.readu8(meshBuffer, offset + 6),
				),
			);
			fc2CA.push(buffer.readu8(meshBuffer, offset + 7) * INV_COLOR);

			fc3Col.push(
				Color3.fromRGB(
					buffer.readu8(meshBuffer, offset + 8),
					buffer.readu8(meshBuffer, offset + 9),
					buffer.readu8(meshBuffer, offset + 10),
				),
			);
			fc3CA.push(buffer.readu8(meshBuffer, offset + 11) * INV_COLOR);
			offset += 12;
		}
	}

	return $tuple(
		{
			chunks: chunks,
			hasUVs: hasUVs,
			hasColors: hasColors,
			vertices: vertices,

			edgeStartVIs: edgeStartVIs,
			edgeEndVIs: edgeEndVIs,
			edgeInvVecs: edgeInvVecs,

			fc1VI: fc1VI,
			fc2VI: fc2VI,
			fc3VI: fc3VI,

			fEI1: fEI1,
			fEI2: fEI2,
			fEI3: fEI3,

			fc1N: fc1N,
			fc2N: fc2N,
			fc3N: fc3N,

			fc1UV: fc1UV,
			fc2UV: fc2UV,
			fc3UV: fc3UV,

			fc1Col: fc1Col,
			fc1CA: fc1CA,
			fc2Col: fc2Col,
			fc2CA: fc2CA,
			fc3Col: fc3Col,
			fc3CA: fc3CA,

			vertsCount: vertsCount,
			trisCount: trisCount,
			edgesCount: edgesCount,
		},
		new Vector3(minX, minY, minZ),
		new Vector3(maxX, maxY, maxZ),
	);
}
