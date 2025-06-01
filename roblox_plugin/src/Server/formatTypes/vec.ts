// //!native

// const YAW = 32767 / math.pi;
// const INV_YAW = 1 / YAW;
// const PITCH = 32767 / (0.5 * math.pi);
// const INV_PITCH = 1 / PITCH;

// export function read(b: Buffer): Vector3 {
// 	const normalYaw = b.read(buffer.readi16, 2) * INV_YAW;
// 	const normalPitch = b.read(buffer.readi16, 2) * INV_PITCH;
// 	const velMag = b.read(buffer.readf32, 4);
// 	const horizontal = math.cos(normalPitch);
// 	return new Vector3(math.cos(normalYaw) * horizontal, math.sin(normalPitch), math.sin(normalYaw) * horizontal).mul(
// 		velMag,
// 	);
// }
// export function write(b: Buffer, value: Vector3) {
// 	const velMag = value.Magnitude;
// 	const unitVel = velMag !== 0 ? value.div(velMag) : Vector3.xAxis;
// 	const normalYaw = math.atan2(unitVel.Z, unitVel.X);
// 	const normalPitch = math.asin(unitVel.Y);
// 	b.write(buffer.writei16, 2, math.round(normalYaw * YAW));
// 	b.write(buffer.writei16, 2, math.round(normalPitch * PITCH));
// 	b.write(buffer.writef32, 4, velMag);
// }
