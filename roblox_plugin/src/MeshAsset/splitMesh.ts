//!native
import { SplitMesh } from "./index";

export function splitMesh(mesh: SplitMesh, axis: "X" | "Y" | "Z", splitPos: number) {
	const vertices = mesh.vertices;
	const edgeStartVIs = mesh.edgeStartVIs;
	const edgeEndVIs = mesh.edgeEndVIs;
	const edgeInvVecs = mesh.edgeInvVecs;

	const edgeSplitEIs = mesh.edgeSplitEIs;
	const edgeSplitAlphas = mesh.edgeSplitAlphas;
	const edgeSplitVIs = mesh.edgeSplitVIs;
	table.clear(edgeSplitEIs);
	table.clear(edgeSplitAlphas);
	table.clear(edgeSplitVIs);

	for (const i of $range(0, mesh.edgesCount - 1)) {
		const endVI = edgeEndVIs[i];
		const startVertex = vertices[edgeStartVIs[i]];
		const endVertex = vertices[endVI];
		const alpha = (splitPos - endVertex[axis]) * edgeInvVecs[i][axis];
		if (alpha > 0 && alpha < 1) {
			const newVertex = startVertex.sub(endVertex).mul(alpha).add(endVertex);
			vertices.push(newVertex);
			const vi = mesh.vertsCount;
			mesh.vertsCount += 1;

			edgeEndVIs[i] = vi;
			edgeInvVecs[i] = Vector3.one.div(startVertex.sub(newVertex));
			edgeStartVIs.push(endVI);
			edgeEndVIs.push(vi);
			edgeInvVecs.push(Vector3.one.div(endVertex.sub(newVertex)));
			const ei = mesh.edgesCount;
			mesh.edgesCount += 1;

			edgeSplitAlphas.set(i, alpha);
			edgeSplitVIs.set(i, vi);
			edgeSplitEIs.set(i, ei);
		}
	}

	const hasUVs = mesh.hasUVs;
	const hasColors = mesh.hasColors;

	const fc1VI = mesh.fc1VI;
	const fc2VI = mesh.fc2VI;
	const fc3VI = mesh.fc3VI;

	const fEI1 = mesh.fEI1;
	const fEI2 = mesh.fEI2;
	const fEI3 = mesh.fEI3;

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
	for (const ti0 of $range(0, mesh.trisCount - 1)) {
		const vi1 = fc1VI[ti0];
		const vi2 = fc2VI[ti0];
		const vi3 = fc3VI[ti0];

		let ei1 = fEI1[ti0];
		let ei2 = fEI2[ti0];
		let ei3 = fEI3[ti0];

		const n1 = fc1N[ti0];
		const n2 = fc2N[ti0];
		const n3 = fc3N[ti0];

		const uv1 = fc1UV[ti0];
		const uv2 = fc2UV[ti0];
		const uv3 = fc3UV[ti0];

		const col1 = fc1Col[ti0];
		const ca1 = fc1CA[ti0];
		const col2 = fc2Col[ti0];
		const ca2 = fc2CA[ti0];
		const col3 = fc3Col[ti0];
		const ca3 = fc3CA[ti0];

		let a1 = edgeSplitAlphas.get(ei1);
		let a2 = edgeSplitAlphas.get(ei2);
		let a3 = edgeSplitAlphas.get(ei3);
		if (a1) {
			const vi4 = edgeSplitVIs.get(ei1)!;
			let ei4 = edgeSplitEIs.get(ei1)!;
			if (edgeStartVIs[ei1] !== vi1) {
				a1 = 1 - a1;
				const swap = ei4;
				ei4 = ei1;
				ei1 = swap;
			}
			if (a2) {
				const vi5 = edgeSplitVIs.get(ei2)!;
				let ei5 = edgeSplitEIs.get(ei2)!;
				if (edgeStartVIs[ei2] !== vi1) {
					a2 = 1 - a2;
					const swap = ei5;
					ei5 = ei2;
					ei2 = swap;
				}
				//a1 and a2, shared v1
				//ei1: vi1 to vi4
				//ei4: vi2 to vi4
				//ei2: vi1 to vi5
				//ei5: vi3 to vi5
				//ei6: vi4 to vi5
				//ei7: vi5 to vi2
				//ei3: vi2 to vi3
				//t0: e1, e2, e6 aka 1=fc1, 2=fc4, 3=fc5
				//t1: e4, e6, e7 aka 1=fc4, 2=fc2, 3=fc5
				//t2: e3, e7, e5 aka 1=fc2, 2=fc3, 3=fc5
				const ti1 = mesh.trisCount;
				const ti2 = ti1 + 1;
				mesh.trisCount += 2;

				edgeStartVIs.push(vi4); //ei6
				edgeEndVIs.push(vi5);
				edgeInvVecs.push(Vector3.one.div(vertices[vi4].sub(vertices[vi5])));
				edgeStartVIs.push(vi2); //ei7
				edgeEndVIs.push(vi5);
				edgeInvVecs.push(Vector3.one.div(vertices[vi2].sub(vertices[vi5])));
				const ei6 = mesh.edgesCount;
				const ei7 = ei6 + 1;
				mesh.edgesCount += 2;

				const n4 = n1.sub(n2).mul(a1).add(n2);
				const n5 = n1.sub(n3).mul(a2).add(n3);
				fc2VI[ti0] = vi4;
				fc3VI[ti0] = vi5;
				fEI1[ti0] = ei1;
				fEI2[ti0] = ei2;
				fEI3[ti0] = ei6;
				fc2N[ti0] = n4;
				fc3N[ti0] = n5;

				fc1VI[ti1] = vi4;
				fc2VI[ti1] = vi2;
				fc3VI[ti1] = vi5;
				fEI1[ti1] = ei4;
				fEI2[ti1] = ei6;
				fEI3[ti1] = ei7;
				fc1N[ti1] = n4;
				fc2N[ti1] = n2;
				fc3N[ti1] = n5;

				fc1VI[ti2] = vi2;
				fc2VI[ti2] = vi3;
				fc3VI[ti2] = vi5;
				fEI1[ti2] = ei3;
				fEI2[ti2] = ei7;
				fEI3[ti2] = ei5;
				fc1N[ti2] = n2;
				fc2N[ti2] = n3;
				fc3N[ti2] = n5;

				if (hasUVs) {
					const uv4 = uv1.sub(uv2).mul(a1).add(uv2);
					const uv5 = uv1.sub(uv3).mul(a2).add(uv3);
					fc2UV[ti0] = uv4;
					fc3UV[ti0] = uv5;

					fc1UV[ti1] = uv4;
					fc2UV[ti1] = uv2;
					fc3UV[ti1] = uv5;

					fc1UV[ti2] = uv2;
					fc2UV[ti2] = uv3;
					fc3UV[ti2] = uv5;
				}
				if (hasColors) {
					const col4 = col2.Lerp(col1, a1);
					const ca4 = (ca1 - ca2) * a1 + ca2;
					const col5 = col3.Lerp(col1, a2);
					const ca5 = (ca1 - ca3) * a2 + ca3;
					fc2Col[ti0] = col4;
					fc2CA[ti0] = ca4;
					fc3Col[ti0] = col5;
					fc3CA[ti0] = ca5;

					fc1Col[ti1] = col4;
					fc1CA[ti1] = ca4;
					fc2Col[ti1] = col2;
					fc2CA[ti1] = ca2;
					fc3Col[ti1] = col5;
					fc3CA[ti1] = ca5;

					fc1Col[ti2] = col2;
					fc1CA[ti2] = ca2;
					fc2Col[ti2] = col3;
					fc2CA[ti2] = ca3;
					fc3Col[ti2] = col5;
					fc3CA[ti2] = ca5;
				}
			} else if (a3) {
				const vi5 = edgeSplitVIs.get(ei3)!;
				let ei5 = edgeSplitEIs.get(ei3)!;
				if (edgeStartVIs[ei3] !== vi2) {
					a3 = 1 - a3;
					const swap = ei5;
					ei5 = ei3;
					ei3 = swap;
				}
				//a1 and a3, shared v2
				//ei1: vi1 to vi4
				//ei4: vi2 to vi4
				//ei3: vi2 to vi5
				//ei5: vi3 to vi5
				//ei6: vi4 to vi5
				//ei7: vi4 to vi3
				//ei2: vi1 to vi3
				//t0: e4, e6, e3 aka 1=fc4, 2=fc2, 3=fc5
				//t1: e6, e7, e5 aka 1=fc4, 2=fc5, 3=fc3
				//t2: e7, e1, e2 aka 1=fc4, 2=fc3, 3=fc1
				const ti1 = mesh.trisCount;
				const ti2 = ti1 + 1;
				mesh.trisCount += 2;

				edgeStartVIs.push(vi4); //ei6
				edgeEndVIs.push(vi5);
				edgeInvVecs.push(Vector3.one.div(vertices[vi4].sub(vertices[vi5])));
				edgeStartVIs.push(vi4); //ei7
				edgeEndVIs.push(vi3);
				edgeInvVecs.push(Vector3.one.div(vertices[vi4].sub(vertices[vi3])));
				const ei6 = mesh.edgesCount;
				const ei7 = ei6 + 1;
				mesh.edgesCount += 2;

				const n4 = n1.sub(n2).mul(a1).add(n2);
				const n5 = n2.sub(n3).mul(a3).add(n3);
				fc1VI[ti0] = vi4;
				fc3VI[ti0] = vi5;
				fEI1[ti0] = ei4;
				fEI2[ti0] = ei6;
				fEI3[ti0] = ei3;
				fc1N[ti0] = n4;
				fc3N[ti0] = n5;

				fc1VI[ti1] = vi4;
				fc2VI[ti1] = vi5;
				fc3VI[ti1] = vi3;
				fEI1[ti1] = ei6;
				fEI2[ti1] = ei7;
				fEI3[ti1] = ei5;
				fc1N[ti1] = n4;
				fc2N[ti1] = n5;
				fc3N[ti1] = n3;

				fc1VI[ti2] = vi4;
				fc2VI[ti2] = vi3;
				fc3VI[ti2] = vi1;
				fEI1[ti2] = ei7;
				fEI2[ti2] = ei1;
				fEI3[ti2] = ei2;
				fc1N[ti2] = n4;
				fc2N[ti2] = n3;
				fc3N[ti2] = n1;

				if (hasUVs) {
					const uv4 = uv1.sub(uv2).mul(a1).add(uv2);
					const uv5 = uv2.sub(uv3).mul(a3).add(uv3);
					fc1UV[ti0] = uv4;
					fc3UV[ti0] = uv5;

					fc1UV[ti1] = uv4;
					fc2UV[ti1] = uv5;
					fc3UV[ti1] = uv3;

					fc1UV[ti2] = uv4;
					fc2UV[ti2] = uv3;
					fc3UV[ti2] = uv1;
				}
				if (hasColors) {
					const col4 = col2.Lerp(col1, a1);
					const ca4 = (ca1 - ca2) * a1 + ca2;
					const col5 = col3.Lerp(col2, a3);
					const ca5 = (ca2 - ca3) * a3 + ca3;
					fc1Col[ti0] = col4;
					fc1CA[ti0] = ca4;
					fc3Col[ti0] = col5;
					fc3CA[ti0] = ca5;

					fc1Col[ti1] = col4;
					fc1CA[ti1] = ca4;
					fc2Col[ti1] = col5;
					fc2CA[ti1] = ca5;
					fc3Col[ti1] = col3;
					fc3CA[ti1] = ca3;

					fc1Col[ti2] = col4;
					fc1CA[ti2] = ca4;
					fc2Col[ti2] = col3;
					fc2CA[ti2] = ca3;
					fc3Col[ti2] = col1;
					fc3CA[ti2] = ca1;
				}
			} else {
				//a1 only, opposing v3
				//ei1: vi1 to vi4
				//ei4: vi2 to vi4
				//ei5: vi4 to vi3
				//t0: e1, e2, e5 aka 1=fc1, 2=fc4, 3=fc3
				//t1: e4, e5, e3 aka 1=fc4, 2=fc2, 3=fc3
				const ti1 = mesh.trisCount;
				mesh.trisCount += 1;

				edgeStartVIs.push(vi4); //ei5
				edgeEndVIs.push(vi3);
				edgeInvVecs.push(Vector3.one.div(vertices[vi4].sub(vertices[vi3])));
				const ei5 = mesh.edgesCount;
				mesh.edgesCount += 1;

				const n4 = n1.sub(n2).mul(a1).add(n2);
				fc2VI[ti0] = vi4;
				fEI3[ti0] = ei5;
				fc2N[ti0] = n4;

				fc1VI[ti1] = vi4;
				fc2VI[ti1] = vi2;
				fc3VI[ti1] = vi3;
				fEI1[ti1] = ei4;
				fEI2[ti1] = ei5;
				fEI3[ti1] = ei3;
				fc1N[ti1] = n4;
				fc2N[ti1] = n2;
				fc3N[ti1] = n3;

				if (hasUVs) {
					const uv4 = uv1.sub(uv2).mul(a1).add(uv2);
					fc2UV[ti0] = uv4;

					fc1UV[ti1] = uv4;
					fc2UV[ti1] = uv2;
					fc3UV[ti1] = uv3;
				}
				if (hasColors) {
					const col4 = col2.Lerp(col1, a1);
					const ca4 = (ca1 - ca2) * a1 + ca2;
					fc2Col[ti0] = col4;
					fc2CA[ti0] = ca4;

					fc1Col[ti1] = col4;
					fc1CA[ti1] = ca4;
					fc2Col[ti1] = col2;
					fc2CA[ti1] = ca2;
					fc3Col[ti1] = col3;
					fc3CA[ti1] = ca3;
				}
			}
		} else if (a2) {
			const vi4 = edgeSplitVIs.get(ei2)!;
			let ei4 = edgeSplitEIs.get(ei2)!;
			if (edgeStartVIs[ei2] !== vi1) {
				a2 = 1 - a2;
				const swap = ei4;
				ei4 = ei2;
				ei2 = swap;
			}
			if (a3) {
				const vi5 = edgeSplitVIs.get(ei3)!;
				let ei5 = edgeSplitEIs.get(ei3)!;
				if (edgeStartVIs[ei3] !== vi2) {
					a3 = 1 - a3;
					const swap = ei5;
					ei5 = ei3;
					ei3 = swap;
				}
				//a2 and a3, shared v3
				//ei2: vi1 to vi4
				//ei4: vi3 to vi4
				//ei3: vi2 to vi5
				//ei5: vi3 to vi5
				//ei6: vi4 to vi5
				//ei7: vi5 to vi1
				//ei1: vi1 to vi2
				//t0: e6, e4, e5 aka 1=fc4, 2=fc5, 3=fc3
				//t1: e2, e6, e7 aka 1=fc4, 2=fc1, 3=fc5
				//t2: e1, e7, e3 aka 1=fc1, 2=fc2, 3=fc5
				const ti1 = mesh.trisCount;
				const ti2 = ti1 + 1;
				mesh.trisCount += 2;

				edgeStartVIs.push(vi4); //ei6
				edgeEndVIs.push(vi5);
				edgeInvVecs.push(Vector3.one.div(vertices[vi4].sub(vertices[vi5])));
				edgeStartVIs.push(vi5); //ei7
				edgeEndVIs.push(vi1);
				edgeInvVecs.push(Vector3.one.div(vertices[vi5].sub(vertices[vi1])));
				const ei6 = mesh.edgesCount;
				const ei7 = ei6 + 1;
				mesh.edgesCount += 2;

				const n4 = n1.sub(n3).mul(a2).add(n3);
				const n5 = n2.sub(n3).mul(a3).add(n3);
				fc1VI[ti0] = vi4;
				fc2VI[ti0] = vi5;
				fEI1[ti0] = ei6;
				fEI2[ti0] = ei4;
				fEI3[ti0] = ei5;
				fc1N[ti0] = n4;
				fc2N[ti0] = n5;

				fc1VI[ti1] = vi4;
				fc2VI[ti1] = vi1;
				fc3VI[ti1] = vi5;
				fEI1[ti1] = ei2;
				fEI2[ti1] = ei6;
				fEI3[ti1] = ei7;
				fc1N[ti1] = n4;
				fc2N[ti1] = n1;
				fc3N[ti1] = n5;

				fc1VI[ti2] = vi1;
				fc2VI[ti2] = vi2;
				fc3VI[ti2] = vi5;
				fEI1[ti2] = ei1;
				fEI2[ti2] = ei7;
				fEI3[ti2] = ei3;
				fc1N[ti2] = n1;
				fc2N[ti2] = n2;
				fc3N[ti2] = n5;

				if (hasUVs) {
					const uv4 = uv1.sub(uv3).mul(a2).add(uv3);
					const uv5 = uv2.sub(uv3).mul(a3).add(uv3);
					fc1UV[ti0] = uv4;
					fc2UV[ti0] = uv5;

					fc1UV[ti1] = uv4;
					fc2UV[ti1] = uv1;
					fc3UV[ti1] = uv5;

					fc1UV[ti2] = uv1;
					fc2UV[ti2] = uv2;
					fc3UV[ti2] = uv5;
				}
				if (hasColors) {
					const col4 = col3.Lerp(col1, a2);
					const ca4 = (ca1 - ca3) * a2 + ca3;
					const col5 = col3.Lerp(col2, a3);
					const ca5 = (ca2 - ca3) * a3 + ca3;
					fc1Col[ti0] = col4;
					fc1CA[ti0] = ca4;
					fc2Col[ti0] = col5;
					fc2CA[ti0] = ca5;

					fc1Col[ti1] = col4;
					fc1CA[ti1] = ca4;
					fc2Col[ti1] = col1;
					fc2CA[ti1] = ca1;
					fc3Col[ti1] = col5;
					fc3CA[ti1] = ca5;

					fc1Col[ti2] = col1;
					fc1CA[ti2] = ca1;
					fc2Col[ti2] = col2;
					fc2CA[ti2] = ca2;
					fc3Col[ti2] = col5;
					fc3CA[ti2] = ca5;
				}
			} else {
				//a2 only, opposing v2
				//ei2: vi1 to vi4
				//ei4: vi3 to vi4
				//ei5: vi4 to vi2
				//t0: e1, e2, e5 aka 1=fc1, 2=fc2, 3=fc4
				//t1: e5, e4, e3 aka 1=fc4, 2=fc2, 3=fc3
				const ti1 = mesh.trisCount;
				mesh.trisCount += 1;

				edgeStartVIs.push(vi4); //ei5
				edgeEndVIs.push(vi2);
				edgeInvVecs.push(Vector3.one.div(vertices[vi4].sub(vertices[vi2])));
				const ei5 = mesh.edgesCount;
				mesh.edgesCount += 1;

				const n4 = n1.sub(n3).mul(a2).add(n3);
				fc3VI[ti0] = vi4;
				fEI3[ti0] = ei5;
				fc3N[ti0] = n4;

				fc1VI[ti1] = vi4;
				fc2VI[ti1] = vi2;
				fc3VI[ti1] = vi3;
				fEI1[ti1] = ei5;
				fEI2[ti1] = ei4;
				fEI3[ti1] = ei3;
				fc1N[ti1] = n4;
				fc2N[ti1] = n2;
				fc3N[ti1] = n3;

				if (hasUVs) {
					const uv4 = uv1.sub(uv3).mul(a2).add(uv3);
					fc3UV[ti0] = uv4;

					fc1UV[ti1] = uv4;
					fc2UV[ti1] = uv2;
					fc3UV[ti1] = uv3;
				}
				if (hasColors) {
					const col4 = col3.Lerp(col1, a2);
					const ca4 = (ca1 - ca3) * a2 + ca3;
					fc3Col[ti0] = col4;
					fc3CA[ti0] = ca4;

					fc1Col[ti1] = col4;
					fc1CA[ti1] = ca4;
					fc2Col[ti1] = col2;
					fc2CA[ti1] = ca2;
					fc3Col[ti1] = col3;
					fc3CA[ti1] = ca3;
				}
			}
		} else if (a3) {
			const vi4 = edgeSplitVIs.get(ei3)!;
			let ei4 = edgeSplitEIs.get(ei3)!;
			if (edgeStartVIs[ei3] !== vi2) {
				a3 = 1 - a3;
				const swap = ei4;
				ei4 = ei3;
				ei3 = swap;
			}
			//a3 only, opposing v1
			//ei3: vi2 to vi4
			//ei4: vi3 to vi4
			//ei5: vi4 to vi1
			//t0: e1, e5, e3 aka 1=fc1, 2=fc2, 3=fc4
			//t1: e5, e2, e4 aka 1=fc1, 2=fc4, 3=fc3
			const ti1 = mesh.trisCount;
			mesh.trisCount += 1;

			edgeStartVIs.push(vi4); //ei5
			edgeEndVIs.push(vi1);
			edgeInvVecs.push(Vector3.one.div(vertices[vi4].sub(vertices[vi1])));
			const ei5 = mesh.edgesCount;
			mesh.edgesCount += 1;

			const n4 = n2.sub(n3).mul(a3).add(n3);
			fc3VI[ti0] = vi4;
			fEI2[ti0] = ei5;
			fc3N[ti0] = n4;

			fc1VI[ti1] = vi1;
			fc2VI[ti1] = vi4;
			fc3VI[ti1] = vi3;
			fEI1[ti1] = ei5;
			fEI2[ti1] = ei2;
			fEI3[ti1] = ei4;
			fc1N[ti1] = n1;
			fc2N[ti1] = n4;
			fc3N[ti1] = n3;

			if (hasUVs) {
				const uv4 = uv2.sub(uv3).mul(a3).add(uv3);
				fc3UV[ti0] = uv4;

				fc1UV[ti1] = uv1;
				fc2UV[ti1] = uv4;
				fc3UV[ti1] = uv3;
			}
			if (hasColors) {
				const col4 = col3.Lerp(col2, a3);
				const ca4 = (ca2 - ca3) * a3 + ca3;
				fc3Col[ti0] = col4;
				fc3CA[ti0] = ca4;

				fc1Col[ti1] = col1;
				fc1CA[ti1] = ca1;
				fc2Col[ti1] = col4;
				fc2CA[ti1] = ca4;
				fc3Col[ti1] = col3;
				fc3CA[ti1] = ca3;
			}
		}
	}
}
