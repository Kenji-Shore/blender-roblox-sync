void main()
{
	gl_Position = instance_uniforms[gl_InstanceID].model_view_matrix * vec4(pos, 1.0f);
	color = instance_uniforms[gl_InstanceID].color;
}