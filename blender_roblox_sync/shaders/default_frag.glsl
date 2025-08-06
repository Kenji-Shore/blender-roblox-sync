float linear_rgb_to_srgb(float color)
{
  if (color < 0.0031308f) {
    return (color < 0.0f) ? 0.0f : color * 12.92f;
  }

  return 1.055f * pow(color, 1.0f / 2.4f) - 0.055f;
}

float3 linear_rgb_to_srgb(float3 color)
{
  return float3(
      linear_rgb_to_srgb(color.r), linear_rgb_to_srgb(color.g), linear_rgb_to_srgb(color.b));
}

float srgb_to_linear_rgb(float color)
{
  if (color < 0.04045f) {
    return (color < 0.0f) ? 0.0f : color * (1.0f / 12.92f);
  }

  return pow((color + 0.055f) * (1.0f / 1.055f), 2.4f);
}

float3 srgb_to_linear_rgb(float3 color)
{
  return float3(
      srgb_to_linear_rgb(color.r), srgb_to_linear_rgb(color.g), srgb_to_linear_rgb(color.b));
}

void main()
{
	float a = max(-dot(normalize(normalInterp), sun_dir), 0.0f);
	fragColor = vec4(world_color + sun_color * a, 1.0f);

	#ifdef USE_TEXTURE
	vec4 texColor = texture(image, uvInterp);
	fragColor *= vec4(srgb_to_linear_rgb(texColor.xyz), texColor.w);
	#endif

	#ifdef USE_COLOR
	fragColor.xyz *= srgb_to_linear_rgb(colorInterp);
	#endif

	fragColor.xyz = linear_rgb_to_srgb(fragColor.xyz);
  gl_FragDepth = gl_FragCoord.z - 0.0001f;
}