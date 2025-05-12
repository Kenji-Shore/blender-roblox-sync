//!native
import { Mesh } from "./index";

export function loadFromMesh(this: Mesh, mesh: Mesh) {
	assert(mesh.chunks === Vector3.one); //can only load from a source (undivided) mesh
	this.hasUVs = mesh.hasUVs;
	this.hasColors = mesh.hasColors;

	this.minBounds = mesh.minBounds;
	this.maxBounds = mesh.maxBounds;
	this.meshSize = mesh.meshSize;
	this.vertices = table.clone(mesh.vertices);

	//edge: start vertex index, end vertex index
	this.edgeStartVIs = table.clone(mesh.edgeStartVIs);
	this.edgeEndVIs = table.clone(mesh.edgeEndVIs);
	this.edgeInvVecs = table.clone(mesh.edgeInvVecs);

	this.vertsCount = mesh.vertsCount;
	this.edgesCount = mesh.edgesCount;
	this.trisCount = mesh.trisCount;
	//face corners: vertex index
	this.fc1VI = table.clone(mesh.fc1VI);
	this.fc2VI = table.clone(mesh.fc2VI);
	this.fc3VI = table.clone(mesh.fc3VI);

	//face: edge index
	this.fEI1 = table.clone(mesh.fEI1);
	this.fEI2 = table.clone(mesh.fEI2);
	this.fEI3 = table.clone(mesh.fEI3);

	//face corners: normal
	this.fc1N = table.clone(mesh.fc1N);
	this.fc2N = table.clone(mesh.fc2N);
	this.fc3N = table.clone(mesh.fc3N);

	//face corners: UV
	this.fc1UV = table.clone(mesh.fc1UV);
	this.fc2UV = table.clone(mesh.fc2UV);
	this.fc3UV = table.clone(mesh.fc3UV);

	//face corners: color and alpha
	this.fc1Col = table.clone(mesh.fc1Col);
	this.fc1CA = table.clone(mesh.fc1CA);
	this.fc2Col = table.clone(mesh.fc2Col);
	this.fc2CA = table.clone(mesh.fc2CA);
	this.fc3Col = table.clone(mesh.fc3Col);
	this.fc3CA = table.clone(mesh.fc3CA);
}
