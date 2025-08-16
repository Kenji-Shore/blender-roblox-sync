float4 blender_srgb_to_framebuffer_space(float4 in_color)
{
	float3 c = max(in_color.rgb, float3(0.0f));
	float3 c1 = c * (1.0f / 12.92f);
	float3 c2 = pow((c + 0.055f) * (1.0f / 1.055f), float3(2.4f));
	in_color.rgb = mix(c1, c2, step(float3(0.04045f), c));
	return in_color;
}

void main()
{
	#ifdef OFFSET_DEPTH
	gl_FragDepth = gl_FragCoord.z - 0.00001f;
	#endif
	fragColor = blender_srgb_to_framebuffer_space(color);
}