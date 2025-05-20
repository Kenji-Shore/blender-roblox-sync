export interface Consumer {
    instance?: Model | MeshPart;
    meshParts: MeshPart[];
    size: Vector3;
    useImageTransparency: boolean;
}
