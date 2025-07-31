void main()
{
	fragColor = texture(image, uvInterp);
	fragColor.xyz *= mix(vec3(0.53f, 1.0f, 0.56f), mix(vec3(1.0f, 0.85f, 0.5f), vec3(1.0f, 1.0f, 1.0f), 0.8f), clamp(dot(normalInterp, vec3(0.0f, 0.0f, 1.0f)), 0.0f, 1.0f));
}