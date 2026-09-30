# 3D models and "View on your table"

Every product page has a 3D view. Without a model file the shop builds one from
the product photo (a transparent PNG works best). With a real model, customers
can turn the product all the way round, and on a phone they can place it on
their own table in augmented reality (AR).

## 1. Make the model

Scan the real product with a phone app that exports **glTF / .glb**, for
example Polycam, Luma AI, KIRI Engine or RealityScan.

Tips for a clean scan:

- Put the pastry on a plain, matt surface in soft, even daylight (no hard shadows).
- Walk round it slowly in two or three rings: low, middle and from above.
- Crop away the table in the app and set the real size if the app asks
  (a Brezel is about 15 cm wide), so it appears life-size in AR.
- Export as **GLB**.

## 2. Shrink it for the web

Scans are often 30–150 MB. From the `frontend` folder run:

```bash
npm run optimize-model -- ~/Downloads/brezel-scan.glb brezel.glb
```

This simplifies the mesh, resizes textures to 2048 px (keeping JPEG/PNG) and
compresses the geometry with Draco. A good result is 1–5 MB. The upload limit
is 20 MB.

These formats work in the shop's own 3D viewer and in the phones' AR viewers
(Scene Viewer on Android, Quick Look on iPhone). The Draco decoder is served by
the shop itself (`/draco/`), so no third-party CDN is contacted.

## 3. Upload it

Admin → Products → edit the product → **3D model (.glb)** → save.

The product page then shows the model and a **View on your table** button:

- **Phone:** opens the camera and places the product on a surface.
- **Computer:** shows a QR code; scanning it opens the same page on the phone.

## Checking a model

- Drop the `.glb` on <https://gltf-viewer.donmccurdy.com/> to see it and its size.
- If it looks too big or small in AR, fix the scale in the scanning app and export again.
- If the product sits sideways, rotate it in the app (or in Blender) so it rests
  flat, as it would on a counter.
