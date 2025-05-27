export interface Consumer {
    instance?: Model | MeshPart;
    meshParts: MeshPart[];
    size: Vector3;
    useImageTransparency: boolean;
}
type MeshImageData = [
    hasImage: boolean,
    useImageTransparency: boolean,
    meshHash: string,
    alpha: number,
    imageHash?: string
];
type ObjectData = [name: string, cframe: CFrame, size: Vector3, meshImages: MeshImageData[]];
export interface Object {
    name: string;
    instance: Model | MeshPart;
    consumers: Consumer[];
}
export declare namespace Object {
    function create(objectData: ObjectData): Object;
}
export default Object;
