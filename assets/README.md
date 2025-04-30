to convert obj to isaac usable usd 
run 
`bash
python convert_mesh.py <file.obj> </Props/desired_out/desired_out.usd> --make-instanceable --collision-approximation convexDecomposition --mass 1.0
`
ie.

`bash
python convert_mesh.py beaker.obj Props/beaker/beaker.usd --make-instanceable --collision-approximation convexDecomposition --mass 1.0
python convert_mesh.py con_flask.obj Props/con_flask/con_flask.usd --make-instanceable --collision-approximation convexDecomposition  --mass 1.0
python convert_mesh.py round_bot.obj Props/round_bot/round_bot.usd --make-instanceable --collision-approximation convexDecomposition  --mass 1.0
`