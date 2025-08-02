void main()
{
	uvInterp = uv;
	#ifdef USE_COLOR
	colorInterp = color;
	#endif
	normalInterp = my_struct[gl_InstanceID].normalMatrix * normal;
	gl_Position = my_struct[gl_InstanceID].modelViewMatrix * vec4(pos, 1.0f);
}