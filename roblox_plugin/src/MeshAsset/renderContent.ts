//!native
import { MeshAsset, Split } from "./index";
import { AssetService } from "@rbxts/services";

export function renderContent(meshAsset: MeshAsset, split: Split) {
	const divisions = split.divisions;
	const chunks = new Vector3(math.pow(2, divisions.X), math.pow(2, divisions.Y), math.pow(2, divisions.Z));
	const editableRawMeshes = new Map<Vector3, EditableMesh>();
	const vertsMaps = new Map<Vector3, Map<number, number>>();
	const faceCounts = new Map<Vector3, number>();
	for (const x of $range(0, chunks.X - 1)) {
		for (const y of $range(0, chunks.Y - 1)) {
			for (const z of $range(0, chunks.Z - 1)) {
				const chunk = new Vector3(x, y, z);
				editableRawMeshes.set(chunk, AssetService.CreateEditableMesh());
				vertsMaps.set(chunk, new Map());
				faceCounts.set(chunk, 0);
			}
		}
	}

	const chunkSize = meshAsset.meshSize.div(chunks);
	const maxChunk = chunks.sub(Vector3.one);
	const minBounds = meshAsset.minBounds;
	const mesh = split.mesh;
	const vertices = mesh.vertices;

	const fc1VI = mesh.fc1VI;
	const fc2VI = mesh.fc2VI;
	const fc3VI = mesh.fc3VI;

	const fc1N = mesh.fc1N;
	const fc2N = mesh.fc2N;
	const fc3N = mesh.fc3N;

	const fc1UV = mesh.fc1UV;
	const fc2UV = mesh.fc2UV;
	const fc3UV = mesh.fc3UV;

	const fc1Col = mesh.fc1Col;
	const fc1CA = mesh.fc1CA;
	const fc2Col = mesh.fc2Col;
	const fc2CA = mesh.fc2CA;
	const fc3Col = mesh.fc3Col;
	const fc3CA = mesh.fc3CA;
	for (const i of $range(0, mesh.trisCount - 1)) {
		const vi1 = fc1VI[i];
		const vi2 = fc2VI[i];
		const vi3 = fc3VI[i];
		const v1 = vertices[vi1];
		const v2 = vertices[vi2];
		const v3 = vertices[vi3];

		const centroid = v1.add(v2).add(v3).mul(0.3333);
		const chunk = centroid.sub(minBounds).idiv(chunkSize).Max(Vector3.zero).Min(maxChunk);
		const editableRawMesh = editableRawMeshes.get(chunk)!;
		const vertsMap = vertsMaps.get(chunk)!;

		const cvi1 = vertsMap.get(vi1) ?? editableRawMesh.AddVertex(v1);
		const cvi2 = vertsMap.get(vi2) ?? editableRawMesh.AddVertex(v2);
		const cvi3 = vertsMap.get(vi3) ?? editableRawMesh.AddVertex(v3);
		vertsMap.set(vi1, cvi1);
		vertsMap.set(vi2, cvi2);
		vertsMap.set(vi3, cvi3);
		const faceId = editableRawMesh.AddTriangle(cvi1, cvi2, cvi3);
		faceCounts.set(chunk, faceCounts.get(chunk)! + 1);
		editableRawMesh.SetFaceNormals(faceId, [
			editableRawMesh.AddNormal(fc1N[i]),
			editableRawMesh.AddNormal(fc2N[i]),
			editableRawMesh.AddNormal(fc3N[i]),
		]);
		if (mesh.hasUVs) {
			editableRawMesh.SetFaceUVs(faceId, [
				editableRawMesh.AddUV(fc1UV[i]),
				editableRawMesh.AddUV(fc2UV[i]),
				editableRawMesh.AddUV(fc3UV[i]),
			]);
		}
		if (mesh.hasColors) {
			editableRawMesh.SetFaceColors(faceId, [
				editableRawMesh.AddColor(fc1Col[i], fc1CA[i]),
				editableRawMesh.AddColor(fc2Col[i], fc2CA[i]),
				editableRawMesh.AddColor(fc3Col[i], fc3CA[i]),
			]);
		}
	}

	const contents = split.contents;
	for (const [chunk, editableRawMesh] of editableRawMeshes) {
		if (faceCounts.get(chunk)! > 0) {
			contents.push(Content.fromObject(editableRawMesh));
		}
	}
}
