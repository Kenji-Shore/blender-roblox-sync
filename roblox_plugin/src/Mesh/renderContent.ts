//!native
import { Mesh } from "./index";
import { AssetService } from "@rbxts/services";

export function renderContent(this: Mesh) {
	const chunks = this.chunks;
	const editableMeshes = new Map<Vector3, EditableMesh>();
	const vertsMaps = new Map<Vector3, Map<number, number>>();
	const faceCounts = new Map<Vector3, number>();
	for (const x of $range(0, chunks.X - 1)) {
		for (const y of $range(0, chunks.Y - 1)) {
			for (const z of $range(0, chunks.Z - 1)) {
				const chunk = new Vector3(x, y, z);
				editableMeshes.set(chunk, AssetService.CreateEditableMesh());
				vertsMaps.set(chunk, new Map());
				faceCounts.set(chunk, 0);
			}
		}
	}

	const chunkSize = this.meshSize.div(chunks);
	const maxChunk = chunks.sub(Vector3.one);
	const minBounds = this.minBounds;
	const vertices = this.vertices;

	const fc1VI = this.fc1VI;
	const fc2VI = this.fc2VI;
	const fc3VI = this.fc3VI;

	const fc1N = this.fc1N;
	const fc2N = this.fc2N;
	const fc3N = this.fc3N;

	const fc1UV = this.fc1UV;
	const fc2UV = this.fc2UV;
	const fc3UV = this.fc3UV;

	const fc1Col = this.fc1Col;
	const fc1CA = this.fc1CA;
	const fc2Col = this.fc2Col;
	const fc2CA = this.fc2CA;
	const fc3Col = this.fc3Col;
	const fc3CA = this.fc3CA;
	for (const i of $range(0, this.trisCount - 1)) {
		const vi1 = fc1VI[i];
		const vi2 = fc2VI[i];
		const vi3 = fc3VI[i];
		const v1 = vertices[vi1];
		const v2 = vertices[vi2];
		const v3 = vertices[vi3];

		const centroid = v1.add(v2).add(v3).mul(0.3333);
		const chunk = centroid.sub(minBounds).idiv(chunkSize).Max(Vector3.zero).Min(maxChunk);
		const editableMesh = editableMeshes.get(chunk)!;
		const vertsMap = vertsMaps.get(chunk)!;

		const cvi1 = vertsMap.get(vi1) ?? editableMesh.AddVertex(v1);
		const cvi2 = vertsMap.get(vi2) ?? editableMesh.AddVertex(v2);
		const cvi3 = vertsMap.get(vi3) ?? editableMesh.AddVertex(v3);
		vertsMap.set(vi1, cvi1);
		vertsMap.set(vi2, cvi2);
		vertsMap.set(vi3, cvi3);
		const faceId = editableMesh.AddTriangle(cvi1, cvi2, cvi3);
		faceCounts.set(chunk, faceCounts.get(chunk)! + 1);
		editableMesh.SetFaceNormals(faceId, [
			editableMesh.AddNormal(fc1N[i]),
			editableMesh.AddNormal(fc2N[i]),
			editableMesh.AddNormal(fc3N[i]),
		]);
		if (this.hasUVs) {
			editableMesh.SetFaceUVs(faceId, [
				editableMesh.AddUV(fc1UV[i]),
				editableMesh.AddUV(fc2UV[i]),
				editableMesh.AddUV(fc3UV[i]),
			]);
		}
		if (this.hasColors) {
			editableMesh.SetFaceColors(faceId, [
				editableMesh.AddColor(fc1Col[i], fc1CA[i]),
				editableMesh.AddColor(fc2Col[i], fc2CA[i]),
				editableMesh.AddColor(fc3Col[i], fc3CA[i]),
			]);
		}
	}

	const contents: Content[] = [];
	this.contents = contents;
	for (const [chunk, editableMesh] of editableMeshes) {
		if (faceCounts.get(chunk)! > 0) {
			contents.push(Content.fromObject(editableMesh));
		}
	}
}
