uniform sampler2D tex;
uniform float strength;
varying vec2 texcoord;

void main() {
    vec2 centered = (texcoord - 0.5) * 2.0;
    float r2 = dot(centered, centered);
    float scale = 1.0 / (1.0 + strength * 2.0);
    vec2 distorted = centered * (1.0 + strength * r2) * scale;
    vec2 final_uv = distorted * 0.5 + 0.5;
    gl_FragColor = texture2D(tex, final_uv);
}
