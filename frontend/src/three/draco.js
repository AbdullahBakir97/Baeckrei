// Where the Draco decoder for compressed 3D models is served from. The files
// are copied from three.js by the `draco-decoder` plugin in vite.config.js,
// so models never depend on a third-party CDN.
export const DRACO_PATH = `${import.meta.env.BASE_URL}draco/`
