import { ImageAsset } from "../ImageAsset";
export type MaterialData = [
    name: string,
    hasImage: boolean,
    useImageTransparency: boolean,
    imageHash: string,
    alpha: number
];
export interface Material {
    name: string;
    useImageTransparency: boolean;
    image?: ImageAsset;
    transparency: number;
}
export declare namespace Material {
    function create(materialData: MaterialData): void;
}
export default Material;
