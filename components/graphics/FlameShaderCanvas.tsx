"use client";

import React, { useRef, useEffect } from "react";

export function FlameShaderCanvas() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Accessibility check: fallback to static warm glow gradient
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const gl = canvas.getContext("webgl");
    if (!gl) {
      return;
    }

    let animationFrameId: number;

    const vertexShaderSource = `
      attribute vec2 position;
      varying vec2 vUv;
      void main() {
        vUv = position * 0.5 + 0.5;
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    const fragmentShaderSource = `
      precision mediump float;
      varying vec2 vUv;
      uniform float uTime;
      uniform vec2 uResolution;

      // Pseudo-random noise function
      float hash(vec2 p) {
        p = fract(p * 0.3183099 + 0.1);
        p *= 17.0;
        return fract(p.x * p.y * (p.x + p.y));
      }

      float noise(vec2 x) {
        vec2 i = floor(x);
        vec2 f = fract(x);
        f = f * f * (3.0 - 2.0 * f);
        return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), f.x),
                   mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
      }

      void main() {
        // 8-bit Pixelation grid
        vec2 pixelGrid = vec2(64.0, 36.0);
        vec2 pixelUv = floor(vUv * pixelGrid) / pixelGrid;

        vec2 uv = pixelUv;
        float y = 1.0 - uv.y;

        // Procedural flame movement
        float n1 = noise(vec2(uv.x * 6.0, uv.y * 3.0 - uTime * 2.5));
        float n2 = noise(vec2(uv.x * 12.0 + uTime * 1.2, uv.y * 6.0 - uTime * 3.5));
        float flame = (n1 * 0.6 + n2 * 0.4) * y * 1.5;

        // Thresholding into 8-bit discrete color bands
        vec3 color = vec3(0.04, 0.04, 0.05); // Base background

        if (flame > 0.75) {
          color = vec3(1.0, 0.95, 0.6); // Hot core yellow/white
        } else if (flame > 0.5) {
          color = vec3(1.0, 0.45, 0.1); // Bright Retro Orange (#FF5722)
        } else if (flame > 0.3) {
          color = vec3(0.85, 0.2, 0.05); // Deep Red/Amber
        } else if (flame > 0.15) {
          color = vec3(0.3, 0.08, 0.05); // Charred embers
        }

        gl_FragColor = vec4(color, 0.88);
      }
    `;

    function compileShader(type: number, source: string) {
      const shader = gl!.createShader(type)!;
      gl!.shaderSource(shader, source);
      gl!.compileShader(shader);
      return shader;
    }

    const vertShader = compileShader(gl.VERTEX_SHADER, vertexShaderSource);
    const fragShader = compileShader(gl.FRAGMENT_SHADER, fragmentShaderSource);

    const program = gl.createProgram()!;
    gl.attachShader(program, vertShader);
    gl.attachShader(program, fragShader);
    gl.linkProgram(program);
    gl.useProgram(program);

    // Quad geometry
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
      gl.STATIC_DRAW
    );

    const positionLocation = gl.getAttribLocation(program, "position");
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    const uTimeLocation = gl.getUniformLocation(program, "uTime");
    const uResolutionLocation = gl.getUniformLocation(program, "uResolution");

    const resize = () => {
      if (!canvas) return;
      canvas.width = canvas.parentElement?.clientWidth || 800;
      canvas.height = canvas.parentElement?.clientHeight || 450;
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(uResolutionLocation, canvas.width, canvas.height);
    };

    resize();
    window.addEventListener("resize", resize);

    const startTime = performance.now();

    const render = (time: number) => {
      const elapsed = (time - startTime) * 0.001;
      gl.uniform1f(uTimeLocation, prefersReducedMotion ? 1.0 : elapsed);
      gl.drawArrays(gl.TRIANGLES, 0, 6);

      if (!prefersReducedMotion) {
        animationFrameId = requestAnimationFrame(render);
      }
    };

    render(startTime);

    return () => {
      window.removeEventListener("resize", resize);
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      gl.deleteProgram(program);
      gl.deleteShader(vertShader);
      gl.deleteShader(fragShader);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none z-0 opacity-80"
      style={{ imageRendering: "pixelated" }}
    />
  );
}
