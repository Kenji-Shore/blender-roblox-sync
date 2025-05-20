--!native
-- Compiled with roblox-ts v3.0.0
local function splitMesh(mesh, axis, splitPos)
	local vertices = mesh.vertices
	local edgeStartVIs = mesh.edgeStartVIs
	local edgeEndVIs = mesh.edgeEndVIs
	local edgeInvVecs = mesh.edgeInvVecs
	local edgeSplitEIs = mesh.edgeSplitEIs
	local edgeSplitAlphas = mesh.edgeSplitAlphas
	local edgeSplitVIs = mesh.edgeSplitVIs
	table.clear(edgeSplitEIs)
	table.clear(edgeSplitAlphas)
	table.clear(edgeSplitVIs)
	for i = 0, mesh.edgesCount - 1 do
		local endVI = edgeEndVIs[i + 1]
		local startVertex = vertices[edgeStartVIs[i + 1] + 1]
		local endVertex = vertices[endVI + 1]
		local alpha = (splitPos - endVertex[axis]) * edgeInvVecs[i + 1][axis]
		if alpha > 0 and alpha < 1 then
			local newVertex = (startVertex - endVertex) * alpha + endVertex
			table.insert(vertices, newVertex)
			local vi = mesh.vertsCount
			mesh.vertsCount += 1
			edgeEndVIs[i + 1] = vi
			local _one = Vector3.one
			local _arg0 = startVertex - newVertex
			edgeInvVecs[i + 1] = _one / _arg0
			table.insert(edgeStartVIs, endVI)
			table.insert(edgeEndVIs, vi)
			local _one_1 = Vector3.one
			local _arg0_1 = endVertex - newVertex
			table.insert(edgeInvVecs, _one_1 / _arg0_1)
			local ei = mesh.edgesCount
			mesh.edgesCount += 1
			edgeSplitAlphas[i] = alpha
			edgeSplitVIs[i] = vi
			edgeSplitEIs[i] = ei
		end
	end
	local hasUVs = mesh.hasUVs
	local hasColors = mesh.hasColors
	local fc1VI = mesh.fc1VI
	local fc2VI = mesh.fc2VI
	local fc3VI = mesh.fc3VI
	local fEI1 = mesh.fEI1
	local fEI2 = mesh.fEI2
	local fEI3 = mesh.fEI3
	local fc1N = mesh.fc1N
	local fc2N = mesh.fc2N
	local fc3N = mesh.fc3N
	local fc1UV = mesh.fc1UV
	local fc2UV = mesh.fc2UV
	local fc3UV = mesh.fc3UV
	local fc1Col = mesh.fc1Col
	local fc1CA = mesh.fc1CA
	local fc2Col = mesh.fc2Col
	local fc2CA = mesh.fc2CA
	local fc3Col = mesh.fc3Col
	local fc3CA = mesh.fc3CA
	for ti0 = 0, mesh.trisCount - 1 do
		local vi1 = fc1VI[ti0 + 1]
		local vi2 = fc2VI[ti0 + 1]
		local vi3 = fc3VI[ti0 + 1]
		local ei1 = fEI1[ti0 + 1]
		local ei2 = fEI2[ti0 + 1]
		local ei3 = fEI3[ti0 + 1]
		local n1 = fc1N[ti0 + 1]
		local n2 = fc2N[ti0 + 1]
		local n3 = fc3N[ti0 + 1]
		local uv1 = fc1UV[ti0 + 1]
		local uv2 = fc2UV[ti0 + 1]
		local uv3 = fc3UV[ti0 + 1]
		local col1 = fc1Col[ti0 + 1]
		local ca1 = fc1CA[ti0 + 1]
		local col2 = fc2Col[ti0 + 1]
		local ca2 = fc2CA[ti0 + 1]
		local col3 = fc3Col[ti0 + 1]
		local ca3 = fc3CA[ti0 + 1]
		local _ei1 = ei1
		local a1 = edgeSplitAlphas[_ei1]
		local _ei2 = ei2
		local a2 = edgeSplitAlphas[_ei2]
		local _ei3 = ei3
		local a3 = edgeSplitAlphas[_ei3]
		if a1 ~= 0 and a1 == a1 and a1 then
			local _ei1_1 = ei1
			local vi4 = edgeSplitVIs[_ei1_1]
			local _ei1_2 = ei1
			local ei4 = edgeSplitEIs[_ei1_2]
			if edgeStartVIs[ei1 + 1] ~= vi1 then
				a1 = 1 - a1
				local swap = ei4
				ei4 = ei1
				ei1 = swap
			end
			if a2 ~= 0 and a2 == a2 and a2 then
				local _ei2_1 = ei2
				local vi5 = edgeSplitVIs[_ei2_1]
				local _ei2_2 = ei2
				local ei5 = edgeSplitEIs[_ei2_2]
				if edgeStartVIs[ei2 + 1] ~= vi1 then
					a2 = 1 - a2
					local swap = ei5
					ei5 = ei2
					ei2 = swap
				end
				--a1 and a2, shared v1
				--ei1: vi1 to vi4
				--ei4: vi2 to vi4
				--ei2: vi1 to vi5
				--ei5: vi3 to vi5
				--ei6: vi4 to vi5
				--ei7: vi5 to vi2
				--ei3: vi2 to vi3
				--t0: e1, e2, e6 aka 1=fc1, 2=fc4, 3=fc5
				--t1: e4, e6, e7 aka 1=fc4, 2=fc2, 3=fc5
				--t2: e3, e7, e5 aka 1=fc2, 2=fc3, 3=fc5
				local ti1 = mesh.trisCount
				local ti2 = ti1 + 1
				mesh.trisCount += 2
				table.insert(edgeStartVIs, vi4)
				table.insert(edgeEndVIs, vi5)
				local _one = Vector3.one
				local _exp = vertices[vi4 + 1]
				local _arg0 = vertices[vi5 + 1]
				table.insert(edgeInvVecs, _one / (_exp - _arg0))
				table.insert(edgeStartVIs, vi2)
				table.insert(edgeEndVIs, vi5)
				local _one_1 = Vector3.one
				local _exp_1 = vertices[vi2 + 1]
				local _arg0_1 = vertices[vi5 + 1]
				table.insert(edgeInvVecs, _one_1 / (_exp_1 - _arg0_1))
				local ei6 = mesh.edgesCount
				local ei7 = ei6 + 1
				mesh.edgesCount += 2
				local _exp_2 = n1 - n2
				local _a1 = a1
				local n4 = _exp_2 * _a1 + n2
				local _exp_3 = n1 - n3
				local _a2 = a2
				local n5 = _exp_3 * _a2 + n3
				fc2VI[ti0 + 1] = vi4
				fc3VI[ti0 + 1] = vi5
				fEI1[ti0 + 1] = ei1
				fEI2[ti0 + 1] = ei2
				fEI3[ti0 + 1] = ei6
				fc2N[ti0 + 1] = n4
				fc3N[ti0 + 1] = n5
				fc1VI[ti1 + 1] = vi4
				fc2VI[ti1 + 1] = vi2
				fc3VI[ti1 + 1] = vi5
				fEI1[ti1 + 1] = ei4
				fEI2[ti1 + 1] = ei6
				fEI3[ti1 + 1] = ei7
				fc1N[ti1 + 1] = n4
				fc2N[ti1 + 1] = n2
				fc3N[ti1 + 1] = n5
				fc1VI[ti2 + 1] = vi2
				fc2VI[ti2 + 1] = vi3
				fc3VI[ti2 + 1] = vi5
				fEI1[ti2 + 1] = ei3
				fEI2[ti2 + 1] = ei7
				fEI3[ti2 + 1] = ei5
				fc1N[ti2 + 1] = n2
				fc2N[ti2 + 1] = n3
				fc3N[ti2 + 1] = n5
				if hasUVs then
					local _exp_4 = uv1 - uv2
					local _a1_1 = a1
					local uv4 = _exp_4 * _a1_1 + uv2
					local _exp_5 = uv1 - uv3
					local _a2_1 = a2
					local uv5 = _exp_5 * _a2_1 + uv3
					fc2UV[ti0 + 1] = uv4
					fc3UV[ti0 + 1] = uv5
					fc1UV[ti1 + 1] = uv4
					fc2UV[ti1 + 1] = uv2
					fc3UV[ti1 + 1] = uv5
					fc1UV[ti2 + 1] = uv2
					fc2UV[ti2 + 1] = uv3
					fc3UV[ti2 + 1] = uv5
				end
				if hasColors then
					local col4 = col2:Lerp(col1, a1)
					local ca4 = (ca1 - ca2) * a1 + ca2
					local col5 = col3:Lerp(col1, a2)
					local ca5 = (ca1 - ca3) * a2 + ca3
					fc2Col[ti0 + 1] = col4
					fc2CA[ti0 + 1] = ca4
					fc3Col[ti0 + 1] = col5
					fc3CA[ti0 + 1] = ca5
					fc1Col[ti1 + 1] = col4
					fc1CA[ti1 + 1] = ca4
					fc2Col[ti1 + 1] = col2
					fc2CA[ti1 + 1] = ca2
					fc3Col[ti1 + 1] = col5
					fc3CA[ti1 + 1] = ca5
					fc1Col[ti2 + 1] = col2
					fc1CA[ti2 + 1] = ca2
					fc2Col[ti2 + 1] = col3
					fc2CA[ti2 + 1] = ca3
					fc3Col[ti2 + 1] = col5
					fc3CA[ti2 + 1] = ca5
				end
			elseif a3 ~= 0 and a3 == a3 and a3 then
				local _ei3_1 = ei3
				local vi5 = edgeSplitVIs[_ei3_1]
				local _ei3_2 = ei3
				local ei5 = edgeSplitEIs[_ei3_2]
				if edgeStartVIs[ei3 + 1] ~= vi2 then
					a3 = 1 - a3
					local swap = ei5
					ei5 = ei3
					ei3 = swap
				end
				--a1 and a3, shared v2
				--ei1: vi1 to vi4
				--ei4: vi2 to vi4
				--ei3: vi2 to vi5
				--ei5: vi3 to vi5
				--ei6: vi4 to vi5
				--ei7: vi4 to vi3
				--ei2: vi1 to vi3
				--t0: e4, e6, e3 aka 1=fc4, 2=fc2, 3=fc5
				--t1: e6, e7, e5 aka 1=fc4, 2=fc5, 3=fc3
				--t2: e7, e1, e2 aka 1=fc4, 2=fc3, 3=fc1
				local ti1 = mesh.trisCount
				local ti2 = ti1 + 1
				mesh.trisCount += 2
				table.insert(edgeStartVIs, vi4)
				table.insert(edgeEndVIs, vi5)
				local _one = Vector3.one
				local _exp = vertices[vi4 + 1]
				local _arg0 = vertices[vi5 + 1]
				table.insert(edgeInvVecs, _one / (_exp - _arg0))
				table.insert(edgeStartVIs, vi4)
				table.insert(edgeEndVIs, vi3)
				local _one_1 = Vector3.one
				local _exp_1 = vertices[vi4 + 1]
				local _arg0_1 = vertices[vi3 + 1]
				table.insert(edgeInvVecs, _one_1 / (_exp_1 - _arg0_1))
				local ei6 = mesh.edgesCount
				local ei7 = ei6 + 1
				mesh.edgesCount += 2
				local _exp_2 = n1 - n2
				local _a1 = a1
				local n4 = _exp_2 * _a1 + n2
				local _exp_3 = n2 - n3
				local _a3 = a3
				local n5 = _exp_3 * _a3 + n3
				fc1VI[ti0 + 1] = vi4
				fc3VI[ti0 + 1] = vi5
				fEI1[ti0 + 1] = ei4
				fEI2[ti0 + 1] = ei6
				fEI3[ti0 + 1] = ei3
				fc1N[ti0 + 1] = n4
				fc3N[ti0 + 1] = n5
				fc1VI[ti1 + 1] = vi4
				fc2VI[ti1 + 1] = vi5
				fc3VI[ti1 + 1] = vi3
				fEI1[ti1 + 1] = ei6
				fEI2[ti1 + 1] = ei7
				fEI3[ti1 + 1] = ei5
				fc1N[ti1 + 1] = n4
				fc2N[ti1 + 1] = n5
				fc3N[ti1 + 1] = n3
				fc1VI[ti2 + 1] = vi4
				fc2VI[ti2 + 1] = vi3
				fc3VI[ti2 + 1] = vi1
				fEI1[ti2 + 1] = ei7
				fEI2[ti2 + 1] = ei1
				fEI3[ti2 + 1] = ei2
				fc1N[ti2 + 1] = n4
				fc2N[ti2 + 1] = n3
				fc3N[ti2 + 1] = n1
				if hasUVs then
					local _exp_4 = uv1 - uv2
					local _a1_1 = a1
					local uv4 = _exp_4 * _a1_1 + uv2
					local _exp_5 = uv2 - uv3
					local _a3_1 = a3
					local uv5 = _exp_5 * _a3_1 + uv3
					fc1UV[ti0 + 1] = uv4
					fc3UV[ti0 + 1] = uv5
					fc1UV[ti1 + 1] = uv4
					fc2UV[ti1 + 1] = uv5
					fc3UV[ti1 + 1] = uv3
					fc1UV[ti2 + 1] = uv4
					fc2UV[ti2 + 1] = uv3
					fc3UV[ti2 + 1] = uv1
				end
				if hasColors then
					local col4 = col2:Lerp(col1, a1)
					local ca4 = (ca1 - ca2) * a1 + ca2
					local col5 = col3:Lerp(col2, a3)
					local ca5 = (ca2 - ca3) * a3 + ca3
					fc1Col[ti0 + 1] = col4
					fc1CA[ti0 + 1] = ca4
					fc3Col[ti0 + 1] = col5
					fc3CA[ti0 + 1] = ca5
					fc1Col[ti1 + 1] = col4
					fc1CA[ti1 + 1] = ca4
					fc2Col[ti1 + 1] = col5
					fc2CA[ti1 + 1] = ca5
					fc3Col[ti1 + 1] = col3
					fc3CA[ti1 + 1] = ca3
					fc1Col[ti2 + 1] = col4
					fc1CA[ti2 + 1] = ca4
					fc2Col[ti2 + 1] = col3
					fc2CA[ti2 + 1] = ca3
					fc3Col[ti2 + 1] = col1
					fc3CA[ti2 + 1] = ca1
				end
			else
				--a1 only, opposing v3
				--ei1: vi1 to vi4
				--ei4: vi2 to vi4
				--ei5: vi4 to vi3
				--t0: e1, e2, e5 aka 1=fc1, 2=fc4, 3=fc3
				--t1: e4, e5, e3 aka 1=fc4, 2=fc2, 3=fc3
				local ti1 = mesh.trisCount
				mesh.trisCount += 1
				table.insert(edgeStartVIs, vi4)
				table.insert(edgeEndVIs, vi3)
				local _one = Vector3.one
				local _exp = vertices[vi4 + 1]
				local _arg0 = vertices[vi3 + 1]
				table.insert(edgeInvVecs, _one / (_exp - _arg0))
				local ei5 = mesh.edgesCount
				mesh.edgesCount += 1
				local _exp_1 = n1 - n2
				local _a1 = a1
				local n4 = _exp_1 * _a1 + n2
				fc2VI[ti0 + 1] = vi4
				fEI3[ti0 + 1] = ei5
				fc2N[ti0 + 1] = n4
				fc1VI[ti1 + 1] = vi4
				fc2VI[ti1 + 1] = vi2
				fc3VI[ti1 + 1] = vi3
				fEI1[ti1 + 1] = ei4
				fEI2[ti1 + 1] = ei5
				fEI3[ti1 + 1] = ei3
				fc1N[ti1 + 1] = n4
				fc2N[ti1 + 1] = n2
				fc3N[ti1 + 1] = n3
				if hasUVs then
					local _exp_2 = uv1 - uv2
					local _a1_1 = a1
					local uv4 = _exp_2 * _a1_1 + uv2
					fc2UV[ti0 + 1] = uv4
					fc1UV[ti1 + 1] = uv4
					fc2UV[ti1 + 1] = uv2
					fc3UV[ti1 + 1] = uv3
				end
				if hasColors then
					local col4 = col2:Lerp(col1, a1)
					local ca4 = (ca1 - ca2) * a1 + ca2
					fc2Col[ti0 + 1] = col4
					fc2CA[ti0 + 1] = ca4
					fc1Col[ti1 + 1] = col4
					fc1CA[ti1 + 1] = ca4
					fc2Col[ti1 + 1] = col2
					fc2CA[ti1 + 1] = ca2
					fc3Col[ti1 + 1] = col3
					fc3CA[ti1 + 1] = ca3
				end
			end
		elseif a2 ~= 0 and a2 == a2 and a2 then
			local _ei2_1 = ei2
			local vi4 = edgeSplitVIs[_ei2_1]
			local _ei2_2 = ei2
			local ei4 = edgeSplitEIs[_ei2_2]
			if edgeStartVIs[ei2 + 1] ~= vi1 then
				a2 = 1 - a2
				local swap = ei4
				ei4 = ei2
				ei2 = swap
			end
			if a3 ~= 0 and a3 == a3 and a3 then
				local _ei3_1 = ei3
				local vi5 = edgeSplitVIs[_ei3_1]
				local _ei3_2 = ei3
				local ei5 = edgeSplitEIs[_ei3_2]
				if edgeStartVIs[ei3 + 1] ~= vi2 then
					a3 = 1 - a3
					local swap = ei5
					ei5 = ei3
					ei3 = swap
				end
				--a2 and a3, shared v3
				--ei2: vi1 to vi4
				--ei4: vi3 to vi4
				--ei3: vi2 to vi5
				--ei5: vi3 to vi5
				--ei6: vi4 to vi5
				--ei7: vi5 to vi1
				--ei1: vi1 to vi2
				--t0: e6, e4, e5 aka 1=fc4, 2=fc5, 3=fc3
				--t1: e2, e6, e7 aka 1=fc4, 2=fc1, 3=fc5
				--t2: e1, e7, e3 aka 1=fc1, 2=fc2, 3=fc5
				local ti1 = mesh.trisCount
				local ti2 = ti1 + 1
				mesh.trisCount += 2
				table.insert(edgeStartVIs, vi4)
				table.insert(edgeEndVIs, vi5)
				local _one = Vector3.one
				local _exp = vertices[vi4 + 1]
				local _arg0 = vertices[vi5 + 1]
				table.insert(edgeInvVecs, _one / (_exp - _arg0))
				table.insert(edgeStartVIs, vi5)
				table.insert(edgeEndVIs, vi1)
				local _one_1 = Vector3.one
				local _exp_1 = vertices[vi5 + 1]
				local _arg0_1 = vertices[vi1 + 1]
				table.insert(edgeInvVecs, _one_1 / (_exp_1 - _arg0_1))
				local ei6 = mesh.edgesCount
				local ei7 = ei6 + 1
				mesh.edgesCount += 2
				local _exp_2 = n1 - n3
				local _a2 = a2
				local n4 = _exp_2 * _a2 + n3
				local _exp_3 = n2 - n3
				local _a3 = a3
				local n5 = _exp_3 * _a3 + n3
				fc1VI[ti0 + 1] = vi4
				fc2VI[ti0 + 1] = vi5
				fEI1[ti0 + 1] = ei6
				fEI2[ti0 + 1] = ei4
				fEI3[ti0 + 1] = ei5
				fc1N[ti0 + 1] = n4
				fc2N[ti0 + 1] = n5
				fc1VI[ti1 + 1] = vi4
				fc2VI[ti1 + 1] = vi1
				fc3VI[ti1 + 1] = vi5
				fEI1[ti1 + 1] = ei2
				fEI2[ti1 + 1] = ei6
				fEI3[ti1 + 1] = ei7
				fc1N[ti1 + 1] = n4
				fc2N[ti1 + 1] = n1
				fc3N[ti1 + 1] = n5
				fc1VI[ti2 + 1] = vi1
				fc2VI[ti2 + 1] = vi2
				fc3VI[ti2 + 1] = vi5
				fEI1[ti2 + 1] = ei1
				fEI2[ti2 + 1] = ei7
				fEI3[ti2 + 1] = ei3
				fc1N[ti2 + 1] = n1
				fc2N[ti2 + 1] = n2
				fc3N[ti2 + 1] = n5
				if hasUVs then
					local _exp_4 = uv1 - uv3
					local _a2_1 = a2
					local uv4 = _exp_4 * _a2_1 + uv3
					local _exp_5 = uv2 - uv3
					local _a3_1 = a3
					local uv5 = _exp_5 * _a3_1 + uv3
					fc1UV[ti0 + 1] = uv4
					fc2UV[ti0 + 1] = uv5
					fc1UV[ti1 + 1] = uv4
					fc2UV[ti1 + 1] = uv1
					fc3UV[ti1 + 1] = uv5
					fc1UV[ti2 + 1] = uv1
					fc2UV[ti2 + 1] = uv2
					fc3UV[ti2 + 1] = uv5
				end
				if hasColors then
					local col4 = col3:Lerp(col1, a2)
					local ca4 = (ca1 - ca3) * a2 + ca3
					local col5 = col3:Lerp(col2, a3)
					local ca5 = (ca2 - ca3) * a3 + ca3
					fc1Col[ti0 + 1] = col4
					fc1CA[ti0 + 1] = ca4
					fc2Col[ti0 + 1] = col5
					fc2CA[ti0 + 1] = ca5
					fc1Col[ti1 + 1] = col4
					fc1CA[ti1 + 1] = ca4
					fc2Col[ti1 + 1] = col1
					fc2CA[ti1 + 1] = ca1
					fc3Col[ti1 + 1] = col5
					fc3CA[ti1 + 1] = ca5
					fc1Col[ti2 + 1] = col1
					fc1CA[ti2 + 1] = ca1
					fc2Col[ti2 + 1] = col2
					fc2CA[ti2 + 1] = ca2
					fc3Col[ti2 + 1] = col5
					fc3CA[ti2 + 1] = ca5
				end
			else
				--a2 only, opposing v2
				--ei2: vi1 to vi4
				--ei4: vi3 to vi4
				--ei5: vi4 to vi2
				--t0: e1, e2, e5 aka 1=fc1, 2=fc2, 3=fc4
				--t1: e5, e4, e3 aka 1=fc4, 2=fc2, 3=fc3
				local ti1 = mesh.trisCount
				mesh.trisCount += 1
				table.insert(edgeStartVIs, vi4)
				table.insert(edgeEndVIs, vi2)
				local _one = Vector3.one
				local _exp = vertices[vi4 + 1]
				local _arg0 = vertices[vi2 + 1]
				table.insert(edgeInvVecs, _one / (_exp - _arg0))
				local ei5 = mesh.edgesCount
				mesh.edgesCount += 1
				local _exp_1 = n1 - n3
				local _a2 = a2
				local n4 = _exp_1 * _a2 + n3
				fc3VI[ti0 + 1] = vi4
				fEI3[ti0 + 1] = ei5
				fc3N[ti0 + 1] = n4
				fc1VI[ti1 + 1] = vi4
				fc2VI[ti1 + 1] = vi2
				fc3VI[ti1 + 1] = vi3
				fEI1[ti1 + 1] = ei5
				fEI2[ti1 + 1] = ei4
				fEI3[ti1 + 1] = ei3
				fc1N[ti1 + 1] = n4
				fc2N[ti1 + 1] = n2
				fc3N[ti1 + 1] = n3
				if hasUVs then
					local _exp_2 = uv1 - uv3
					local _a2_1 = a2
					local uv4 = _exp_2 * _a2_1 + uv3
					fc3UV[ti0 + 1] = uv4
					fc1UV[ti1 + 1] = uv4
					fc2UV[ti1 + 1] = uv2
					fc3UV[ti1 + 1] = uv3
				end
				if hasColors then
					local col4 = col3:Lerp(col1, a2)
					local ca4 = (ca1 - ca3) * a2 + ca3
					fc3Col[ti0 + 1] = col4
					fc3CA[ti0 + 1] = ca4
					fc1Col[ti1 + 1] = col4
					fc1CA[ti1 + 1] = ca4
					fc2Col[ti1 + 1] = col2
					fc2CA[ti1 + 1] = ca2
					fc3Col[ti1 + 1] = col3
					fc3CA[ti1 + 1] = ca3
				end
			end
		elseif a3 ~= 0 and a3 == a3 and a3 then
			local _ei3_1 = ei3
			local vi4 = edgeSplitVIs[_ei3_1]
			local _ei3_2 = ei3
			local ei4 = edgeSplitEIs[_ei3_2]
			if edgeStartVIs[ei3 + 1] ~= vi2 then
				a3 = 1 - a3
				local swap = ei4
				ei4 = ei3
				ei3 = swap
			end
			--a3 only, opposing v1
			--ei3: vi2 to vi4
			--ei4: vi3 to vi4
			--ei5: vi4 to vi1
			--t0: e1, e5, e3 aka 1=fc1, 2=fc2, 3=fc4
			--t1: e5, e2, e4 aka 1=fc1, 2=fc4, 3=fc3
			local ti1 = mesh.trisCount
			mesh.trisCount += 1
			table.insert(edgeStartVIs, vi4)
			table.insert(edgeEndVIs, vi1)
			local _one = Vector3.one
			local _exp = vertices[vi4 + 1]
			local _arg0 = vertices[vi1 + 1]
			table.insert(edgeInvVecs, _one / (_exp - _arg0))
			local ei5 = mesh.edgesCount
			mesh.edgesCount += 1
			local _exp_1 = n2 - n3
			local _a3 = a3
			local n4 = _exp_1 * _a3 + n3
			fc3VI[ti0 + 1] = vi4
			fEI2[ti0 + 1] = ei5
			fc3N[ti0 + 1] = n4
			fc1VI[ti1 + 1] = vi1
			fc2VI[ti1 + 1] = vi4
			fc3VI[ti1 + 1] = vi3
			fEI1[ti1 + 1] = ei5
			fEI2[ti1 + 1] = ei2
			fEI3[ti1 + 1] = ei4
			fc1N[ti1 + 1] = n1
			fc2N[ti1 + 1] = n4
			fc3N[ti1 + 1] = n3
			if hasUVs then
				local _exp_2 = uv2 - uv3
				local _a3_1 = a3
				local uv4 = _exp_2 * _a3_1 + uv3
				fc3UV[ti0 + 1] = uv4
				fc1UV[ti1 + 1] = uv1
				fc2UV[ti1 + 1] = uv4
				fc3UV[ti1 + 1] = uv3
			end
			if hasColors then
				local col4 = col3:Lerp(col2, a3)
				local ca4 = (ca2 - ca3) * a3 + ca3
				fc3Col[ti0 + 1] = col4
				fc3CA[ti0 + 1] = ca4
				fc1Col[ti1 + 1] = col1
				fc1CA[ti1 + 1] = ca1
				fc2Col[ti1 + 1] = col4
				fc2CA[ti1 + 1] = ca4
				fc3Col[ti1 + 1] = col3
				fc3CA[ti1 + 1] = ca3
			end
		end
	end
end
return {
	splitMesh = splitMesh,
}
