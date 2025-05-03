
./isaaclab.bat -p scripts/tools/convert_mesh.py "C:\Users\Administrator\Downloads\beaker.obj" "C:\Users\Administrator\OneDrive - The University of Liverpool\Playground\Chills\assets\data\Props\Beaker\beaker.usd"  --collision-approximation convexDecomposition --mass 0.05

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