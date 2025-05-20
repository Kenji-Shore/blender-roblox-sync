--!native
-- Compiled with roblox-ts v3.0.0
local function loadFromMesh(copyFrom)
	return {
		edgeSplitEIs = {},
		edgeSplitAlphas = {},
		edgeSplitVIs = {},
		hasUVs = copyFrom.hasUVs,
		hasColors = copyFrom.hasColors,
		vertices = table.clone(copyFrom.vertices),
		edgeStartVIs = table.clone(copyFrom.edgeStartVIs),
		edgeEndVIs = table.clone(copyFrom.edgeEndVIs),
		edgeInvVecs = table.clone(copyFrom.edgeInvVecs),
		vertsCount = copyFrom.vertsCount,
		edgesCount = copyFrom.edgesCount,
		trisCount = copyFrom.trisCount,
		fc1VI = table.clone(copyFrom.fc1VI),
		fc2VI = table.clone(copyFrom.fc2VI),
		fc3VI = table.clone(copyFrom.fc3VI),
		fEI1 = table.clone(copyFrom.fEI1),
		fEI2 = table.clone(copyFrom.fEI2),
		fEI3 = table.clone(copyFrom.fEI3),
		fc1N = table.clone(copyFrom.fc1N),
		fc2N = table.clone(copyFrom.fc2N),
		fc3N = table.clone(copyFrom.fc3N),
		fc1UV = table.clone(copyFrom.fc1UV),
		fc2UV = table.clone(copyFrom.fc2UV),
		fc3UV = table.clone(copyFrom.fc3UV),
		fc1Col = table.clone(copyFrom.fc1Col),
		fc1CA = table.clone(copyFrom.fc1CA),
		fc2Col = table.clone(copyFrom.fc2Col),
		fc2CA = table.clone(copyFrom.fc2CA),
		fc3Col = table.clone(copyFrom.fc3Col),
		fc3CA = table.clone(copyFrom.fc3CA),
	}
end
return {
	loadFromMesh = loadFromMesh,
}
