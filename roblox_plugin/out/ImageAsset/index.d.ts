import { Consumer } from "../index.server";
interface ImageConsumer {
    consumer: Consumer;
}
export interface ImageAsset {
    content: Content;
    consumers: ImageConsumer[];
}
export declare namespace ImageAsset {
    function update(imageHash: string, imageBuffer: buffer): void;
    function create(imageBuffer: buffer): ImageAsset;
    function addConsumer(imageAsset: ImageAsset, consumer: Consumer): void;
}
export default ImageAsset;
