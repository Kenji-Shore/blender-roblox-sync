import { Consumer } from "../index.server";
export interface SourceMesh {
    hasUVs: boolean;
    hasColors: boolean;
    vertices: Vector3[];
    vertsCount: number;
    edgesCount: number;
    trisCount: number;
    edgeStartVIs: number[];
    edgeEndVIs: number[];
    edgeInvVecs: Vector3[];
    fc1VI: number[];
    fc2VI: number[];
    fc3VI: number[];
    fEI1: number[];
    fEI2: number[];
    fEI3: number[];
    fc1N: Vector3[];
    fc2N: Vector3[];
    fc3N: Vector3[];
    fc1UV: Vector2[];
    fc2UV: Vector2[];
    fc3UV: Vector2[];
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
    minBounds: Vector3;
    maxBounds: Vector3;
    meshSize: Vector3;
    sourceSplit: Split;
    splits: Split[];
}
export declare namespace MeshAsset {
    function create(meshBuffer: buffer): MeshAsset;
    function addConsumer(meshAsset: MeshAsset, consumer: Consumer): void;
}
export default MeshAsset;
