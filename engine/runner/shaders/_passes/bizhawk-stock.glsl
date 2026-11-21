// Pass-through second pass; linear input filtering is selected by the preset.
#ifdef VERTEX
in vec2 VertexCoord; in vec2 TexCoord; out vec2 vTexCoord;
void main(){vTexCoord=TexCoord;gl_Position=vec4(VertexCoord*2.0-1.0,0.0,1.0);}
#endif
#ifdef FRAGMENT
uniform sampler2D Texture;in vec2 vTexCoord;out vec4 FragColor;
void main(){FragColor=texture(Texture,vTexCoord);}
#endif
