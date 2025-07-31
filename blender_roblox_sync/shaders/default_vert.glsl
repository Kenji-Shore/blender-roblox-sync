void main()
{
	uvInterp = uv;
	normalInterp = my_struct[gl_InstanceID].normalMatrix * normal;
	gl_Position = my_struct[gl_InstanceID].modelViewMatrix * vec4(pos, 1.0f);
}