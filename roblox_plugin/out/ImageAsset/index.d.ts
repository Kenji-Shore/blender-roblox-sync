export interface ImageAsset {
    name: string;
    content: Content;
}
export declare namespace ImageAsset {
    function update(imageHash: string, imageBuffer: buffer): void;
    function create(imageBuffer: buffer): ImageAsset;
}
export default ImageAsset;
