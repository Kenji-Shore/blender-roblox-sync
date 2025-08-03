void main()
{
	uvInterp = uv;
	#ifdef USE_COLOR
	colorInterp = color;
	#endif
	normalInterp = instance_uniforms[gl_InstanceID].normal_matrix * normal;
	gl_Position = instance_uniforms[gl_InstanceID].model_view_matrix * vec4(pos, 1.0f);
}